

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

# ─────────────────────────────────────────
# Static dim data
# ─────────────────────────────────────────
DIM_VENDOR_DATA = [
    {"vendor_key": 1, "vendor_name": "Creative Mobile Technologies"},
    {"vendor_key": 2, "vendor_name": "Curb Mobility"},
    {"vendor_key": 7, "vendor_name": "Unknown"},
]

DIM_PAYMENT_DATA = [
    {"payment_key": 1, "payment_name": "Credit card"},
    {"payment_key": 2, "payment_name": "Cash"},
    {"payment_key": 3, "payment_name": "No charge"},
    {"payment_key": 4, "payment_name": "Dispute"},
    {"payment_key": 5, "payment_name": "Unknown"},
    {"payment_key": 6, "payment_name": "Voided trip"},
]

DIM_RATE_DATA = [
    {"rate_key": 1,  "rate_name": "Standard rate"},
    {"rate_key": 2,  "rate_name": "JFK"},
    {"rate_key": 3,  "rate_name": "Newark"},
    {"rate_key": 4,  "rate_name": "Nassau or Westchester"},
    {"rate_key": 5,  "rate_name": "Negotiated fare"},
    {"rate_key": 6,  "rate_name": "Group ride"},
    {"rate_key": 99, "rate_name": "Unknown"},
]

