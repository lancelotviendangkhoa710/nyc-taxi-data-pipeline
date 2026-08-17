

from __future__ import annotations

import argparse
import csv
import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from spark.config import RAW_DIR, ROOT_DIR, SELECTED_COLUMNS, setup_java_env
from spark.etl.transform import add_derived_columns, filter_outliers, handle_null_values

MEBIBYTE = 1024 * 1024
RESULT_COLUMNS = (
    "run_id",
    "timestamp_utc",
    "input_start_month",
    "input_end_month",
    "requested_data_size_mb",
    "actual_input_size_mb",
    "input_files",
    "cpu_cores",
    "host_logical_cpus",
    "requested_partitions",
    "spark_default_parallelism",
    "input_rows",
    "output_rows",
    "read_seconds",
    "transform_seconds",
    "write_seconds",
    "total_seconds",
    "output_size_mb",
)


def parse_positive_int_list(value: str) -> list[int]:
    """Parse a comma-separated list of positive integers for argparse."""
    try:
        items = [int(item.strip()) for item in value.split(",")]
    except ValueError as error:
        raise argparse.ArgumentTypeError("Expected comma-separated integers") from error
    if not items or any(item <= 0 for item in items):
        raise argparse.ArgumentTypeError("All values must be positive")
    return items


def select_files_for_size(raw_dir: Path, requested_size_mb: int) -> list[Path]:
    """Select chronological source files until their total reaches the requested size."""
    target_bytes = requested_size_mb * MEBIBYTE
    selected: list[Path] = []
    total_bytes = 0
    for path in sorted(raw_dir.glob("yellow_tripdata_*.parquet")):
        if not path.is_file():
            continue
        selected.append(path)
        total_bytes += path.stat().st_size
        if total_bytes >= target_bytes:
            return selected
    if not selected:
        raise FileNotFoundError(f"No Yellow Taxi Parquet files found in {raw_dir}")
    raise ValueError(
        f"Requested {requested_size_mb} MiB, but only {total_bytes / MEBIBYTE:.1f} MiB is available"
    )


def month_from_path(path: Path) -> str:
    """Return YYYY-MM from a TLC file named yellow_tripdata_YYYY-MM.parquet."""
    prefix = "yellow_tripdata_"
    name = path.stem
    if not name.startswith(prefix) or len(name) != len(prefix) + 7:
        raise ValueError(f"Unexpected Yellow Taxi filename: {path.name}")
    return name.removeprefix(prefix)


def select_files_for_time_window(raw_dir: Path, start_month: str, file_count: int) -> list[Path]:
    """Select a consecutive monthly batch starting with ``start_month``.

    The function validates that every requested month is available, preventing a
    benchmark labelled as a time window from silently skipping missing months.
    """
    if file_count <= 0:
        raise ValueError("file_count must be positive")
    available = {
        month_from_path(path): path
        for path in raw_dir.glob("yellow_tripdata_*.parquet")
        if path.is_file()
    }
    selected: list[Path] = []
    year, month = map(int, start_month.split("-"))
    for _ in range(file_count):
        key = f"{year:04d}-{month:02d}"
        if key not in available:
            raise FileNotFoundError(f"Missing raw file for requested month {key} in {raw_dir}")
        selected.append(available[key])
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return selected


def parse_time_windows(value: str) -> list[tuple[str, int]]:
    """Parse ``YYYY-MM:file_count`` groups, e.g. ``2025-01:3,2025-07:6``."""
    windows: list[tuple[str, int]] = []
    for item in value.split(","):
        try:
            start_month, count = item.strip().split(":", maxsplit=1)
            # Validate the month before executing a potentially expensive Spark job.
            datetime.strptime(start_month, "%Y-%m")
            parsed_count = int(count)
        except ValueError as error:
            raise argparse.ArgumentTypeError(
                "Expected comma-separated YYYY-MM:file_count values"
            ) from error
        if parsed_count <= 0:
            raise argparse.ArgumentTypeError("Each file count must be positive")
        windows.append((start_month, parsed_count))
    return windows


