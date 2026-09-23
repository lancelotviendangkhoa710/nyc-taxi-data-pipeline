from spark.etl.pipeline import YellowTaxiETLPipeline
from spark.etl.metadata import ETLMetadata
from spark.config import RAW_DIR, YELLOW_TAXI_PATTERN
from spark.utils.logger import get_logger

logger = get_logger(__name__)


def reconcile_processed_vs_dwh(metadata: ETLMetadata) -> None:
    """
    Kiem tra cac file co status='processed' trong metadata.
    Redshift logic pending.
    """
    pass

def main() -> None:
    initial_metadata = ETLMetadata()
    reconcile_processed_vs_dwh(initial_metadata)

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

