import math
import os
from pathlib import Path

from pyspark.sql import DataFrame

from spark.config import (
    PROCESSED_DIR,
    RAW_DIR,
    SELECTED_COLUMNS,
    YELLOW_TAXI_PATTERN,
    TARGET_FILE_SIZE_BYTES,
    MIN_WRITE_PARTITIONS,
    MAX_WRITE_PARTITIONS,
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
   
    if output_path is None:
        output_path = str(PROCESSED_DIR / "yellow_taxi")

    logger.info("Preparing to write data to: %s", output_path)
    try:
        df_selected = df.select(*SELECTED_COLUMNS)
    except Exception as error:
        logger.error("Unable to select configured columns: %s", error)
        raise

    input_size_bytes = input_size_bytes if input_size_bytes is not None else get_configured_batch_size_bytes()

    num_partitions = max(
        MIN_WRITE_PARTITIONS,
        min(
            MAX_WRITE_PARTITIONS,
            math.ceil(input_size_bytes / TARGET_FILE_SIZE_BYTES) if input_size_bytes > 0 else 1,
        ),
    )

    logger.info(
        "Dynamic partitioning: raw batch=%.2f MiB -> target partitions=%d (target_size=%.2f MiB)",
        input_size_bytes / MEBIBYTE,
        num_partitions,
        TARGET_FILE_SIZE_BYTES / MEBIBYTE,
    )

    try:
        if num_partitions == 1:
            df_writer = df_selected.coalesce(1)
        else:
            df_writer = df_selected.repartition(num_partitions)

        (
            df_writer
            .write.mode("overwrite")
            .parquet(output_path)
        )
        logger.info("Data written successfully to: %s", output_path)
    except Exception as error:
        logger.error("Unable to write Parquet output: %s", error)
        raise


