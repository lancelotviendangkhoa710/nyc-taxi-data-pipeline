"""
airflow/dags/learning_operate_etl.py
------------------------------------
Bài 6: vận hành một ETL DAG an toàn trước khi bật Spark ETL thật.

Mục tiêu học:
- schedule, catchup, max_active_runs và retry.
- Preflight check cho raw files và metadata.
- Guardrail: chặn ETL write khi chưa được bật rõ ràng.

DAG này không chạy Spark ETL, không ghi local Parquet, và không gọi BigQuery.
Nó là template vận hành trước khi triển khai task Spark thật.

Author: NYC Taxi Project
Phase: Airflow learning
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException

DAG_ID = "learning_operate_etl"
RAW_DATA_DIR = Path("/opt/airflow/project_data/raw/yellow")
METADATA_FILE = Path("/opt/airflow/project_data/metadata/etl_metadata.json")
START_DATE = datetime(2025, 1, 1)


@dag(
    dag_id=DAG_ID,
    description="Bài 6: schedule, preflight và guardrail cho NYC Taxi ETL.",
    start_date=START_DATE,
    schedule="0 6 1 * *",
    catchup=False,
    max_active_runs=1,
    tags=["learning", "nyc-taxi", "operations", "etl"],
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
)
def learning_operate_etl() -> None:
    """Tạo workflow vận hành an toàn trước bước Spark ETL write."""

    @task
    def log_run_context(**context: object) -> None:
        """In logical date để phân biệt thời điểm schedule và thời điểm chạy thực tế."""
        print(f"DAG run ID: {context['run_id']}")
        print(f"Logical date: {context['logical_date']}")
        print("Schedule: 06:00 UTC, first day of each month")

    @task
    def validate_raw_input() -> int:
        """Fail fast nếu raw input không tồn tại hoặc không có Yellow Taxi Parquet."""
        if not RAW_DATA_DIR.is_dir():
            raise AirflowFailException(f"Raw directory missing: {RAW_DATA_DIR}")

        raw_files = sorted(RAW_DATA_DIR.glob("yellow_tripdata_*.parquet"))
        if not raw_files:
            raise AirflowFailException(f"No raw Parquet files found in: {RAW_DATA_DIR}")

        print(f"Preflight passed: {len(raw_files)} raw Parquet file(s) available")
        print(f"Next candidate by filename: {raw_files[0].name}")
        return len(raw_files)

    @task
    def validate_metadata_file(raw_file_count: int) -> None:
        """Check metadata mount exists; output file count received by XCom."""
        if not METADATA_FILE.is_file():
            raise AirflowFailException(f"Metadata file missing: {METADATA_FILE}")

        print(f"Metadata file found: {METADATA_FILE.name}")
        print(f"Raw file count from XCom: {raw_file_count}")

    @task
    def block_spark_etl_until_enabled() -> None:
        """Stop safely; task Spark ETL thật chỉ được thêm sau cấu hình production rõ ràng."""
        raise AirflowFailException(
            "Spark ETL is intentionally disabled in Lesson 6. "
            "Do not add data/credential write mounts without an explicit production configuration."
        )

    run_context = log_run_context()
    raw_file_count = validate_raw_input()
    metadata_validated = validate_metadata_file(raw_file_count)
    spark_etl_blocked = block_spark_etl_until_enabled()

    run_context >> raw_file_count >> metadata_validated >> spark_etl_blocked


learning_operate_etl()

# Bài tập:
# 1. Trigger learning_operate_etl. Ba task đầu Success, task cuối Failed có chủ đích.
# 2. Giải thích schedule="0 6 1 * *": chạy 06:00 UTC vào ngày 1 mỗi tháng.
# 3. max_active_runs=1 ngăn hai ETL batch chạy đồng thời.
# 4. catchup=False ngăn Airflow tự chạy bù toàn bộ tháng từ START_DATE.
# 5. Xem log validate_raw_input và validate_metadata_file.
# 6. Không xóa guardrail. Task Spark ETL thật cần review riêng vì nó ghi data/BigQuery.
