"""Persistent batch manifest. Raw and processed files are disposable staging data."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from spark.config import METADATA_DIR, PROCESSED_DIR, RAW_DIR
from spark.utils.logger import get_logger

logger = get_logger("spark.etl.metadata")
METADATA_FILE = METADATA_DIR / "etl_metadata.json"
COMPLETED_STATUSES = {"completed", "dbt_tested"}


def source_month_from_filename(filename: str) -> str:
    """Extract YYYY-MM from yellow_tripdata_YYYY-MM.parquet."""
    prefix = "yellow_tripdata_"
    if not filename.startswith(prefix) or not filename.endswith(".parquet"):
        raise ValueError(f"Tên source không hợp lệ: {filename}")
    source_month = filename.removeprefix(prefix).removesuffix(".parquet")
    datetime.strptime(source_month, "%Y-%m")
    return source_month


class ETLMetadata:
    def __init__(self, metadata_path: Path = METADATA_FILE):
        self.path = metadata_path
        self._records: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            self._records = json.loads(self.path.read_text(encoding="utf-8"))
            for filename, record in self._records.items():
                record.setdefault("filename", filename)
                record.setdefault("source_month", source_month_from_filename(filename))
                if record.get("status") == "extracted":
                    record["status"] = "processed"
        except (json.JSONDecodeError, OSError, ValueError) as error:
            logger.warning("Không đọc được metadata %s: %s", self.path, error)
            self._records = {}

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(".json.tmp")
        temporary_path.write_text(json.dumps(self._records, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary_path.replace(self.path)

    def _record(self, filename: str) -> dict:
        return self._records.setdefault(filename, {"filename": filename, "source_month": source_month_from_filename(filename), "attempts": 0})

    def status(self, filename: str) -> Optional[str]:
        record = self._records.get(filename)
        return record.get("status") if record else None

    def is_completed(self, filename: str) -> bool:
        return self.status(filename) in COMPLETED_STATUSES

    def mark_fetched(self, filename: str, file_size: int) -> None:
        record = self._record(filename)
        record.update({"file_size": file_size, "status": "fetched", "fetched_at": datetime.now().isoformat(timespec="seconds")})
        self._save()

    def mark_processed(self, filename: str, file_size: int) -> None:
        record = self._record(filename)
        record.update({"file_size": file_size, "status": "processed", "processed_at": datetime.now().isoformat(timespec="seconds")})
        self._save()

    def mark_bq_loaded(self, filename: str) -> None:
        record = self._record(filename)
        record.update({"status": "bq_loaded", "bq_loaded_at": datetime.now().isoformat(timespec="seconds")})
        self._save()

    def mark_dbt_tested(self, filename: str) -> None:
        record = self._record(filename)
        if record.get("status") != "bq_loaded":
            raise ValueError(f"Không thể xác nhận dbt cho {filename}: status={record.get('status')}")
        record.update({"status": "dbt_tested", "dbt_tested_at": datetime.now().isoformat(timespec="seconds")})
        self._save()

    def mark_completed(self, filename: str) -> None:
        record = self._record(filename)
        record.update({"status": "completed", "cleaned_at": datetime.now().isoformat(timespec="seconds")})
        self._save()

    def mark_failed(self, filename: str, reason: str) -> None:
        record = self._record(filename)
        record.update({"status": "failed", "error": reason, "failed_at": datetime.now().isoformat(timespec="seconds"), "attempts": record.get("attempts", 0) + 1})
        self._save()

    def get_latest_unprocessed(self, raw_dir: Path, pattern: str) -> Optional[Path]:
        for file_path in sorted(raw_dir.glob(pattern), key=lambda path: path.name):
            if not self.is_completed(file_path.name) and self.status(file_path.name) != "bq_loaded":
                return file_path
        return None

    def processed_path(self, filename: str) -> Path:
        return PROCESSED_DIR / "yellow_taxi" / f"source_month={source_month_from_filename(filename)}"

    def complete_and_cleanup(self, retention_days: int) -> list[str]:
        """Delete only dbt-verified batches older than retention; retain manifest."""
        if retention_days < 0:
            raise ValueError("retention_days không được âm")
        cutoff = datetime.now() - timedelta(days=retention_days)
        cleaned = []
        for filename, record in list(self._records.items()):
            if record.get("status") != "dbt_tested" or datetime.fromisoformat(record["dbt_tested_at"]) > cutoff:
                continue
            raw_path = RAW_DIR / filename
            processed_path = self.processed_path(filename)
            if raw_path.exists():
                raw_path.unlink()
            if processed_path.exists():
                shutil.rmtree(processed_path)
            self.mark_completed(filename)
            cleaned.append(filename)
        return cleaned

    def summary(self) -> dict:
        statuses: dict[str, int] = {}
        for record in self._records.values():
            status = record.get("status", "unknown")
            statuses[status] = statuses.get(status, 0) + 1
        return {"total": len(self._records), "by_status": statuses}