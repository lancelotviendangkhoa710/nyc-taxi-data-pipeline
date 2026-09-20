from __future__ import annotations
import json, os
from datetime import datetime, timedelta
from pathlib import Path
from airflow.decorators import dag, task
from airflow.exceptions import AirflowSkipException
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

DAG_ID                = "nyc_taxi_integrity_check"
SPARK_IMAGE           = "docker-spark-etl:latest"
CONTAINER_PROJECT_DIR = "/app"
CONTAINER_KEYFILE     = f"{CONTAINER_PROJECT_DIR}/gcp_service_account.json"
START_DATE            = datetime(2025, 1, 1)
PROJECT_ROOT          = os.getenv("NYC_TAXI_PROJECT_ROOT", "")


def project_path(*parts): return str(Path(PROJECT_ROOT, *parts))


def project_mounts():
    return [
        Mount(source=project_path("data"),    target=f"{CONTAINER_PROJECT_DIR}/data",    type="bind"),
        Mount(source=project_path("spark"),   target=f"{CONTAINER_PROJECT_DIR}/spark",   type="bind", read_only=True),
        Mount(source=project_path("scripts"), target=f"{CONTAINER_PROJECT_DIR}/scripts", type="bind", read_only=True),
        Mount(source=project_path("gcp_service_account.json"), target=CONTAINER_KEYFILE, type="bind", read_only=True),
    ]


def runtime_environment():
    return {
        "GCP_PROJECT_ID":           os.getenv("GCP_PROJECT_ID", ""),
        "GCP_DATASET_RAW":          os.getenv("GCP_DATASET_RAW", ""),
        "GCP_KEYFILE_PATH":         CONTAINER_KEYFILE,
        "ETL_LOCAL_RETENTION_DAYS": os.getenv("ETL_LOCAL_RETENTION_DAYS", "7"),
    }


@dag(
    dag_id=DAG_ID,
    description=(
        "Ngay 15 moi thang: query BQ kiem tra tung thang co du du lieu khong. "
        "Neu thieu/lung lo -> trigger nyc_taxi_full_reload tu dong."
    ),
    start_date=START_DATE,
    schedule="0 6 15 * *",
    catchup=False,
    max_active_runs=1,
    tags=["nyc-taxi", "production", "integrity"],
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
)
def nyc_taxi_integrity_check():

    # ── 1. Query BQ, ghi integrity_report.json ───────────────────────────
    run_integrity_check = DockerOperator(
        task_id="run_integrity_check",
        image=SPARK_IMAGE,
        entrypoint=["python"],
        command=["/app/scripts/check_bq_integrity.py"],
        environment=runtime_environment(),
        mounts=project_mounts(),
        docker_url="unix://var/run/docker.sock",
        auto_remove="success",
        mount_tmp_dir=False,
    )

    # ── 2. Doc report, quyet dinh co trigger full reload khong ───────────
    @task
    def read_report_and_decide() -> dict:
        """
        Doc integrity_report.json tu host.
        - ok=True  : raise AirflowSkipException -> downstream bi skip
        - co loi   : tra conf cho TriggerDagRunOperator
        """
        if not PROJECT_ROOT:
            raise ValueError("NYC_TAXI_PROJECT_ROOT missing")

        rp = Path(PROJECT_ROOT) / "data" / "metadata" / "integrity_report.json"
        if not rp.exists():
            raise FileNotFoundError(f"integrity_report.json khong ton tai: {rp}")

        report = json.loads(rp.read_text(encoding="utf-8"))
        repair_needed = report.get("repair_needed", [])

        if report.get("ok") or not repair_needed:
            months = report.get("expected_months", [])
            print(f"[OK] Tat ca {len(months)} thang co du lieu day du tren BQ.")
            raise AirflowSkipException("BQ day du — khong can repair.")

        print(f"[ACTION] Phat hien {len(repair_needed)} thang bi thieu/lung lo: {repair_needed}")
        print("[ACTION] Se trigger nyc_taxi_full_reload de rebuild toan bo.")

        # Tra conf de TriggerDagRunOperator co the log thong tin
        return {
            "triggered_by": "integrity_check",
            "repair_needed": repair_needed,
            "checked_at": report.get("checked_at", ""),
        }

    # ── 3. Trigger full reload neu co loi ────────────────────────────────
    trigger_full_reload = TriggerDagRunOperator(
        task_id="trigger_full_reload",
        trigger_dag_id="nyc_taxi_full_reload",
        wait_for_completion=True,   # cho full reload chay xong roi moi done
        poke_interval=60,           # check moi 60s
        reset_dag_run=True,         # cho phep re-trigger neu da co run truoc
        allowed_states=["success"],
        failed_states=["failed"],
    )

    # ── Chain ─────────────────────────────────────────────────────────────
    run_integrity_check >> read_report_and_decide() >> trigger_full_reload


nyc_taxi_integrity_check()

