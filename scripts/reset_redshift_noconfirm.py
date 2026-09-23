"""
scripts/reset_redshift_noconfirm.py
-------------------------------
Xoa table yellow_taxi_raw tren Redshift (Khong xac nhan)
"""

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import redshift_connector

REDSHIFT_HOST = os.getenv("REDSHIFT_HOST", "redshift-cluster-1.xxxx.us-east-1.redshift.amazonaws.com")
REDSHIFT_PORT = int(os.getenv("REDSHIFT_PORT", "5439"))
REDSHIFT_DB = os.getenv("REDSHIFT_DB", "dev")
REDSHIFT_USER = os.getenv("REDSHIFT_USER", "awsuser")
REDSHIFT_PASSWORD = os.getenv("REDSHIFT_PASSWORD", "Password123")


def reset_redshift() -> None:
    print(f"\n{'='*60}")
    print(f"  REDSHIFT FULL RESET (non-interactive)")
    print(f"  host : {REDSHIFT_HOST}")
    print(f"  db   : {REDSHIFT_DB}")
    print(f"{'='*60}\n")

    try:
        conn = redshift_connector.connect(
            host=REDSHIFT_HOST,
            port=REDSHIFT_PORT,
            database=REDSHIFT_DB,
            user=REDSHIFT_USER,
            password=REDSHIFT_PASSWORD
        )
    except Exception as e:
        print(f"[ERROR] Khong the ket noi toi Redshift: {e}")
        sys.exit(1)

    try:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS yellow_taxi_raw;")
            conn.commit()
            print("[OK] Da xoa table yellow_taxi_raw tren Redshift.")
            print("     Table se tu dong duoc tao lai khi chay load.")
    except Exception as e:
        print(f"[ERROR] Loi khi xoa table: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    reset_redshift()
