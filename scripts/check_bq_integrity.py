"""
scripts/check_bq_integrity.py
-------------------------------
Kiem tra su dong bo giua BigQuery va metadata local.

Logic:
  1. Query BQ: SELECT source_month, COUNT(*) FROM yellow_taxi_raw GROUP BY source_month
  2. So sanh voi expected months (DATA_START_DATE den thang truoc hien tai)
  3. Thang thieu hoac rows=0 (lung lo) -> danh dau repair_needed
  4. Fix metadata bat dong bo: BQ co du lieu nhung metadata chua biet -> mark bq_loaded

Report ghi ra: /app/data/metadata/integrity_report.json
  {
    "checked_at": "...",
    "expected_months": [...],
    "bq_months": {"2025-06": 1234567, ...},
    "missing_months": [...],
    "empty_months": [...],
    "repair_needed": [...],
    "ok": true/false
  }

Goi boi: nyc_taxi_integrity_check DAG (schedule ngay 15 moi thang).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from google.cloud import bigquery
from google.oauth2 import service_account
from spark.etl.fetch_taxi_data import DATA_START_DATE
from spark.etl.metadata import ETLMetadata
from spark.utils.logger import get_logger

logger = get_logger(__name__)

GCP_PROJECT_ID  = os.getenv("GCP_PROJECT_ID",  "nyc-taxi-data-pipeline-507015")
GCP_DATASET_RAW = os.getenv("GCP_DATASET_RAW",  "nyc_taxi_raw")
GCP_KEYFILE     = os.getenv("GCP_KEYFILE_PATH", str(ROOT_DIR / "gcp_service_account.json"))
REPORT_PATH     = Path("/app/data/metadata/integrity_report.json")


def _bq_client() -> bigquery.Client:
    creds = service_account.Credentials.from_service_account_file(
        GCP_KEYFILE, scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    return bigquery.Client(project=GCP_PROJECT_ID, credentials=creds)


def _expected_months() -> list[str]:
    """Tra ve tat ca YYYY-MM tu DATA_START_DATE den thang truoc hien tai."""
    start = datetime.strptime(DATA_START_DATE, "%Y-%m")
    now   = datetime.now()
    end   = datetime(now.year, now.month - 1, 1) if now.month > 1 else datetime(now.year - 1, 12, 1)
    months, cur = [], start
    while cur <= end:
        months.append(cur.strftime("%Y-%m"))
        cur = datetime(cur.year + (cur.month // 12), (cur.month % 12) + 1, 1)
    return months


def _query_bq_months(client: bigquery.Client) -> dict[str, int]:
    """Query BQ tra ve {source_month: row_count}. Tra {} neu table chua ton tai."""
    sql = f"""
        SELECT source_month, COUNT(*) AS row_count
        FROM `{GCP_PROJECT_ID}.{GCP_DATASET_RAW}.yellow_taxi_raw`
        GROUP BY source_month ORDER BY source_month
    """
    try:
        return {r["source_month"]: r["row_count"] for r in client.query(sql).result()}
    except Exception as e:
        logger.warning("Khong query duoc BQ (table chua ton tai?): %s", e)
        return {}


def _fix_metadata_from_bq(bq_months: dict[str, int]) -> None:
    """BQ co du lieu nhung metadata chua cap nhat -> tu dong fix sang bq_loaded."""
    metadata, changed = ETLMetadata(), False
    for month, row_count in bq_months.items():
        if row_count == 0:
            continue
        filename = f"yellow_tripdata_{month}.parquet"
        if metadata.status(filename) not in ("bq_loaded", "dbt_tested", "completed"):
            logger.info("[FIX] %s BQ rows=%d nhung status=%s -> set bq_loaded",
                        filename, row_count, metadata.status(filename))
            record = metadata._record(filename)
            record.update({"status": "bq_loaded",
                           "bq_loaded_at": datetime.now().isoformat(timespec="seconds"),
                           "note": "auto-fixed by integrity check"})
            changed = True
    if changed:
        metadata._save()


def main() -> None:
    logger.info("=== BQ INTEGRITY CHECK | project=%s dataset=%s ===", GCP_PROJECT_ID, GCP_DATASET_RAW)
    client          = _bq_client()
    expected_months = _expected_months()
    bq_months       = _query_bq_months(client)

    logger.info("Expected (%d): %s", len(expected_months), expected_months)
    logger.info("BQ has   (%d): %s", len(bq_months), list(bq_months.keys()))

    missing_months = [m for m in expected_months if m not in bq_months]
    empty_months   = [m for m in expected_months if bq_months.get(m, -1) == 0]
    repair_needed  = sorted(set(missing_months + empty_months))

    for m in missing_months: logger.warning("[MISSING] %s khong co trong BQ", m)
    for m in empty_months:   logger.warning("[EMPTY]   %s co rows=0 (lung lo)", m)
    if not repair_needed:    logger.info("[OK] Tat ca %d thang co du lieu day du.", len(expected_months))
    else:                    logger.warning("[ACTION] Can repair %d thang: %s", len(repair_needed), repair_needed)

    _fix_metadata_from_bq(bq_months)

    report = {
        "checked_at":      datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "expected_months": expected_months,
        "bq_months":       bq_months,
        "missing_months":  missing_months,
        "empty_months":    empty_months,
        "repair_needed":   repair_needed,
        "ok":              len(repair_needed) == 0,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Report: %s | ok=%s", REPORT_PATH, report["ok"])


if __name__ == "__main__":
    main()