# ─────────────────────────────────────────
# BigQuery schemas
# ─────────────────────────────────────────
SCHEMAS = {
    "fact_trip": [
        bigquery.SchemaField("trip_id",             "STRING",  mode="REQUIRED"),
        bigquery.SchemaField("vendor_key",           "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("pickup_time_key",      "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("dropoff_time_key",     "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("pickup_location_key",  "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("dropoff_location_key", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("payment_key",          "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("rate_key",             "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("passenger_count",      "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("trip_distance",        "FLOAT",   mode="NULLABLE"),
        bigquery.SchemaField("trip_duration_min",    "FLOAT",   mode="NULLABLE"),
        bigquery.SchemaField("fare_amount",          "FLOAT",   mode="NULLABLE"),
        bigquery.SchemaField("extra",                "FLOAT",   mode="NULLABLE"),
        bigquery.SchemaField("tip_amount",           "FLOAT",   mode="NULLABLE"),
        bigquery.SchemaField("tip_ratio",            "FLOAT",   mode="NULLABLE"),
        bigquery.SchemaField("tolls_amount",         "FLOAT",   mode="NULLABLE"),
        bigquery.SchemaField("congestion_surcharge", "FLOAT",   mode="NULLABLE"),
        bigquery.SchemaField("airport_fee",          "FLOAT",   mode="NULLABLE"),
        bigquery.SchemaField("cbd_congestion_fee",   "FLOAT",   mode="NULLABLE"),
        bigquery.SchemaField("total_amount",         "FLOAT",   mode="NULLABLE"),
        bigquery.SchemaField("pickup_date",          "DATE",    mode="NULLABLE"),
    ],
    "dim_vendor": [
        bigquery.SchemaField("vendor_key",  "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("vendor_name", "STRING",  mode="NULLABLE"),
    ],
    "dim_payment": [
        bigquery.SchemaField("payment_key",  "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("payment_name", "STRING",  mode="NULLABLE"),
    ],
    "dim_rate": [
        bigquery.SchemaField("rate_key",  "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("rate_name", "STRING",  mode="NULLABLE"),
    ],
    "dim_location": [
        bigquery.SchemaField("location_key",  "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("zone",          "STRING",  mode="NULLABLE"),
        bigquery.SchemaField("borough",       "STRING",  mode="NULLABLE"),
        bigquery.SchemaField("service_zone",  "STRING",  mode="NULLABLE"),
    ],
    "dim_time": [
        bigquery.SchemaField("time_key",     "INTEGER",  mode="REQUIRED"),
        bigquery.SchemaField("datetime",     "DATETIME", mode="NULLABLE"),
        bigquery.SchemaField("date",         "DATE",     mode="NULLABLE"),
        bigquery.SchemaField("year",         "INTEGER",  mode="NULLABLE"),
        bigquery.SchemaField("month",        "INTEGER",  mode="NULLABLE"),
        bigquery.SchemaField("month_name",   "STRING",   mode="NULLABLE"),
        bigquery.SchemaField("day",          "INTEGER",  mode="NULLABLE"),
        bigquery.SchemaField("day_of_week",  "INTEGER",  mode="NULLABLE"),
        bigquery.SchemaField("day_name",     "STRING",   mode="NULLABLE"),
        bigquery.SchemaField("hour",         "INTEGER",  mode="NULLABLE"),
        bigquery.SchemaField("is_weekend",   "BOOLEAN",  mode="NULLABLE"),
        bigquery.SchemaField("is_peak_hour", "BOOLEAN",  mode="NULLABLE"),
        bigquery.SchemaField("quarter",      "INTEGER",  mode="NULLABLE"),
    ],
}


class BigQueryLoader:
    """Load dữ liệu từ local Parquet → BigQuery dataset nyc_taxi_raw."""

    def __init__(self) -> None:
        credentials = service_account.Credentials.from_service_account_file(
            GCP_KEYFILE_PATH,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        self.client  = bigquery.Client(project=GCP_PROJECT_ID, credentials=credentials)
        self.dataset = GCP_DATASET_RAW
        self.project = GCP_PROJECT_ID
        logger.info(
            "BigQueryLoader initialized — project=%s, dataset=%s",
            self.project, self.dataset,
        )

    # ──────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────

    def _table_ref(self, table_name: str) -> str:
        return f"{self.project}.{self.dataset}.{table_name}"

    def _ensure_dataset(self) -> None:
        """Tạo dataset nếu chưa tồn tại."""
        dataset_ref = bigquery.Dataset(f"{self.project}.{self.dataset}")
        dataset_ref.location = "US"
        self.client.create_dataset(dataset_ref, exists_ok=True)
        logger.info("Dataset %s sẵn sàng.", self.dataset)

    def _load_parquet_files(
        self,
        parquet_files: Sequence[Path],
        table_name: str,
        write_disposition: str = bigquery.WriteDisposition.WRITE_TRUNCATE,
    ) -> None:
        """Load danh sách Parquet files vào 1 BigQuery table."""
        table_ref  = self._table_ref(table_name)
   
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
            write_disposition=write_disposition,
            autodetect=True,
        )

        logger.info("Loading %d file(s) → %s ...", len(parquet_files), table_ref)
        for i, fpath in enumerate(parquet_files, 1):
            logger.info("  [%d/%d] %s", i, len(parquet_files), fpath.name)
            # File đầu tiên dùng write_disposition gốc, các file sau APPEND
            if i > 1:
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
            with open(fpath, "rb") as f:
                job = self.client.load_table_from_file(f, table_ref, job_config=job_config)
                job.result()

        tbl = self.client.get_table(table_ref)
        logger.info("✓ %s — total rows: %d", table_ref, tbl.num_rows)

    def _load_rows(self, rows: list[dict], table_name: str) -> None:
        """Load static rows (dim tables nhỏ) vào BigQuery qua batch load (không dùng Streaming Insert).
        Dùng load_table_from_json thay vì insert_rows để tương thích GCP free tier."""
        import io, json as _json
        table_ref = self._table_ref(table_name)
        schema    = SCHEMAS[table_name]

        # Drop + recreate để đảm bảo idempotent
        self.client.delete_table(table_ref, not_found_ok=True)
        self.client.create_table(bigquery.Table(table_ref, schema=schema))

        # Ghi rows dưới dạng newline-delimited JSON rồi batch load
        ndjson = "\n".join(_json.dumps(r) for r in rows).encode("utf-8")
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            schema=schema,
        )
        job = self.client.load_table_from_file(
            io.BytesIO(ndjson), table_ref, job_config=job_config
        )
        job.result()
        tbl = self.client.get_table(table_ref)
        logger.info("✓ %s — %d rows.", table_ref, tbl.num_rows)

    # ──────────────────────────────────────
    # Public entry-point
    # ──────────────────────────────────────

    def load_all(self) -> None:
    
        self._ensure_dataset()

        parquet_dir = PROCESSED_DIR / "yellow_taxi"
        parquet_files = sorted(parquet_dir.rglob("*.parquet"))

        if not parquet_files:
            raise FileNotFoundError(
                f"Không tìm thấy Parquet file nào trong: {parquet_dir}\n"
                "Hãy chạy bước load (Spark → local Parquet) trước."
            )

        logger.info(
            "Tìm thấy %d Parquet file(s) trong %s — bắt đầu load lên BigQuery...",
            len(parquet_files),
            parquet_dir,
        )

        # Load raw processed data — dbt sẽ transform sang star-schema
        self._load_parquet_files(
            parquet_files,
            table_name="yellow_taxi_raw",
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )

        # dim tables tĩnh (dùng schema cứng qua _load_rows)
        self._load_rows(DIM_VENDOR_DATA,  "dim_vendor")
        self._load_rows(DIM_PAYMENT_DATA, "dim_payment")
        self._load_rows(DIM_RATE_DATA,    "dim_rate")

        logger.info("=== BigQuery load hoàn tất ===")

    def load_batch(self, parquet_dir: Path, source_month: str) -> None:
        """Replace one source-month batch before appending it to BigQuery."""
        self._ensure_dataset()
        parquet_files = sorted(parquet_dir.rglob("*.parquet"))
        if not parquet_files:
            raise FileNotFoundError(f"Không tìm thấy processed batch: {parquet_dir}")
        table_ref = self._table_ref("yellow_taxi_raw")
        # DML DELETE không được phép trên BigQuery Sandbox (free tier).
        # Thay bằng: kiểm tra table tồn tại chưa, nếu chưa thì WRITE_TRUNCATE,
        # nếu đã có data từ tháng khác thì WRITE_APPEND (source_month column đảm bảo idempotent).
        try:
            tbl = self.client.get_table(table_ref)
            has_rows = tbl.num_rows > 0
        except Exception:
            has_rows = False
        disposition = (
            bigquery.WriteDisposition.WRITE_APPEND if has_rows
            else bigquery.WriteDisposition.WRITE_TRUNCATE
        )
        logger.info(
            "load_batch source_month=%s — table %s rows=%s → %s",
            source_month, table_ref, tbl.num_rows if has_rows else 0,
            "APPEND" if has_rows else "TRUNCATE",
        )
        # Nếu table cũ tồn tại nhưng thiếu source_month column → drop để recreate schema đúng.
        if has_rows:
            try:
                tbl_schema_names = {f.name for f in tbl.schema}
                if "source_month" not in tbl_schema_names:
                    logger.warning("Table thiếu source_month column, drop để recreate schema.")
                    self.client.delete_table(table_ref)
                    has_rows = False
                    disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
            except Exception as schema_err:
                logger.warning("Không kiểm tra được schema: %s", schema_err)
        self._load_parquet_files(parquet_files, "yellow_taxi_raw", disposition)
        self._load_rows(DIM_VENDOR_DATA, "dim_vendor")
        self._load_rows(DIM_PAYMENT_DATA, "dim_payment")
        self._load_rows(DIM_RATE_DATA, "dim_rate")


