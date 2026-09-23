"""
scripts/check_redshift_integrity.py
-------------------------------
Kiem tra su dong bo giua Redshift va metadata local.

Logic:
  1. Query Redshift: SELECT source_month, COUNT(*) FROM yellow_taxi_raw GROUP BY source_month
  2. So sanh voi expected months (DATA_START_DATE den thang truoc hien tai)
  3. Thang thieu hoac rows=0 (lung lo) -> danh dau repair_needed
  4. Fix metadata bat dong bo: Redshift co du lieu nhung metadata chua biet -> mark dwh_loaded

Report ghi ra: /app/data/metadata/integrity_report.json
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import redshift_connector
from spark.etl.fetch_taxi_data import DATA_START_DATE
from spark.etl.metadata import ETLMetadata
from spark.utils.logger import get_logger

logger = get_logger(__name__)

REDSHIFT_HOST = os.getenv("REDSHIFT_HOST", "redshift-cluster-1.xxxx.us-east-1.redshift.amazonaws.com")
REDSHIFT_PORT = int(os.getenv("REDSHIFT_PORT", "5439"))
REDSHIFT_DB = os.getenv("REDSHIFT_DB", "dev")
REDSHIFT_USER = os.getenv("REDSHIFT_USER", "awsuser")
REDSHIFT_PASSWORD = os.getenv("REDSHIFT_PASSWORD", "Password123")

REPORT_PATH = Path("/app/data/metadata/integrity_report.json")


def _redshift_conn() -> redshift_connector.Connection:
    return redshift_connector.connect(
        host=REDSHIFT_HOST,
        port=REDSHIFT_PORT,
        database=REDSHIFT_DB,
        user=REDSHIFT_USER,
        password=REDSHIFT_PASSWORD
    )


def _expected_months() -> list[str]:
    start = datetime.strptime(DATA_START_DATE, "%Y-%m")
    now   = datetime.now()
    end   = datetime(now.year, now.month - 1, 1) if now.month > 1 else datetime(now.year - 1, 12, 1)
    months, cur = [], start
    while cur <= end:
        months.append(cur.strftime("%Y-%m"))
        cur = datetime(cur.year + (cur.month // 12), (cur.month % 12) + 1, 1)
    return months


def _query_redshift_months(conn: redshift_connector.Connection) -> dict[str, int]:
    sql = """
        SELECT source_month, COUNT(*) AS row_count
        FROM yellow_taxi_raw
        GROUP BY source_month ORDER BY source_month
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            results = cursor.fetchall()
            return {r[0]: r[1] for r in results}
    except Exception as e:
        logger.warning("Khong query duoc Redshift (table chua ton tai?): %s", e)
        return {}


def _fix_metadata_from_redshift(redshift_months: dict[str, int]) -> None:
    metadata, changed = ETLMetadata(), False
    for month, row_count in redshift_months.items():
        if row_count == 0:
            continue
        filename = f"yellow_tripdata_{month}.parquet"
        if metadata.status(filename) not in ("bq_loaded", "dwh_loaded", "dbt_tested", "completed"):
            logger.info("[FIX] %s Redshift rows=%d nhung status=%s -> set bq_loaded (alias for dwh)",
                        filename, row_count, metadata.status(filename))
            record = metadata._record(filename)
            # Giu nguyen key 'bq_loaded' hoac mark thong qua logic hien tai (project dang dung mark_bq_loaded alias)
            record.update({"status": "bq_loaded",
                           "bq_loaded_at": datetime.now().isoformat(timespec="seconds"),
                           "note": "auto-fixed by integrity check"})
            changed = True
    if changed:
        metadata._save()


def main() -> None:
    logger.info("=== REDSHIFT INTEGRITY CHECK | db=%s ===", REDSHIFT_DB)
    try:
        conn = _redshift_conn()
    except Exception as e:
        logger.error("Khong the ket noi Redshift: %s", e)
        sys.exit(1)
        
    expected_months = _expected_months()
    redshift_months = _query_redshift_months(conn)
    conn.close()

    logger.info("Expected (%d): %s", len(expected_months), expected_months)
    logger.info("Redshift has (%d): %s", len(redshift_months), list(redshift_months.keys()))

    missing_months = [m for m in expected_months if m not in redshift_months]
    empty_months   = [m for m in expected_months if redshift_months.get(m, -1) == 0]
    repair_needed  = sorted(set(missing_months + empty_months))

    for m in missing_months: logger.warning("[MISSING] %s khong co trong Redshift", m)
    for m in empty_months:   logger.warning("[EMPTY]   %s co rows=0 (lung lo)", m)
    if not repair_needed:    logger.info("[OK] Tat ca %d thang co du lieu day du.", len(expected_months))
    else:                    logger.warning("[ACTION] Can repair %d thang: %s", len(repair_needed), repair_needed)

    _fix_metadata_from_redshift(redshift_months)

    report = {
        "checked_at":      datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "expected_months": expected_months,
        "dwh_months":      redshift_months,
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
