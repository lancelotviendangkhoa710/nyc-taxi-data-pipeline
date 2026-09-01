import math
import os
from pathlib import Path

from pyspark.sql import DataFrame

from spark.config import (
    MAX_WRITE_PARTITIONS,
    MIN_WRITE_PARTITIONS,
    PROCESSED_DIR,
    RAW_DIR,
    SELECTED_COLUMNS,
    TARGET_FILE_SIZE_BYTES,
    YELLOW_TAXI_PATTERN,
)
from spark.utils.logger import get_logger

logger = get_logger("spark.etl.load")
MEBIBYTE = 1024 * 1024


def get_raw_batch_size_bytes(raw_dir: Path = RAW_DIR, pattern: str = YELLOW_TAXI_PATTERN) -> int:
    """Return the total on-disk size of the raw files included in this batch."""
    return sum(path.stat().st_size for path in raw_dir.glob(pattern) if path.is_file())


def calculate_write_partitions(
    input_size_bytes: int,
    target_size_bytes: int = TARGET_FILE_SIZE_BYTES,
    min_partitions: int = MIN_WRITE_PARTITIONS,
    max_partitions: int = MAX_WRITE_PARTITIONS,
) -> int:
    """Choose a bounded number of write tasks from the batch's input size."""
    if input_size_bytes < 0:
        raise ValueError("input_size_bytes must not be negative")
    if target_size_bytes <= 0:
        raise ValueError("target_size_bytes must be positive")
    if min_partitions < 1:
        raise ValueError("min_partitions must be at least 1")
    if max_partitions < min_partitions:
        raise ValueError("max_partitions must be greater than or equal to min_partitions")

    estimated_partitions = max(1, math.ceil(input_size_bytes / target_size_bytes))
    return min(max(estimated_partitions, min_partitions), max_partitions)


def get_configured_batch_size_bytes() -> int:
    """Let an orchestrator supply the exact byte count for remote input."""
    configured_size = os.getenv("ETL_INPUT_SIZE_BYTES")
    return int(configured_size) if configured_size is not None else get_raw_batch_size_bytes()


def load_data(
    df: DataFrame,
    output_path: str | None = None,
    partition_col: str = "pickup_date",
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
    write_partitions = calculate_write_partitions(input_size_bytes)
    logger.info(
        "Adaptive output sizing: raw batch=%.2f MiB, target=%.2f MiB, write partitions=%s",
        input_size_bytes / MEBIBYTE,
        TARGET_FILE_SIZE_BYTES / MEBIBYTE,
        write_partitions,
    )

    current_partitions = df_selected.rdd.getNumPartitions()
    if write_partitions < current_partitions:
        # Reducing partitions does not need an additional full shuffle.
        df_for_write = df_selected.coalesce(write_partitions)
        resize_method = "coalesce"
    elif write_partitions > current_partitions:
        # Increasing parallelism requires a shuffle to balance data.
        df_for_write = df_selected.repartition(write_partitions)
        resize_method = "repartition"
    else:
        df_for_write = df_selected
        resize_method = "unchanged"

    logger.info(
        "Physical write plan: current partitions=%s, method=%s, target partitions=%s",
        current_partitions,
        resize_method,
        write_partitions,
    )

    # The resize controls physical write tasks; partitionBy preserves the
    # pickup_date directory layout used by downstream partition pruning.
    try:
        (
            df_for_write
            .write.mode("overwrite")
            .partitionBy(partition_col)
            .parquet(output_path)
        )
        logger.info("Data written successfully to: %s", output_path)
    except Exception as error:
        logger.error("Unable to write Parquet output: %s", error)
        raise
