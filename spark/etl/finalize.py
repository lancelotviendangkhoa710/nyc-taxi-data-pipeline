"""Mark dbt-verified batches, then clean expired local staging artifacts."""
from spark.config import ETL_LOCAL_RETENTION_DAYS
from spark.etl.metadata import ETLMetadata


def main() -> None:
    metadata = ETLMetadata()
    for filename, record in list(metadata._records.items()):
        if record.get("status") == "bq_loaded":
            metadata.mark_dbt_tested(filename)
    metadata.complete_and_cleanup(ETL_LOCAL_RETENTION_DAYS)


if __name__ == "__main__":
    main()