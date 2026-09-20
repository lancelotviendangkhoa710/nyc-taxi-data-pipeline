"""
scripts/load_bq_all.py
-----------------------
Load toan bo processed/ len BigQuery 1 lan duy nhat (TRUNCATE + load all).
Dung sau khi tat ca Spark transform jobs da chay xong song song.

Duoc goi boi nyc_taxi_full_reload DAG (task: load_bq_all).
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from spark.etl.load_bigquery import BigQueryLoader
from spark.utils.logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    logger.info("=== BQ LOAD ALL: processed/ -> BigQuery (TRUNCATE + reload) ===")
    BigQueryLoader().load_all()
    logger.info("=== BQ LOAD ALL completed ===")


if __name__ == "__main__":
    main()
