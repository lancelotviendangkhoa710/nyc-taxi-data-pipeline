from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

from google.cloud import bigquery
from google.oauth2 import service_account

from spark.config import PROCESSED_DIR, ROOT_DIR
from spark.utils.logger import get_logger

logger = get_logger("spark.etl.load_bigquery")

GCP_PROJECT_ID   = os.getenv("GCP_PROJECT_ID", "nyc-taxi-data-pipeline-507015")
GCP_DATASET_RAW  = os.getenv("GCP_DATASET_RAW", "nyc_taxi_raw")
GCP_KEYFILE_PATH = os.getenv(
    "GCP_KEYFILE_PATH",
    str(ROOT_DIR / "gcp_service_account.json"),
)
if not os.path.exists(GCP_KEYFILE_PATH):
    fallback_key = str(ROOT_DIR / "gcp_service_account.json")
    if os.path.exists(fallback_key):
        GCP_KEYFILE_PATH = fallback_key
    elif os.path.exists("/app/gcp_service_account.json"):
        GCP_KEYFILE_PATH = "/app/gcp_service_account.json"


class BigQueryLoader:
    """Load du lieu tu local Parquet -> BigQuery table yellow_taxi_raw.

    Chi load raw data -- dim/fact tables duoc quan ly boi dbt (T2 transform).
    """

    def __init__(self) -> None:
        credentials = service_account.Credentials.from_service_account_file(
            GCP_KEYFILE_PATH,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        self.client  = bigquery.Client(project=GCP_PROJECT_ID, credentials=credentials)
        self.dataset = GCP_DATASET_RAW
        self.project = GCP_PROJECT_ID
        logger.info(
            "BigQueryLoader initialized -- project=%s, dataset=%s",
            self.project, self.dataset,
        )

    def _table_ref(self, table_name: str) -> str:
        return f"{self.project}.{self.dataset}.{table_name}"

    def _ensure_dataset(self) -> None:
        """Tao dataset neu chua ton tai."""
        dataset_ref = bigquery.Dataset(f"{self.project}.{self.dataset}")
        dataset_ref.location = "US"
        self.client.create_dataset(dataset_ref, exists_ok=True)
        logger.info("Dataset %s san sang.", self.dataset)

    def _load_parquet_files(
        self,
        parquet_files: Sequence[Path],
        table_name: str,
        write_disposition: str = bigquery.WriteDisposition.WRITE_TRUNCATE,
    ) -> None:
        """Load danh sach Parquet files vao 1 BigQuery table."""
        table_ref  = self._table_ref(table_name)
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
            write_disposition=write_disposition,
            autodetect=True,
        )
        logger.info("Loading %d file(s) -> %s ...", len(parquet_files), table_ref)
        for i, fpath in enumerate(parquet_files, 1):
            logger.info("  [%d/%d] %s", i, len(parquet_files), fpath.name)
            if i > 1:
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
            with open(fpath, "rb") as f:
                job = self.client.load_table_from_file(f, table_ref, job_config=job_config)
                job.result()
        tbl = self.client.get_table(table_ref)
        logger.info("OK %s -- total rows: %d", table_ref, tbl.num_rows)

    def load_all(self) -> None:
        """Load toan bo processed Parquet -> yellow_taxi_raw.
        Dim/fact tables duoc tao boi dbt sau buoc nay.
        """
        self._ensure_dataset()
        parquet_dir   = PROCESSED_DIR / "yellow_taxi"
        parquet_files = sorted(parquet_dir.rglob("*.parquet"))
        if not parquet_files:
            raise FileNotFoundError(
                f"Khong tim thay Parquet file nao trong: {parquet_dir}\n"
                "Hay chay buoc load (Spark -> local Parquet) truoc."
            )
        logger.info(
            "Tim thay %d Parquet file(s) trong %s -- bat dau load len BigQuery...",
            len(parquet_files), parquet_dir,
        )
        self._load_parquet_files(
            parquet_files,
            table_name="yellow_taxi_raw",
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )
        logger.info("=== BigQuery load hoan tat -- chay dbt de build dim/fact ===")

    def load_batch(self, parquet_dir: Path, source_month: str) -> None:
        """Replace one source-month batch truoc khi append len BigQuery."""
        self._ensure_dataset()
        parquet_files = sorted(parquet_dir.rglob("*.parquet"))
        if not parquet_files:
            raise FileNotFoundError(f"Khong tim thay processed batch: {parquet_dir}")
        table_ref = self._table_ref("yellow_taxi_raw")
        try:
            tbl      = self.client.get_table(table_ref)
            has_rows = tbl.num_rows > 0
        except Exception:
            has_rows = False
        disposition = (
            bigquery.WriteDisposition.WRITE_APPEND if has_rows
            else bigquery.WriteDisposition.WRITE_TRUNCATE
        )
        logger.info(
            "load_batch source_month=%s -- table %s rows=%s -> %s",
            source_month, table_ref, tbl.num_rows if has_rows else 0,
            "APPEND" if has_rows else "TRUNCATE",
        )
        if has_rows:
            try:
                tbl_schema_names = {f.name for f in tbl.schema}
                if "source_month" not in tbl_schema_names:
                    logger.warning("Table thieu source_month column, drop de recreate schema.")
                    self.client.delete_table(table_ref)
                    has_rows    = False
                    disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
            except Exception as schema_err:
                logger.warning("Khong kiem tra duoc schema: %s", schema_err)
        self._load_parquet_files(parquet_files, "yellow_taxi_raw", disposition)
        logger.info("load_batch hoan tat -- chay dbt de refresh dim/fact.")
