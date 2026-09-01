import os
from pathlib import Path

from pyspark.sql import DataFrame, functions as F
from spark.config import (
    RAW_DIR,
    PROCESSED_DIR,
    YELLOW_TAXI_PATTERN,
    SELECTED_COLUMNS,
    SPARK_LOG_LEVEL,
)
from spark.etl.extract import get_spark_session, extract_data
from spark.etl.metadata import ETLMetadata
from spark.etl.validate import validate_schema, is_empty_dataframe
from spark.etl.transform import handle_null_values, remove_duplicates, standardize_data_types, add_pickup_date
from spark.etl.load import load_data
from spark.utils.logger import get_logger


class YellowTaxiETLPipeline:

    def __init__(self):
        self.logger = get_logger("spark.etl.pipeline")
        self.spark = None
        self.metadata = ETLMetadata()

        # pickup_date và source_month được thêm bởi pipeline, không có trong raw file
        derived_cols = ["pickup_date", "source_month"]
        self.required_cols = [col for col in SELECTED_COLUMNS if col not in derived_cols]

    def initialize_spark(self) -> None:
        self.logger.info("Khởi tạo Spark Session...")
        self.spark = get_spark_session()
        self.spark.sparkContext.setLogLevel(SPARK_LOG_LEVEL)
        self.logger.info("Đã cấu hình log level: %s", SPARK_LOG_LEVEL)

    def extract(self, file_path: Path) -> DataFrame:
        self.logger.info("=== EXTRACT: %s ===", file_path.name)
        return extract_data(self.spark, str(file_path.parent), file_path.name)

    def validate(self, df: DataFrame) -> bool:
        self.logger.info("=== VALIDATE ===")
        if not validate_schema(df, self.required_cols):
            self.logger.error("Kiểm tra schema thất bại!")
            return False
        if is_empty_dataframe(df):
            self.logger.error("DataFrame rỗng!")
            return False
        self.logger.info("Validate thành công!")
        return True

    def transform(self, df: DataFrame) -> DataFrame:
        self.logger.info("=== TRANSFORM (T1: clean & standardize) ===")
        df = standardize_data_types(df)
        df = handle_null_values(df)
        df = remove_duplicates(df)
        df = add_pickup_date(df)
        return df

    def load(self, df: DataFrame, filename: str, input_size_bytes: int) -> None:
        self.logger.info("=== LOAD: Spark → local Parquet ===")
        load_data(
            df,
            str(self.metadata.processed_path(filename)),
            input_size_bytes=input_size_bytes,
        )

    def load_bigquery(self, filename: str) -> None:
        self.logger.info("=== LOAD: local Parquet → BigQuery ===")
        from spark.etl.load_bigquery import BigQueryLoader
        BigQueryLoader().load_batch(
            self.metadata.processed_path(filename),
            self.metadata._record(filename)["source_month"],
        )

    def run(self) -> None:
        self.logger.info("=== Running ETL Pipeline ===")

        # ── 0. Metadata: tìm file mới nhất chưa xử lý ──────────────────────
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
                "Không có file mới để xử lý. "
                "Thêm file Parquet vào %s để chạy lại.", RAW_DIR,
            )
            return

        filename = target_file.name
        self.logger.info(">>> File được chọn: %s", filename)

        try:
            if self.metadata.status(filename) == "processed":
                self.load_bigquery(filename)
                self.metadata.mark_bq_loaded(filename)
                return

            self.metadata.mark_fetched(filename, target_file.stat().st_size)
            self.initialize_spark()

            # ── 1. Extract ────────────────────────────────────────────────
            df_raw = self.extract(target_file)

            # ── 2. Validate ───────────────────────────────────────────────
            if not self.validate(df_raw):
                raise ValueError(f"Validation failed: {filename}")

            # ── 3. Transform ──────────────────────────────────────────────
            df_transformed = self.transform(df_raw)

            test_row_limit = os.getenv("ETL_TEST_ROW_LIMIT")
            if test_row_limit:
                row_limit = int(test_row_limit)
                if row_limit <= 0:
                    raise ValueError("ETL_TEST_ROW_LIMIT phải là số nguyên dương")
                self.logger.info("Test mode: giới hạn %d rows", row_limit)
                df_transformed = df_transformed.limit(row_limit)

            # ── 4. Load → local Parquet ───────────────────────────────────
            df_transformed = df_transformed.withColumn(
                "source_month", F.lit(self.metadata._record(filename)["source_month"])
            )
            self.load(df_transformed, filename, target_file.stat().st_size)
            self.metadata.mark_processed(filename, target_file.stat().st_size)

            # ── 5. Load → BigQuery ────────────────────────────────────────
            try:
                self.load_bigquery(filename)
                self.metadata.mark_bq_loaded(filename)
            except Exception as bq_err:
                self.logger.warning(
                    "BigQuery load thất bại: %s\n"
                    "Data batch vẫn giữ tại processed/. Retry BQ ở lần chạy tiếp theo.",
                    bq_err,
                )
                # Status vẫn là "extracted" → lần sau sẽ retry step BQ

            self.logger.info("=== ETL PIPELINE COMPLETED: %s ===", filename)

        except Exception as e:
            self.metadata.mark_failed(filename, str(e))
            self.logger.error("Pipeline failed [%s]: %s", filename, e, exc_info=True)
            raise
        finally:
            if self.spark is not None:
                self.logger.info("Dừng Spark Session...")
                self.spark.stop()
                self.logger.info("Spark Session đã dừng.")

