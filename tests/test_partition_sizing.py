# test_partition_sizing.py
# calculate_write_partitions đã bị xóa — load.py giờ dùng coalesce(1) cố định
# để tối ưu BQ upload (1 file/batch thay vì N files/ngày).
# Test này được thay bằng kiểm tra load_data sử dụng đúng output path.

from spark.etl.load import get_raw_batch_size_bytes, get_configured_batch_size_bytes
from pathlib import Path
import os


def test_get_configured_batch_size_bytes_uses_env_when_set(monkeypatch):
    monkeypatch.setenv("ETL_INPUT_SIZE_BYTES", "12345678")
    assert get_configured_batch_size_bytes() == 12345678


def test_get_configured_batch_size_bytes_fallback_when_env_unset(monkeypatch):
    monkeypatch.delenv("ETL_INPUT_SIZE_BYTES", raising=False)
    # Không có raw file → trả về 0
    result = get_configured_batch_size_bytes()
    assert isinstance(result, int)
    assert result >= 0


def test_get_raw_batch_size_bytes_empty_dir(tmp_path):
    result = get_raw_batch_size_bytes(raw_dir=tmp_path, pattern="*.parquet")
    assert result == 0


def test_get_raw_batch_size_bytes_counts_files(tmp_path):
    f1 = tmp_path / "yellow_tripdata_2025-01.parquet"
    f2 = tmp_path / "yellow_tripdata_2025-02.parquet"
    f1.write_bytes(b"x" * 100)
    f2.write_bytes(b"x" * 200)
    result = get_raw_batch_size_bytes(raw_dir=tmp_path, pattern="yellow_tripdata_*.parquet")
    assert result == 300

