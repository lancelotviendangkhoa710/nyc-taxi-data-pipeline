"""
airflow/dags/learning_hello_airflow.py
-------------------------------------
Bài 1: DAG Airflow cơ bản với TaskFlow API.

Mục tiêu học:
- DAG là workflow gồm nhiều task.
- @task biến Python function thành Airflow task.
- >> định nghĩa thứ tự chạy task.
- Mỗi task có log riêng trong Airflow UI.

DAG này chỉ in log an toàn, không chạy Spark, dbt, Docker, hoặc BigQuery.

Author: NYC Taxi Project
Phase: Airflow learning
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator

LESSON_1_DAG_ID = "learning_hello_airflow"
LESSON_2_DAG_ID = "learning_bash_operator"
LESSON_3_DAG_ID = "learning_check_raw_data"
PROJECT_DATA_DIR = Path("/opt/airflow/project_data")
RAW_DATA_DIR = PROJECT_DATA_DIR / "raw" / "yellow"
START_DATE = datetime(2025, 1, 1)


@dag(
    dag_id=LESSON_1_DAG_ID,
    description="Bài 1: hiểu DAG, task và dependencies trong Airflow.",
    start_date=START_DATE,
    schedule=None,
    catchup=False,
    tags=["learning", "nyc-taxi"],
    default_args={
        "retries": 2,
        "retry_delay": timedelta(seconds=30),
    },
)
def learning_hello_airflow() -> None:
    """Tạo workflow ba task chạy thủ công từ Airflow UI."""

    @task
    def start() -> str:
        """Đánh dấu bắt đầu workflow và trả metadata nhỏ qua XCom."""
        message = "Airflow lesson started"
        print(message)
        return message

    @task
    def show_current_time() -> None:
        """Ghi thời gian chạy task để xem trong Airflow task logs."""
        print(f"Current UTC time: {datetime.utcnow().isoformat()}")

    @task
    def say_your_name() -> None:
        """Bài tập: in tên người học trong task độc lập."""
        print("My name is Khoa")


    @task
    def finish() -> None:
        """Đánh dấu workflow đã hoàn tất."""
        print("Airflow lesson finished successfully")

    start_task = start()
    time_task = show_current_time()
    name_task = say_your_name()
    finish_task = finish()

    start_task >> time_task >> name_task >> finish_task


learning_hello_airflow()


@dag(
    dag_id=LESSON_2_DAG_ID,
    description="Bài 2: chạy shell commands bằng BashOperator.",
    start_date=START_DATE,
    schedule=None,
    catchup=False,
    tags=["learning", "nyc-taxi", "bash"],
    default_args={
        "retries": 1,
        "retry_delay": timedelta(seconds=30),
    },
)
def learning_bash_operator() -> None:
    """Tạo workflow shell an toàn để học BashOperator và task logs."""
    show_airflow_context = BashOperator(
        task_id="show_airflow_context",
        bash_command="""
            echo "Running BashOperator inside Airflow"
            echo "Task ID: $AIRFLOW_CTX_TASK_ID"
            echo "DAG ID: $AIRFLOW_CTX_DAG_ID"
            echo "Logical date: $AIRFLOW_CTX_LOGICAL_DATE"
        """,
    )
    say_hello = BashOperator(
        task_id="say_hello",
        bash_command='echo "Hello from BashOperator"',
    )

    show_working_directory = BashOperator(
        task_id="show_working_directory",
        bash_command="""
            echo "Current directory: $(pwd)"
            echo "DAG files:"
            ls -la /opt/airflow/dags
        """,
    )

    finish_lesson = BashOperator(
        task_id="finish_lesson",
        bash_command='echo "Airflow lesson finished successfully"',
    )

    show_airflow_context >>say_hello>> show_working_directory >> finish_lesson


learning_bash_operator()


@dag(
    dag_id=LESSON_3_DAG_ID,
    description="Bài 3: kiểm tra input Parquet trước khi chạy ETL.",
    start_date=START_DATE,
    schedule=None,
    catchup=False,
    tags=["learning", "nyc-taxi", "python", "data-quality"],
)
def learning_check_raw_data() -> None:
    """Kiểm tra raw data bằng Python task, không chạy Spark hay BigQuery."""

    @task
    def find_raw_parquet_files() -> list[str]:
        """Tìm Yellow Taxi Parquet files từ volume read-only được mount vào Airflow."""
        if not RAW_DATA_DIR.exists():
            raise FileNotFoundError(f"Raw directory not found: {RAW_DATA_DIR}")

        parquet_files = sorted(RAW_DATA_DIR.glob("yellow_tripdata_*.parquet"))
        if not parquet_files:
            raise FileNotFoundError(f"No Yellow Taxi Parquet files found in: {RAW_DATA_DIR}")

        file_names = [file_path.name for file_path in parquet_files]
        print(f"Found {len(file_names)} raw Parquet file(s)")
        print(f"First file: {file_names[0]}")
        return file_names

    @task
    def report_raw_data(file_names: list[str]) -> None:
        """Log small metadata received through XCom; never send file contents through XCom."""
        print(f"Raw file count from XCom: {len(file_names)}")
        print(f"Last file: {file_names[-1]}")

    raw_file_names = find_raw_parquet_files()
    report_raw_data(raw_file_names)


learning_check_raw_data()


#
# Bài 2:
# 1. Trigger DAG learning_bash_operator từ Airflow UI.
# 2. Mở log show_airflow_context, tìm task ID, DAG ID, logical date.
# 3. Mở log show_working_directory, quan sát thư mục /opt/airflow/dags.
# 4. Đổi finish_lesson thành: bash_command="exit 1".
# 5. Trigger lại. Task này retry một lần rồi Failed. Đổi về echo để DAG pass.
# 6. Thêm task BashOperator say_hello giữa hai task đầu:
#    bash_command='echo "Hello from BashOperator"'
