import os
import time
from pathlib import Path

from pyspark.sql import DataFrame, functions as F
from spark.config import (
    RAW_DIR,
    YELLOW_TAXI_PATTERN,
    SELECTED_COLUMNS,
    SPARK_LOG_LEVEL,
)
from spark.etl.extract import get_spark_session, extract_data
from spark.etl.metadata import ETLMetadata
from spark.etl.validate import validate_schema, is_empty_dataframe
from spark.etl.transform import (
    add_pickup_date,
    handle_null_values,
    remove_duplicates,
    standardize_data_types,
)
from spark.etl.load import load_data
from spark.utils.logger import get_logger


class YellowTaxiETLPipeline:

    def __init__(self):
        self.logger = get_logger("spark.etl.pipeline")
        self.spark = None
        self.metadata = ETLMetadata()
        self.stage_timings: dict[str, float] = {}

        derived_cols = ["pickup_date", "source_month"]
        self.required_cols = [col for col in SELECTED_COLUMNS if col not in derived_cols]

    def _log_stage_timings(self, total_seconds: float) -> None:
        lines = [
            "",
            "=" * 55,
            "             ETL PIPELINE STAGE TIMINGS             ",
            "=" * 55,
            f"{'Stage':<30} | {'Duration (s)':<15}",
            "-" * 55,
        ]
        for stage, duration in self.stage_timings.items():
            lines.append(f"{stage:<30} | {duration:>10.3f}s")
        lines.extend([
            "-" * 55,
            f"{'Total Pipeline Time':<30} | {total_seconds:>10.3f}s",
            "=" * 55,
        ])
        self.logger.info("\n".join(lines))

    def initialize_spark(self) -> None:
        self.logger.info("Initializing Spark Session...")
        self.spark = get_spark_session()
        self.spark.sparkContext.setLogLevel(SPARK_LOG_LEVEL)
        self.logger.info("Log level configured: %s", SPARK_LOG_LEVEL)

    def extract(self, file_path: Path) -> DataFrame:
        self.logger.info("=== EXTRACT: %s ===", file_path.name)
        return extract_data(self.spark, str(file_path.parent), file_path.name)

    def validate(self, df: DataFrame) -> bool:
        self.logger.info("=== VALIDATE ===")
        if not validate_schema(df, self.required_cols):
            self.logger.error("Schema validation failed!")
            return False
        if is_empty_dataframe(df):
            self.logger.error("DataFrame is empty!")
            return False
        self.logger.info("Validate successful!")
        return True

    def transform(self, df: DataFrame) -> DataFrame:
        self.logger.info("=== TRANSFORM (T1: clean and standardize) ===")
        df = standardize_data_types(df)
        df = handle_null_values(df)
        df = remove_duplicates(df)
        return add_pickup_date(df)

    def load(self, df: DataFrame, filename: str, input_size_bytes: int) -> None:
        self.logger.info("=== LOAD: Spark → local Parquet ===")
        load_data(
            df,
            str(self.metadata.processed_path(filename)),
            input_size_bytes=input_size_bytes,
        )

    def load_bigquery(self, filename: str) -> None:
        self.logger.info("=== LOAD: local Parquet → S3 → Redshift ===")
        from spark.etl.load_redshift import RedshiftLoader
        RedshiftLoader().load_batch(
            self.metadata.processed_path(filename),
            self.metadata._record(filename)["source_month"],
        )

    def run(self) -> None:
        self.logger.info("=== Running ETL Pipeline ===")
        pipeline_start = time.perf_counter()
        self.stage_timings.clear()

        summary = self.metadata.summary()
        self.logger.info(
            "Metadata: %d file tổng, by_status=%s",
            summary["total"], summary["by_status"],
        )

        target_file: Path | None = self.metadata.get_latest_unprocessed(
            raw_dir=RAW_DIR,
            pattern=YELLOW_TAXI_PATTERN,
        )

        if target_file is None:
            self.logger.info(
                "Thêm file Parquet vào %s để chạy lại.", RAW_DIR,
            )
            return

        filename = target_file.name
        self.logger.info(">>> Selected file: %s", filename)

        try:
            if self.metadata.status(filename) == "processed":
                t_bq = time.perf_counter()
                self.load_bigquery(filename)
                self.metadata.mark_bq_loaded(filename)
                self.stage_timings["Load BigQuery"] = time.perf_counter() - t_bq
                self._log_stage_timings(time.perf_counter() - pipeline_start)
                return

            self.metadata.mark_fetched(filename, target_file.stat().st_size)

            # ── 0. Initialize Spark ───────────────────────────────────────
            t0 = time.perf_counter()
            self.initialize_spark()
            self.stage_timings["Spark Init"] = time.perf_counter() - t0

            # ── 1. Extract ────────────────────────────────────────────────
            t0 = time.perf_counter()
            df_raw = self.extract(target_file)
            self.stage_timings["Extract"] = time.perf_counter() - t0

            # ── 2. Validate ───────────────────────────────────────────────
            t0 = time.perf_counter()
            if not self.validate(df_raw):
                raise ValueError(f"Validation failed: {filename}")
            self.stage_timings["Validate"] = time.perf_counter() - t0

            # ── 3. Transform ──────────────────────────────────────────────
            t0 = time.perf_counter()
            df_transformed = self.transform(df_raw)

            test_row_limit = os.getenv("ETL_TEST_ROW_LIMIT")
            if test_row_limit:
                row_limit = int(test_row_limit)
                if row_limit <= 0:
                    raise ValueError("ETL_TEST_ROW_LIMIT phải là số nguyên dương")
                self.logger.info("Test mode: limiting to %d rows", row_limit)
                df_transformed = df_transformed.limit(row_limit)
            self.stage_timings["Transform"] = time.perf_counter() - t0

            # ── 4. Load → local Parquet ───────────────────────────────────
            t0 = time.perf_counter()
            df_transformed = df_transformed.withColumn(
                "source_month", F.lit(self.metadata._record(filename)["source_month"])
            )
            self.load(df_transformed, filename, target_file.stat().st_size)
            self.metadata.mark_processed(filename, target_file.stat().st_size)
            self.stage_timings["Load Local Parquet"] = time.perf_counter() - t0

            # ── 5. Load → BigQuery ────────────────────────────────────────
            t0 = time.perf_counter()
            try:
                self.load_bigquery(filename)
                self.metadata.mark_bq_loaded(filename)
                self.stage_timings["Load BigQuery"] = time.perf_counter() - t0
            except Exception as bq_err:
                self.logger.warning(
                    "BigQuery load failed: %s\n"
                    "Data batch retained in processed/. Will retry BigQuery load on next run.",
                    bq_err,
                )
                self.stage_timings["Load BigQuery (Failed)"] = time.perf_counter() - t0

            total_elapsed = time.perf_counter() - pipeline_start
            self._log_stage_timings(total_elapsed)
            self.logger.info("=== ETL PIPELINE COMPLETED: %s (Total: %.3fs) ===", filename, total_elapsed)

        except Exception as e:
            self.metadata.mark_failed(filename, str(e))
            self.logger.error("Pipeline failed [%s]: %s", filename, e, exc_info=True)
            raise
        finally:
            if self.spark is not None:
                self.logger.info("Stopping Spark Session...")
                self.spark.stop()
                self.logger.info("Spark Session stopped.")

