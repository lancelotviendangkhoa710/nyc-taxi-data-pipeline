"""
scripts/reset_local_data.py
-----------------------------
Xoa thu muc processed/ va reset metadata ve status=fetched.
Chay trong Spark container (docker-spark-etl:latest) de dam bao
dung uid voi files da duoc Spark tao ra -> co quyen xoa.

Duoc goi boi nyc_taxi_full_reload DAG (task: reset_local_data).
"""

import json
import shutil
import sys
from pathlib import Path

# /app/data tuong ung voi d:/NYC_Taxi_Project/data tren host
DATA_DIR      = Path("/app/data")
PROCESSED_DIR = DATA_DIR / "processed"
METADATA_FILE = DATA_DIR / "metadata" / "etl_metadata.json"

STALE_FIELDS = (
    "processed_at", "bq_loaded_at", "dbt_tested_at",
    "cleaned_at", "error", "failed_at",
)


def reset_processed() -> None:
    if PROCESSED_DIR.exists():
        shutil.rmtree(PROCESSED_DIR)
        print(f"[DELETED] {PROCESSED_DIR}")
    else:
        print(f"[SKIP] {PROCESSED_DIR} khong ton tai.")


def reset_metadata() -> None:
    if not METADATA_FILE.exists():
        print(f"[WARN] Metadata file khong ton tai: {METADATA_FILE}")
        return

    records: dict = json.loads(METADATA_FILE.read_text(encoding="utf-8"))
    for record in records.values():
        record["status"] = "fetched"
        for field in STALE_FIELDS:
            record.pop(field, None)

    METADATA_FILE.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[RESET] {len(records)} record(s) -> status=fetched")


def main() -> None:
    print(f"\n{'='*55}")
    print("  LOCAL DATA RESET")
    print(f"  data dir : {DATA_DIR}")
    print(f"{'='*55}\n")

    reset_processed()
    reset_metadata()

    print("\n[OK] Local data reset hoan tat.\n")


if __name__ == "__main__":
    main()