def directory_size_bytes(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def create_spark(cpu_cores: int):
    """Create an isolated session so every run gets its requested CPU cap."""
    setup_java_env()
    from pyspark.sql import SparkSession

    return (
        SparkSession.builder.appName("nyc-taxi-etl-benchmark")
        .master(f"local[{cpu_cores}]")
        .config("spark.sql.shuffle.partitions", str(cpu_cores))
        .config("spark.sql.adaptive.enabled", "false")
        .getOrCreate()
    )


def run_case(
    files: Iterable[Path],
    requested_size_mb: int,
    cpu_cores: int,
    partitions: int,
    output_root: Path,
) -> dict[str, object]:
    """Measure read, transform, and Parquet write for one configuration."""
    file_list = list(files)
    start_month = month_from_path(file_list[0])
    end_month = month_from_path(file_list[-1])
    time_label = f"{start_month}_to_{end_month}"
    run_id = f"{time_label}-cpu{cpu_cores}-part{partitions}"
    output_path = output_root / run_id
    if output_path.exists():
        shutil.rmtree(output_path)

    spark = create_spark(cpu_cores)
    spark.sparkContext.setLogLevel("WARN")
    started = time.perf_counter()
    try:
        read_started = time.perf_counter()
        raw = spark.read.parquet(*(str(path) for path in file_list)).cache()
        input_rows = raw.count()
        read_seconds = time.perf_counter() - read_started

        transform_started = time.perf_counter()
        transformed = add_derived_columns(filter_outliers(handle_null_values(raw)))
        transformed = transformed.select(*SELECTED_COLUMNS).repartition(partitions).cache()
        output_rows = transformed.count()
        transform_seconds = time.perf_counter() - transform_started

        write_started = time.perf_counter()
        transformed.write.mode("overwrite").partitionBy("pickup_date").parquet(str(output_path))
        write_seconds = time.perf_counter() - write_started

        return {
            "run_id": run_id,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "input_start_month": start_month,
            "input_end_month": end_month,
            "requested_data_size_mb": requested_size_mb,
            "actual_input_size_mb": round(sum(path.stat().st_size for path in file_list) / MEBIBYTE, 2),
            "input_files": len(file_list),
            "cpu_cores": cpu_cores,
            "host_logical_cpus": os.cpu_count() or 0,
            "requested_partitions": partitions,
            "spark_default_parallelism": spark.sparkContext.defaultParallelism,
            "input_rows": input_rows,
            "output_rows": output_rows,
            "read_seconds": round(read_seconds, 3),
            "transform_seconds": round(transform_seconds, 3),
            "write_seconds": round(write_seconds, 3),
            "total_seconds": round(time.perf_counter() - started, 3),
            "output_size_mb": round(directory_size_bytes(output_path) / MEBIBYTE, 2),
        }
    finally:
        spark.stop()


def append_result(path: Path, result: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=RESULT_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow(result)


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark NYC Taxi Spark ETL locally.")
    parser.add_argument("--cpus", type=parse_positive_int_list, default=[ 2, 4])
    parser.add_argument("--partitions", type=parse_positive_int_list, default=[ 4, 8,14,12,16,32])
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--data-sizes-mb",
        type=parse_positive_int_list,
        help="Create batches by minimum input size (MiB), for example: 64,128,256.",
    )
    selection.add_argument(
        "--time-windows",
        type=parse_time_windows,
        help="Create exact monthly batches: YYYY-MM:file_count, e.g. 2025-01:3,2025-07:6.",
    )
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--results", type=Path, default=ROOT_DIR / "benchmarks" / "results" / "etl_benchmark.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT_DIR / "data" / "benchmark-output")
    args = parser.parse_args()

    if args.time_windows:
        batches = [
            (start_month, count, select_files_for_time_window(args.raw_dir, start_month, count))
            for start_month, count in args.time_windows
        ]
    else:
        sizes_mb = args.data_sizes_mb or [64, 128, 256]
        batches = [("size", size_mb, select_files_for_size(args.raw_dir, size_mb)) for size_mb in sizes_mb]

    for group_start, requested_amount, files in batches:
        # ``requested_data_size_mb`` remains numeric for backward-compatible CSVs.
        # Time-window batches report their actual on-disk input size in that field.
        size_mb = (
            requested_amount
            if group_start == "size"
            else round(sum(path.stat().st_size for path in files) / MEBIBYTE)
        )
        for cpu_cores in args.cpus:
            for partitions in args.partitions:
                print(
                    f"Running {month_from_path(files[0])} to {month_from_path(files[-1])} "
                    f"({len(files)} files), cpu={cpu_cores}, partitions={partitions}"
                )
                result = run_case(files, size_mb, cpu_cores, partitions, args.output_dir)
                append_result(args.results, result)
                print(f"  total={result['total_seconds']}s, rows={result['output_rows']}")


if __name__ == "__main__":
    main()
