"""
airflow/dags/learning_spark_container.py
----------------------------------------
Bài 5: Airflow tạo Spark container an toàn bằng DockerOperator.

Mục tiêu học:
- Chọn image Spark ETL có sẵn của project.
- Override image entrypoint để không chạy Spark ETL mặc định.
- Đọc log Java/PySpark từ container task.

DAG này KHÔNG gọi spark.etl.main, không mount data, không mount credentials,
và không ghi local Parquet hoặc BigQuery.

Author: NYC Taxi Project
Phase: Airflow learning
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.providers.docker.operators.docker import DockerOperator

DAG_ID = "learning_spark_container"
SPARK_IMAGE = "docker-spark-etl:latest"
START_DATE = datetime(2025, 1, 1)


@dag(
    dag_id=DAG_ID,
    description="Bài 5: kiểm tra Spark image từ một Airflow Docker task.",
    start_date=START_DATE,
    schedule=None,
    catchup=False,
    tags=["learning", "nyc-taxi", "docker", "spark"],
    default_args={
        "retries": 1,
        "retry_delay": timedelta(seconds=30),
    },
)
def learning_spark_container() -> None:
    """Tạo Spark smoke test không chạm vào ETL hoặc BigQuery."""
    check_spark_runtime = DockerOperator(
        task_id="check_spark_runtime",
        image=SPARK_IMAGE,
        entrypoint=["python"],
        command=[
            "-c",
            (
                "import os, pyspark; "
                "print('Spark image started safely'); "
                "print(f'PySpark version: {pyspark.__version__}'); "
                "print(f'JAVA_HOME: {os.environ.get(\"JAVA_HOME\")}')"
            ),
        ],
        docker_url="unix://var/run/docker.sock",
        auto_remove="success",
        mount_tmp_dir=False,
    )

    confirm_no_etl_run = DockerOperator(
        task_id="confirm_no_etl_run",
        image=SPARK_IMAGE,
        entrypoint=["sh", "-c"],
        command=[
            "echo 'Spark ETL was not executed'; "
            "echo 'No data or GCP credential volume was mounted'",
        ],
        docker_url="unix://var/run/docker.sock",
        auto_remove="success",
        mount_tmp_dir=False,
    )

    check_spark_runtime >> confirm_no_etl_run


learning_spark_container()

# Bài tập tự làm:

# 3. Giải thích vì sao entrypoint=["python"] là bắt buộc.
# 4. Không xóa entrypoint override: image mặc định chạy spark/etl/main.py.
# 5. Bài 6 mới thiết kế task ETL thật với data, metadata, credentials, và guardrails.
