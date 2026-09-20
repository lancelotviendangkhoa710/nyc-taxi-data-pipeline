from __future__ import annotations
import os, smtplib, textwrap
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path, PureWindowsPath
from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

DAG_ID="nyc_taxi_full_reload"; SPARK_IMAGE="docker-spark-etl:latest"; DBT_IMAGE="docker-dbt:latest"
CONTAINER_PROJECT_DIR="/app"; CONTAINER_KEYFILE=f"{CONTAINER_PROJECT_DIR}/gcp_service_account.json"
START_DATE=datetime(2025,1,1)
PROJECT_ROOT=os.getenv("NYC_TAXI_PROJECT_ROOT",""); ETL_ENABLED=os.getenv("ENABLE_NYC_TAXI_ETL","true").lower()=="true"
ALERT_EMAIL_TO=os.getenv("ALERT_EMAIL_TO",""); ALERT_SMTP_USER=os.getenv("ALERT_SMTP_USER","")
ALERT_SMTP_PASSWORD=os.getenv("ALERT_SMTP_PASSWORD",""); ALERT_SMTP_HOST="smtp.gmail.com"; ALERT_SMTP_PORT=587

def notify_on_failure(context):
    if not all([ALERT_EMAIL_TO,ALERT_SMTP_USER,ALERT_SMTP_PASSWORD]):
        print("notify_on_failure: bien SMTP chua set."); return
    ti=context.get("task_instance")
    subject=f"[Airflow FAILED] {context.get('dag').dag_id} - {ti.task_id}"
    body=f"DAG:{context.get('dag').dag_id} Task:{ti.task_id} Run:{context.get('run_id')} Log:{ti.log_url}"
    msg=MIMEText(body); msg["Subject"]=subject; msg["From"]=ALERT_SMTP_USER; msg["To"]=ALERT_EMAIL_TO
    try:
        with smtplib.SMTP(ALERT_SMTP_HOST,ALERT_SMTP_PORT) as s:
            s.ehlo(); s.starttls(); s.login(ALERT_SMTP_USER,ALERT_SMTP_PASSWORD)
            s.sendmail(ALERT_SMTP_USER,[ALERT_EMAIL_TO],msg.as_string())
    except Exception as e: print(f"notify_on_failure: loi -- {e}")

def project_path(*parts): return str(Path(PROJECT_ROOT,*parts))

def project_mounts(*, include_dbt=False):
    m=[
        Mount(source=project_path("data"),target=f"{CONTAINER_PROJECT_DIR}/data",type="bind"),
        Mount(source=project_path("spark"),target=f"{CONTAINER_PROJECT_DIR}/spark",type="bind",read_only=True),
        Mount(source=project_path("scripts"),target=f"{CONTAINER_PROJECT_DIR}/scripts",type="bind",read_only=True),
        Mount(source=project_path("gcp_service_account.json"),target=CONTAINER_KEYFILE,type="bind",read_only=True),
    ]
    if include_dbt: m.append(Mount(source=project_path("dbt"),target=f"{CONTAINER_PROJECT_DIR}/dbt",type="bind"))
    return m

def runtime_environment():
    return {"GCP_PROJECT_ID":os.getenv("GCP_PROJECT_ID",""),"GCP_DATASET_RAW":os.getenv("GCP_DATASET_RAW",""),
            "GCP_KEYFILE_PATH":CONTAINER_KEYFILE,"ETL_LOCAL_RETENTION_DAYS":os.getenv("ETL_LOCAL_RETENTION_DAYS","7")}

@dag(dag_id=DAG_ID,description="Full reload MANUAL only.",start_date=START_DATE,schedule=None,
     catchup=False,max_active_runs=1,tags=["nyc-taxi","production","full-reload","spark","dbt"],
     default_args={"retries":1,"retry_delay":timedelta(minutes=5),"on_failure_callback":notify_on_failure})
def nyc_taxi_full_reload():
    @task
    def validate_config():
        if not ETL_ENABLED: raise AirflowFailException("Full Reload bi chan: ENABLE_NYC_TAXI_ETL=true.")
        if not PROJECT_ROOT: raise AirflowFailException("Full Reload bi chan: NYC_TAXI_PROJECT_ROOT missing.")
        if not (Path(PROJECT_ROOT).is_absolute() or PureWindowsPath(PROJECT_ROOT).is_absolute()):
            raise AirflowFailException("Full Reload bi chan: NYC_TAXI_PROJECT_ROOT phai absolute path.")
        print(f"[OK] PROJECT_ROOT={PROJECT_ROOT}")

    def docker(tid, img, cmd, dbt=False):
        return DockerOperator(task_id=tid,image=img,entrypoint=["python"] if not cmd[0].startswith("cd") else ["sh","-c"],
            command=cmd,environment=runtime_environment(),mounts=project_mounts(include_dbt=dbt),
            docker_url="unix://var/run/docker.sock",auto_remove="success",mount_tmp_dir=False)

    reset_local  = docker("reset_local_data","docker-spark-etl:latest",["/app/scripts/reset_local_data.py"])
    reset_bq     = docker("reset_bigquery",  "docker-spark-etl:latest",["/app/scripts/reset_bigquery_noconfirm.py"])
    fetch        = DockerOperator(task_id="fetch_data",image=SPARK_IMAGE,entrypoint=["python"],
                     command=["/app/spark/etl/fetch_taxi_data.py"],environment=runtime_environment(),
                     mounts=project_mounts(),docker_url="unix://var/run/docker.sock",
                     auto_remove="success",mount_tmp_dir=False,execution_timeout=timedelta(hours=3))
    spark        = docker("run_spark_etl",   SPARK_IMAGE,["/app/spark/etl/main.py"])
    dbt_debug    = docker("dbt_debug",  DBT_IMAGE,["cd /app/dbt && dbt debug"],dbt=True)
    dbt_deps     = docker("dbt_deps",   DBT_IMAGE,["cd /app/dbt && dbt deps"], dbt=True)
    dbt_run      = docker("dbt_run",    DBT_IMAGE,["cd /app/dbt && dbt run"],  dbt=True)
    dbt_test     = docker("dbt_test",   DBT_IMAGE,["cd /app/dbt && dbt test"], dbt=True)
    finalize     = docker("finalize_verified_batches",DBT_IMAGE,["/app/spark/etl/finalize.py"],dbt=True)

    validate_config() >> reset_local >> reset_bq >> fetch >> spark >> dbt_debug >> dbt_deps >> dbt_run >> dbt_test >> finalize

nyc_taxi_full_reload()
