from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from pyspark.sql import DataFrame, SparkSession
import pyspark.sql.functions as F
import pyspark.sql.types as T

from google.cloud import bigquery
from google.oauth2 import service_account

from spark.config import (
    GCP_DATASET_RAW,
    GCP_KEYFILE_PATH,
    GCP_PROJECT_ID,
    RAW_DIR,
    YELLOW_TAXI_PATTERN,
)
from spark.etl.extract import extract_data, get_spark_session
from spark.utils.logger import get_logger

logger = get_logger("spark.etl.data_profiling")


def get_numeric_columns(df: DataFrame) -> list[str]:
    """Get a list of columns with numeric data types."""
    numeric_types = (
        T.ByteType,
        T.ShortType,
        T.IntegerType,
        T.LongType,
        T.FloatType,
        T.DoubleType,
        T.DecimalType,
    )
    return [
        field.name
        for field in df.schema.fields
        if isinstance(field.dataType, numeric_types)
    ]


def profile_numeric_columns(df: DataFrame) -> DataFrame:
    numeric_cols = get_numeric_columns(df)
    if not numeric_cols:
        logger.warning("Can't find any numeric columns in the DataFrame.")
        spark = df.sparkSession
        schema = T.StructType([
            T.StructField("column_name", T.StringType(), True),
            T.StructField("min_value", T.DoubleType(), True),
            T.StructField("max_value", T.DoubleType(), True),
            T.StructField("mean_value", T.DoubleType(), True),
            T.StructField("median_value", T.DoubleType(), True),
            T.StructField("mode_value", T.DoubleType(), True),
            T.StructField("null_count", T.LongType(), True),
            T.StructField("total_count", T.LongType(), True),
            T.StructField("profiled_at", T.StringType(), True),
        ])
        return spark.createDataFrame([], schema)

    logger.info("Starting data profiling for %d numeric columns: %s", len(numeric_cols), numeric_cols)

    agg_exprs = []
    for col in numeric_cols:
        col_ref = F.col(col)
        agg_exprs.extend([
            F.min(col_ref).cast("double").alias(f"{col}__min"),
            F.max(col_ref).cast("double").alias(f"{col}__max"),
            F.avg(col_ref).cast("double").alias(f"{col}__mean"),
            F.percentile_approx(col_ref.cast("double"), 0.5).alias(f"{col}__median"),
            F.mode(col_ref).cast("double").alias(f"{col}__mode"),
            F.count(col_ref).alias(f"{col}__count"),
            F.count(F.when(col_ref.isNull(), 1)).alias(f"{col}__null_count"),
        ])

    total_rows = df.count()
    summary_row = df.agg(*agg_exprs).collect()[0]
    now_str = datetime.now().isoformat()

    profiling_data = []
    for col in numeric_cols:
        profiling_data.append({
            "column_name": col,
            "min_value": summary_row[f"{col}__min"],
            "max_value": summary_row[f"{col}__max"],
            "mean_value": summary_row[f"{col}__mean"],
            "median_value": summary_row[f"{col}__median"],
            "mode_value": summary_row[f"{col}__mode"],
            "null_count": summary_row[f"{col}__null_count"],
            "total_count": total_rows,
            "profiled_at": now_str,
        })

    spark = df.sparkSession
    result_df = spark.createDataFrame(profiling_data)
    logger.info("Completed data profiling for numeric columns.")
    return result_df


def save_profiling_to_bigquery(
    profiling_df: DataFrame | pd.DataFrame,
    table_name: str = "data_profiling",
) -> None:
    """Save the profiling results to BigQuery."""
    if isinstance(profiling_df, DataFrame):
        pdf = profiling_df.toPandas()
    else:
        pdf = profiling_df

    if pdf.empty:
        logger.warning("Profiling table is empty, skipping BigQuery save.")
        return

    keyfile = GCP_KEYFILE_PATH
    if not os.path.exists(keyfile):
        raise FileNotFoundError(f"Cannot find service account keyfile at: {keyfile}")

    credentials = service_account.Credentials.from_service_account_file(
        keyfile,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    client = bigquery.Client(project=GCP_PROJECT_ID, credentials=credentials)

    dataset_ref = bigquery.Dataset(f"{GCP_PROJECT_ID}.{GCP_DATASET_RAW}")
    dataset_ref.location = "US"
    client.create_dataset(dataset_ref, exists_ok=True)

    table_ref = f"{GCP_PROJECT_ID}.{GCP_DATASET_RAW}.{table_name}"
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=True,
    )

    logger.info("Uploading profiling table (%d rows) to BigQuery: %s ...", len(pdf), table_ref)
    job = client.load_table_from_dataframe(pdf, table_ref, job_config=job_config)
    job.result()
    logger.info("Successfully saved profiling data to BigQuery table: %s", table_ref)


def run_profiling(
    spark: SparkSession | None = None,
    raw_dir_path: str | Path | None = None,
    file_pattern: str = YELLOW_TAXI_PATTERN,
    table_name: str = "data_profiling",
    save_to_bq: bool = True,
) -> DataFrame:

    if spark is None:
        spark = get_spark_session()

    if raw_dir_path is None:
        raw_dir_path = RAW_DIR

    df = extract_data(spark, str(raw_dir_path), file_pattern)
    profiling_df = profile_numeric_columns(df)

    if save_to_bq:
        try:
            save_profiling_to_bigquery(profiling_df, table_name=table_name)
        except Exception as e:
            logger.error("Error occurred while saving profiling results to BigQuery: %s", e)
            raise e

    return profiling_df


if __name__ == "__main__":
    spark_sess = get_spark_session()
    try:
        res = run_profiling(spark=spark_sess, save_to_bq=False)
        res.show(truncate=False)
    finally:
        spark_sess.stop()

