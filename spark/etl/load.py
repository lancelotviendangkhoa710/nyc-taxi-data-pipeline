import math
import os
from pathlib import Path

from pyspark.sql import DataFrame

from spark.config import (
    PROCESSED_DIR,
    RAW_DIR,
    SELECTED_COLUMNS,
    YELLOW_TAXI_PATTERN,
)
from spark.utils.logger import get_logger

logger = get_logger("spark.etl.load")
MEBIBYTE = 1024 * 1024


def get_raw_batch_size_bytes(raw_dir: Path = RAW_DIR, pattern: str = YELLOW_TAXI_PATTERN) -> int:
    """Return the total on-disk size of the raw files included in this batch."""
    return sum(path.stat().st_size for path in raw_dir.glob(pattern) if path.is_file())


def get_configured_batch_size_bytes() -> int:
    """Let an orchestrator supply the exact byte count for remote input."""
    configured_size = os.getenv("ETL_INPUT_SIZE_BYTES")
    return int(configured_size) if configured_size is not None else get_raw_batch_size_bytes()


def load_data(
    df: DataFrame,
    output_path: str | None = None,
    input_size_bytes: int | None = None,
) -> None:
    """Write processed data to a single Parquet file per source_month batch.

    Dùng coalesce(1) thay vì partitionBy(pickup_date) để tối ưu BQ upload:
    - partitionBy tạo N files (1 per ngày) → N BQ load jobs → chậm
    - coalesce(1) tạo 1 file per batch → 1 BQ load job → nhanh hơn ~30x
    pickup_date vẫn là cột trong data, chỉ không dùng để partition file nữa.
    """
    if output_path is None:
        output_path = str(PROCESSED_DIR / "yellow_taxi")

    logger.info("Preparing to write data to: %s", output_path)
    try:
        df_selected = df.select(*SELECTED_COLUMNS)
    except Exception as error:
        logger.error("Unable to select configured columns: %s", error)
        raise

    input_size_bytes = input_size_bytes if input_size_bytes is not None else get_configured_batch_size_bytes()
    logger.info(
        "Coalescing to 1 file — raw batch=%.2f MiB → single Parquet for fast BQ upload",
        input_size_bytes / MEBIBYTE,
    )

    try:
        (
            df_selected
            .coalesce(1)
            .write.mode("overwrite")
            .parquet(output_path)
        )
        logger.info("Data written successfully to: %s", output_path)
    except Exception as error:
        logger.error("Unable to write Parquet output: %s", error)
        raise

