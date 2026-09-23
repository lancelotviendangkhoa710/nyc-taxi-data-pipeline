

from __future__ import annotations

import os
import smtplib
import textwrap
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path, PureWindowsPath

from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

DAG_ID = "nyc_taxi_etl_pipeline"
SPARK_IMAGE = "docker-spark-etl:latest"
DBT_IMAGE = "docker-dbt:latest"
CONTAINER_PROJECT_DIR = "/app"
CONTAINER_KEYFILE = f"{CONTAINER_PROJECT_DIR}/gcp_service_account.json"
AIRFLOW_DATA_DIR = Path("/opt/airflow/project_data")
START_DATE = datetime(2025, 1, 1)
PROJECT_ROOT = os.getenv("NYC_TAXI_PROJECT_ROOT", "")
ETL_ENABLED = os.getenv("ENABLE_NYC_TAXI_ETL", "true").lower() == "true"

# ---------------------------------------------------------------------------
# Alert configuration — read from environment, never hardcoded
# ---------------------------------------------------------------------------
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "")
ALERT_SMTP_USER = os.getenv("ALERT_SMTP_USER", "")
ALERT_SMTP_PASSWORD = os.getenv("ALERT_SMTP_PASSWORD", "")
ALERT_SMTP_HOST = "smtp.gmail.com"
ALERT_SMTP_PORT = 587


