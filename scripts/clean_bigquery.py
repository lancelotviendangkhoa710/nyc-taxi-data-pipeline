"""
clean_bigquery.py
-----------------
Xóa toàn bộ tables trong dataset nyc_taxi_raw trên BigQuery.
Chạy script này trước khi re-load data với ETLT architecture mới.

Usage:
    python scripts/clean_bigquery.py
"""

import os
import sys
from pathlib import Path

# Thêm project root vào path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from spark.config import GCP_PROJECT_ID, GCP_DATASET_RAW, GCP_KEYFILE_PATH
from google.cloud import bigquery
from google.oauth2 import service_account

def clean_bigquery_dataset():
    print(f"\n{'='*60}")
    print(f"  BQ CLEANUP — project: {GCP_PROJECT_ID}")
    print(f"  dataset : {GCP_DATASET_RAW}")
    print(f"{'='*60}\n")

    # Auth
    if not os.path.exists(GCP_KEYFILE_PATH):
        print(f"[ERROR] Keyfile không tìm thấy: {GCP_KEYFILE_PATH}")
        sys.exit(1)

    credentials = service_account.Credentials.from_service_account_file(
        GCP_KEYFILE_PATH,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    client = bigquery.Client(project=GCP_PROJECT_ID, credentials=credentials)
    dataset_ref = f"{GCP_PROJECT_ID}.{GCP_DATASET_RAW}"

    # Kiểm tra dataset tồn tại không
    try:
        client.get_dataset(dataset_ref)
    except Exception:
        print(f"[INFO] Dataset {dataset_ref} không tồn tại — không cần xóa.")
        return

    # List tất cả tables
    tables = list(client.list_tables(dataset_ref))
    if not tables:
        print(f"[INFO] Dataset {GCP_DATASET_RAW} đang trống — không có gì để xóa.")
        return

    print(f"[INFO] Tìm thấy {len(tables)} table(s):\n")
    for tbl in tables:
        print(f"  - {tbl.table_id}")

    print(f"\n[WARN] Sẽ xóa TẤT CẢ {len(tables)} table(s) trong dataset {GCP_DATASET_RAW}.")
    confirm = input("  Nhập 'yes' để xác nhận: ").strip().lower()
    if confirm != "yes":
        print("[ABORT] Hủy bỏ — không có gì bị xóa.")
        return

    # Xóa từng table
    print()
    for tbl in tables:
        table_ref = f"{dataset_ref}.{tbl.table_id}"
        client.delete_table(table_ref, not_found_ok=True)
        print(f"  [DELETED] {tbl.table_id}")

    print(f"\n[OK] Đã xóa {len(tables)} table(s) trong {GCP_DATASET_RAW}.")
    print("     Dataset vẫn còn tồn tại — sẵn sàng để load lại.\n")


if __name__ == "__main__":
    clean_bigquery_dataset()
