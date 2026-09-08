"""
airflow/dags/learning_docker_operator.py
----------------------------------------
Bài 4: tạo một container task bằng DockerOperator.

Mục tiêu học:
- Airflow task có thể tạo container Docker riêng.
- Log stdout của container xuất hiện trong task log.
- auto_remove="success" chỉ dọn container khi task thành công.

DAG này chỉ chạy alpine:3.20 và echo text. Không chạy Spark, dbt,
BigQuery, hoặc ghi dữ liệu dự án.

Author: NYC Taxi Project
Phase: Airflow learning
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.providers.docker.operators.docker import DockerOperator

DAG_ID = "learning_docker_operator"
START_DATE = datetime(2025, 1, 1)


@dag(
    dag_id=DAG_ID,
    description="Bài 4: tạo container Docker từ một Airflow task.",
    start_date=START_DATE,
    schedule=None,
    catchup=False,
    tags=["learning", "nyc-taxi", "docker"],
    default_args={
        "retries": 1,
        "retry_delay": timedelta(seconds=30),
    },
)
def learning_docker_operator() -> None:
    """Tạo workflow kiểm tra DockerOperator an toàn."""
    run_container = DockerOperator(
        task_id="run_alpine_container",
        image="alpine:3.20",
        command='sh -c "echo Hello from a DockerOperator task; uname -a"',
        docker_url="unix://var/run/docker.sock",
        auto_remove="success",
        mount_tmp_dir=False,
    )

    show_completion = DockerOperator(
        task_id="show_completion",
        image="alpine:3.20",
        command='echo "DockerOperator task completed successfully"',
        docker_url="unix://var/run/docker.sock",
        auto_remove="success",
        mount_tmp_dir=False,
    )

    run_container >> show_completion


learning_docker_operator()

# Bài tập tự làm:

# 5. Không thay image alpine bằng spark-etl ở bài này. Bài 5 mới chạy Spark thật.