def notify_on_failure(context: dict) -> None:
    """Send a Gmail alert when a task fails after all retries are exhausted.

    Reads ALERT_EMAIL_TO, ALERT_SMTP_USER, ALERT_SMTP_PASSWORD from environment.
    Silently skips if any of those variables are unset so that local dev runs
    without SMTP credentials do not crash the callback itself.
    """
    if not all([ALERT_EMAIL_TO, ALERT_SMTP_USER, ALERT_SMTP_PASSWORD]):
        print(
            "notify_on_failure: ALERT_EMAIL_TO / ALERT_SMTP_USER / ALERT_SMTP_PASSWORD "
            "not set — skipping email alert."
        )
        return

    dag_id = context.get("dag").dag_id
    task_id = context.get("task_instance").task_id
    run_id = context.get("run_id", "unknown")
    execution_date = context.get("execution_date", "unknown")
    exception = context.get("exception", "No exception details available.")
    log_url = context.get("task_instance").log_url

    subject = f"[Airflow FAILED] {dag_id} › {task_id}"
    body = textwrap.dedent(f"""\
        A task in your NYC Taxi pipeline has failed.

        DAG         : {dag_id}
        Task        : {task_id}
        Run ID      : {run_id}
        Exec date   : {execution_date}
        Exception   : {exception}

        Log URL     : {log_url}

        This task has exhausted all configured retries.
        Check the Airflow UI for full traceback.
    """)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = ALERT_SMTP_USER
    msg["To"] = ALERT_EMAIL_TO

    try:
        with smtplib.SMTP(ALERT_SMTP_HOST, ALERT_SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(ALERT_SMTP_USER, ALERT_SMTP_PASSWORD)
            server.sendmail(ALERT_SMTP_USER, [ALERT_EMAIL_TO], msg.as_string())
        print(f"notify_on_failure: alert sent to {ALERT_EMAIL_TO}")
    except Exception as exc:  # noqa: BLE001
        # Never let the alert callback itself crash Airflow task state
        print(f"notify_on_failure: failed to send email — {exc}")


def project_path(*parts: str) -> str:
    """Build a host path from the explicit project-root environment variable."""
    return str(Path(PROJECT_ROOT, *parts))


def project_mounts(*, include_dbt: bool = False) -> list[Mount]:
    """Return Docker bind mounts required by Spark/dbt task containers."""
    mounts = [
        Mount(source=project_path("data"), target=f"{CONTAINER_PROJECT_DIR}/data", type="bind"),
        Mount(
            source=project_path("spark"),
            target=f"{CONTAINER_PROJECT_DIR}/spark",
            type="bind",
            read_only=True,
        ),
        Mount(
            source=project_path("gcp_service_account.json"),
            target=CONTAINER_KEYFILE,
            type="bind",
            read_only=True,
        ),
    ]
    if include_dbt:
        mounts.append(
            Mount(
                source=project_path("dbt"),
                target=f"{CONTAINER_PROJECT_DIR}/dbt",
                type="bind",
            )
        )
    return mounts


def runtime_environment() -> dict[str, str]:
    """Return non-secret runtime environment passed to ETL task containers."""
    return {
        "GCP_PROJECT_ID": os.getenv("GCP_PROJECT_ID", ""),
        "GCP_DATASET_RAW": os.getenv("GCP_DATASET_RAW", ""),
        "GCP_KEYFILE_PATH": CONTAINER_KEYFILE,
        "ETL_LOCAL_RETENTION_DAYS": os.getenv("ETL_LOCAL_RETENTION_DAYS", "7"),
    }


@dag(
    dag_id=DAG_ID,
    description="Run NYC Taxi Spark ETL, dbt transformations, tests, and finalization.",
    start_date=START_DATE,
    schedule="0 6 1 * *",
    catchup=False,
    max_active_runs=1,
    tags=["nyc-taxi", "production", "spark", "dbt"],
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "on_failure_callback": notify_on_failure,
    },
)
def nyc_taxi_etl_pipeline() -> None:
    """Define the production batch workflow with explicit safety checks."""

    @task
    def validate_runtime_configuration() -> None:
        """Fail before any write if the production switch or required host files are absent."""
        if not ETL_ENABLED:
            raise AirflowFailException(
                "ETL blocked: set ENABLE_NYC_TAXI_ETL=true in .env after reviewing BigQuery writes."
            )
        if not PROJECT_ROOT:
            raise AirflowFailException("ETL blocked: NYC_TAXI_PROJECT_ROOT is not configured.")

        is_absolute_host_path = Path(PROJECT_ROOT).is_absolute() or PureWindowsPath(PROJECT_ROOT).is_absolute()
        if not is_absolute_host_path:
            raise AirflowFailException("ETL blocked: NYC_TAXI_PROJECT_ROOT must be an absolute host path.")

        raw_data_dir = AIRFLOW_DATA_DIR / "raw" / "yellow"
        metadata_file = AIRFLOW_DATA_DIR / "metadata" / "etl_metadata.json"
        if not raw_data_dir.is_dir():
            raise AirflowFailException(f"ETL blocked: Airflow data mount missing: {raw_data_dir}")
        if not metadata_file.is_file():
            raise AirflowFailException(f"ETL blocked: metadata file missing: {metadata_file}")

        raw_files = sorted(raw_data_dir.glob("yellow_tripdata_*.parquet"))
        if not raw_files:
            raise AirflowFailException("ETL blocked: no Yellow Taxi raw Parquet files found.")

        print(f"Runtime configuration valid; {len(raw_files)} raw file(s) available")
        print("Docker daemon will validate host bind-mount sources when Spark starts")

    run_spark_etl = DockerOperator(
        task_id="run_spark_etl",
        image=SPARK_IMAGE,
        entrypoint=["python"],
        command=["/app/spark/etl/main.py"],
        environment=runtime_environment(),
        mounts=project_mounts(),
        docker_url="unix://var/run/docker.sock",
        auto_remove="success",
        mount_tmp_dir=False,
    )

    dbt_debug = DockerOperator(
        task_id="dbt_debug",
        image=DBT_IMAGE,
        entrypoint=["sh", "-c"],
        command=["cd /app/dbt && dbt debug"],
        environment=runtime_environment(),
        mounts=project_mounts(include_dbt=True),
        docker_url="unix://var/run/docker.sock",
        auto_remove="success",
        mount_tmp_dir=False,
    )

    dbt_deps = DockerOperator(
        task_id="dbt_deps",
        image=DBT_IMAGE,
        entrypoint=["sh", "-c"],
        command=["cd /app/dbt && dbt deps"],
        environment=runtime_environment(),
        mounts=project_mounts(include_dbt=True),
        docker_url="unix://var/run/docker.sock",
        auto_remove="success",
        mount_tmp_dir=False,
    )

    dbt_run = DockerOperator(
        task_id="dbt_run",
        image=DBT_IMAGE,
        entrypoint=["sh", "-c"],
        command=["cd /app/dbt && dbt run"],
        environment=runtime_environment(),
        mounts=project_mounts(include_dbt=True),
        docker_url="unix://var/run/docker.sock",
        auto_remove="success",
        mount_tmp_dir=False,
    )

    dbt_test = DockerOperator(
        task_id="dbt_test",
        image=DBT_IMAGE,
        entrypoint=["sh", "-c"],
        command=["cd /app/dbt && dbt test"],
        environment=runtime_environment(),
        mounts=project_mounts(include_dbt=True),
        docker_url="unix://var/run/docker.sock",
        auto_remove="success",
        mount_tmp_dir=False,
    )

    finalize_verified_batches = DockerOperator(
        task_id="finalize_verified_batches",
        image=DBT_IMAGE,
        entrypoint=["python"],
        command=["/app/spark/etl/finalize.py"],
        environment=runtime_environment(),
        mounts=project_mounts(include_dbt=True),
        docker_url="unix://var/run/docker.sock",
        auto_remove="success",
        mount_tmp_dir=False,
    )

    configuration_valid = validate_runtime_configuration()
    configuration_valid >> run_spark_etl >> dbt_debug >> dbt_deps >> dbt_run >> dbt_test >> finalize_verified_batches


nyc_taxi_etl_pipeline()
