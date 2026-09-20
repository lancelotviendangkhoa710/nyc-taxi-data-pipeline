from spark.etl.pipeline import YellowTaxiETLPipeline
from spark.etl.load_bigquery import BigQueryLoader
from spark.etl.metadata import ETLMetadata
from spark.config import RAW_DIR, YELLOW_TAXI_PATTERN
from spark.utils.logger import get_logger

logger = get_logger(__name__)


def reconcile_processed_vs_bq(metadata: ETLMetadata) -> None:
    """
    Kiem tra cac file co status='processed' trong metadata:
    - Neu BQ da co data (rows > 0) cho thang do -> mark_bq_loaded
      (xu ly truong hop crash sau BQ write nhung truoc mark_bq_loaded)
    - Neu BQ khong co -> giu nguyen 'processed', pipeline se retry BQ
    Chi chay 1 lan truoc khi bat dau batch loop.
    """
    processed_files = [
        fn for fn, rec in metadata._records.items()
        if rec.get("status") == "processed"
    ]
    if not processed_files:
        return

    logger.info("[RECONCILE] Tim thay %d file(s) status=processed, kiem tra BQ...", len(processed_files))
    try:
        bq = BigQueryLoader()
        from google.cloud import bigquery as bq_sdk
        client = bq.client
        table_ref = f"{bq.project}.{bq.dataset}.yellow_taxi_raw"
        sql = f"""
            SELECT source_month, COUNT(*) AS row_count
            FROM `{table_ref}`
            GROUP BY source_month
        """
        bq_months = {r["source_month"]: r["row_count"] for r in client.query(sql).result()}
    except Exception as e:
        logger.warning("[RECONCILE] Khong query duoc BQ, bo qua reconcile: %s", e)
        return

    for filename in processed_files:
        record = metadata._records[filename]
        source_month = record.get("source_month", "")
        bq_rows = bq_months.get(source_month, 0)
        if bq_rows > 0:
            logger.info(
                "[RECONCILE] %s: status=processed nhung BQ co %d rows -> mark_bq_loaded",
                filename, bq_rows,
            )
            metadata.mark_bq_loaded(filename)
        else:
            logger.info(
                "[RECONCILE] %s: status=processed, BQ rows=0 -> giu nguyen, se retry BQ",
                filename,
            )


def main() -> None:
    """
    Chay ETL pipeline cho tat ca file chua xu ly.
    Buoc 0: reconcile metadata vs BQ truoc khi bat dau.
    Buoc 1+: xu ly tung file: extract -> validate -> transform -> load local -> load BQ.
    """
    # Reconcile truoc de dam bao metadata dong bo voi BQ thuc te
    initial_metadata = ETLMetadata()
    reconcile_processed_vs_bq(initial_metadata)

    batch = 0
    while True:
        pipeline = YellowTaxiETLPipeline()
        next_file = pipeline.metadata.get_latest_unprocessed(
            raw_dir=RAW_DIR,
            pattern=YELLOW_TAXI_PATTERN,
        )
        if next_file is None:
            if batch == 0:
                logger.info("Khong co file nao can xu ly.")
            else:
                logger.info("=== HOAN THANH: da xu ly %d file(s). ===", batch)
            break

        batch += 1
        logger.info("--- Bat dau batch %d: %s ---", batch, next_file.name)
        pipeline.run()
        logger.info("--- Hoan thanh batch %d: %s ---", batch, next_file.name)


if __name__ == "__main__":
    main()

