import json
from pathlib import Path

from spark.etl.metadata import ETLMetadata


def test_get_latest_unprocessed_skips_files_written_to_processed(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    processed_file = raw_dir / "yellow_tripdata_2026-01.parquet"
    pending_file = raw_dir / "yellow_tripdata_2026-02.parquet"
    processed_file.write_bytes(b"processed")
    pending_file.write_bytes(b"pending")

    metadata = ETLMetadata(tmp_path / "metadata" / "etl_metadata.json")
    metadata.mark_processed(processed_file.name, processed_file.stat().st_size)

    # processed = local Parquet đã ghi, pipeline coi là "có thể retry BQ"
    assert metadata.is_completed(processed_file.name) is False
    assert metadata.status(processed_file.name) == "processed"
    # pending_file chưa có status → nên được chọn
    assert metadata.get_latest_unprocessed(raw_dir, "yellow_tripdata_*.parquet") == pending_file


def test_processed_record_persists_and_prevents_reprocessing(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    source_file = raw_dir / "yellow_tripdata_2026-01.parquet"
    source_file.write_bytes(b"processed")
    metadata_path = tmp_path / "metadata" / "etl_metadata.json"

    ETLMetadata(metadata_path).mark_processed(source_file.name, source_file.stat().st_size)
    reloaded_metadata = ETLMetadata(metadata_path)

    assert json.loads(metadata_path.read_text(encoding="utf-8"))[source_file.name]["status"] == "processed"
    # status=processed → pipeline sẽ retry step BQ; get_latest_unprocessed trả về file này
    assert reloaded_metadata.get_latest_unprocessed(raw_dir, "yellow_tripdata_*.parquet") == source_file


def test_cleanup_deletes_only_dbt_verified_batch_and_keeps_manifest(tmp_path: Path, monkeypatch) -> None:
    import spark.etl.metadata as metadata_module

    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    metadata_path = tmp_path / "metadata" / "etl_metadata.json"
    monkeypatch.setattr(metadata_module, "RAW_DIR", raw_dir)
    monkeypatch.setattr(metadata_module, "PROCESSED_DIR", processed_dir)
    filename = "yellow_tripdata_2026-01.parquet"
    raw_dir.mkdir()
    (raw_dir / filename).write_bytes(b"raw")
    batch_dir = processed_dir / "yellow_taxi" / "source_month=2026-01"
    batch_dir.mkdir(parents=True)
    (batch_dir / "part-000.parquet").write_bytes(b"processed")

    metadata = ETLMetadata(metadata_path)
    metadata.mark_processed(filename, 3)
    metadata.mark_bq_loaded(filename)
    metadata.mark_dbt_tested(filename)

    assert metadata.complete_and_cleanup(retention_days=0) == [filename]
    assert not (raw_dir / filename).exists()
    assert not batch_dir.exists()
    assert ETLMetadata(metadata_path).status(filename) == "completed"