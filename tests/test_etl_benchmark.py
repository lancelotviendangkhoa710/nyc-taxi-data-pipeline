from pathlib import Path

import pytest

from spark.benchmark.etl_benchmark import (
    parse_positive_int_list,
    parse_time_windows,
    select_files_for_size,
    select_files_for_time_window,
)


def test_parse_positive_int_list():
    assert parse_positive_int_list("1, 2,8") == [1, 2, 8]
    with pytest.raises(Exception):
        parse_positive_int_list("1,0")


def test_select_files_reaches_requested_size(tmp_path: Path):
    first = tmp_path / "yellow_tripdata_2025-01.parquet"
    second = tmp_path / "yellow_tripdata_2025-02.parquet"
    first.write_bytes(b"a" * 700_000)
    second.write_bytes(b"b" * 700_000)

    selected = select_files_for_size(tmp_path, 1)

    assert selected == [first, second]


def test_select_files_for_time_window_requires_consecutive_months(tmp_path: Path):
    january = tmp_path / "yellow_tripdata_2025-01.parquet"
    february = tmp_path / "yellow_tripdata_2025-02.parquet"
    january.write_bytes(b"a")
    february.write_bytes(b"b")

    assert select_files_for_time_window(tmp_path, "2025-01", 2) == [january, february]
    with pytest.raises(FileNotFoundError):
        select_files_for_time_window(tmp_path, "2025-01", 3)


def test_parse_time_windows():
    assert parse_time_windows("2025-01:3,2025-07:6") == [("2025-01", 3), ("2025-07", 6)]
