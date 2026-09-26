from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

import boto3
import redshift_connector
from spark.config import PROCESSED_DIR, ROOT_DIR
from spark.utils.logger import get_logger

logger = get_logger("spark.etl.load_redshift")

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET", "nyc-taxi-data-lake")
REDSHIFT_HOST = os.getenv("REDSHIFT_HOST", "redshift-cluster-1.xxxx.us-east-1.redshift.amazonaws.com")
REDSHIFT_PORT = int(os.getenv("REDSHIFT_PORT", "5439"))
REDSHIFT_DB = os.getenv("REDSHIFT_DB", "dev")
REDSHIFT_USER = os.getenv("REDSHIFT_USER", "awsuser")
REDSHIFT_PASSWORD = os.getenv("REDSHIFT_PASSWORD", "Password123")
IAM_ROLE = os.getenv("REDSHIFT_IAM_ROLE", "arn:aws:iam::123456789012:role/RedshiftS3Access")

class RedshiftLoader:

    def __init__(self) -> None:
        self.s3_client = boto3.client("s3", region_name=AWS_REGION)
        self.bucket = S3_BUCKET
        self.conn = redshift_connector.connect(
            host=REDSHIFT_HOST,
            port=REDSHIFT_PORT,
            database=REDSHIFT_DB,
            user=REDSHIFT_USER,
            password=REDSHIFT_PASSWORD
        )
        logger.info("RedshiftLoader initialized.")

    def _upload_to_s3(self, fpath: Path) -> str:
        s3_key = f"raw/yellow_taxi/{fpath.name}"
        self.s3_client.upload_file(str(fpath), self.bucket, s3_key)
        logger.info("Uploaded %s to s3://%s/%s", fpath.name, self.bucket, s3_key)
        return f"s3://{self.bucket}/{s3_key}"

    def _execute_query(self, query: str) -> None:
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            self.conn.commit()

    def _ensure_table(self) -> None:
        self._execute_query("""
            CREATE TABLE IF NOT EXISTS yellow_taxi_raw (
                VendorID INT,
                tpep_pickup_datetime TIMESTAMP,
                tpep_dropoff_datetime TIMESTAMP,
                passenger_count INT,
                trip_distance FLOAT8,
                RatecodeID INT,
                store_and_fwd_flag VARCHAR(1),
                PULocationID INT,
                DOLocationID INT,
                payment_type INT,
                fare_amount FLOAT8,
                extra FLOAT8,
                mta_tax FLOAT8,
                tip_amount FLOAT8,
                tolls_amount FLOAT8,
                improvement_surcharge FLOAT8,
                total_amount FLOAT8,
                congestion_surcharge FLOAT8,
                Airport_fee FLOAT8,
                cbd_congestion_fee FLOAT8,
                pickup_date DATE,
                source_month VARCHAR(7)
            );
        """)

    def load_batch(self, parquet_dir: Path, source_month: str) -> None:
        """Upload batch to S3 and copy to Redshift."""
        self._ensure_table()
        parquet_files = sorted(parquet_dir.rglob("*.parquet"))
        if not parquet_files:
            raise FileNotFoundError(f"Can not find any processed batch in: {parquet_dir}")
        
        # S3 upload
        s3_paths = []
        for f in parquet_files:
            s3_paths.append(self._upload_to_s3(f))
            
        logger.info("load_batch source_month=%s -> Redshift COPY", source_month)
        
        # Redshift logic: Delete old data for this month (idempotent), then copy
        self._execute_query(f"DELETE FROM yellow_taxi_raw WHERE source_month = '{source_month}';")
        
        for s3_uri in s3_paths:
            copy_sql = f"""
                COPY yellow_taxi_raw
                FROM '{s3_uri}'
                IAM_ROLE '{IAM_ROLE}'
                FORMAT AS PARQUET;
            """
            self._execute_query(copy_sql)
            
        logger.info("load_batch completed -- run dbt to refresh dim/fact.")

