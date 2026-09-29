from pathlib import Path
from unittest.mock import Mock

from spark.etl.load_redshift import RedshiftLoader


def test_upload_to_s3_uses_partitioned_silver_key() -> None:
    loader = object.__new__(RedshiftLoader)
    loader.bucket = "test-bucket"
    loader.s3_client = Mock()

    s3_uri = loader._upload_to_s3(Path("part-00000.parquet"), "2026-01")

    assert s3_uri == "s3://test-bucket/silver/yellow_taxi/source_month=2026-01/part-00000.parquet"
    loader.s3_client.upload_file.assert_called_once_with(
        "part-00000.parquet",
        "test-bucket",
        "silver/yellow_taxi/source_month=2026-01/part-00000.parquet",
    )
