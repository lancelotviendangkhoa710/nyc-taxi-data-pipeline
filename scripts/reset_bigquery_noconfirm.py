

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from google.cloud import bigquery
from google.oauth2 import service_account

GCP_PROJECT_ID  = os.getenv("GCP_PROJECT_ID",  "nyc-taxi-data-pipeline-507015")
GCP_DATASET_RAW = os.getenv("GCP_DATASET_RAW",  "nyc_taxi_raw")
GCP_KEYFILE     = os.getenv("GCP_KEYFILE_PATH", str(ROOT_DIR / "gcp_service_account.json"))


def reset_bigquery() -> None:
    print(f"\n{'='*60}")
    print(f"  BQ FULL RESET (non-interactive)")
    print(f"  project : {GCP_PROJECT_ID}")
    print(f"  dataset : {GCP_DATASET_RAW}")
    print(f"{'='*60}\n")

    if not os.path.exists(GCP_KEYFILE):
        print(f"[ERROR] Keyfile not found: {GCP_KEYFILE}")
        sys.exit(1)

    credentials = service_account.Credentials.from_service_account_file(
        GCP_KEYFILE,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    client = bigquery.Client(project=GCP_PROJECT_ID, credentials=credentials)
    dataset_ref = f"{GCP_PROJECT_ID}.{GCP_DATASET_RAW}"

    # Kiểm tra dataset tồn tại
    try:
        client.get_dataset(dataset_ref)
    except Exception:
        print(f"[INFO] Dataset {dataset_ref} không tồn tại — bỏ qua bước xóa.")
        return

    tables = list(client.list_tables(dataset_ref))
    if not tables:
        print(f"[INFO] Dataset {GCP_DATASET_RAW} đã rỗng — không có gì để xóa.")
        return

    print(f"[INFO] Tìm thấy {len(tables)} table(s):")
    for tbl in tables:
        print(f"  - {tbl.table_id}")

    print(f"\n[RESET] Đang xóa {len(tables)} table(s)...\n")
    for tbl in tables:
        table_ref = f"{dataset_ref}.{tbl.table_id}"
        client.delete_table(table_ref, not_found_ok=True)
        print(f"  [DELETED] {tbl.table_id}")

    print(f"\n[OK] Đã xóa {len(tables)} table(s) trong {GCP_DATASET_RAW}.")
    print("     Dataset vẫn còn — sẵn sàng load lại.\n")


if __name__ == "__main__":
    reset_bigquery()
