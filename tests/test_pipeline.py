from __future__ import annotations

import pytest
from pyspark.sql import SparkSession
from pyspark.sql import types as T

from spark.etl.transform import (
    add_pickup_date,
    handle_null_values,
    remove_duplicates,
    standardize_data_types,
)


@pytest.fixture(scope="module")
def spark() -> SparkSession:
    session = SparkSession.builder.master("local[1]").appName("nyc-taxi-tests").getOrCreate()
    yield session
    session.stop()


def test_t1_transforms_standardize_fill_deduplicate_and_add_pickup_date(spark: SparkSession) -> None:
    columns = [
        "VendorID",
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
        "passenger_count",
        "trip_distance",
        "fare_amount",
        "tip_amount",
    ]
    rows = [
        (1, "2026-01-01 10:00:00", "2026-01-01 10:10:00", None, "5.0", "10.0", None),
        (1, "2026-01-01 10:00:00", "2026-01-01 10:10:00", None, "5.0", "10.0", None),
    ]

    schema = T.StructType([
        T.StructField("VendorID", T.IntegerType(), True),
        T.StructField("tpep_pickup_datetime", T.StringType(), True),
        T.StructField("tpep_dropoff_datetime", T.StringType(), True),
        T.StructField("passenger_count", T.IntegerType(), True),
        T.StructField("trip_distance", T.StringType(), True),
        T.StructField("fare_amount", T.StringType(), True),
        T.StructField("tip_amount", T.DoubleType(), True),
    ])
    transformed = standardize_data_types(spark.createDataFrame(rows, schema))
    transformed = handle_null_values(transformed)
    transformed = remove_duplicates(transformed)
    transformed = add_pickup_date(transformed)

    result = transformed.collect()
    assert len(result) == 1
    assert result[0].passenger_count == 1
    assert result[0].tip_amount == 0.0
    assert result[0].trip_distance == 5.0
    assert result[0].fare_amount == 10.0
    assert str(result[0].pickup_date) == "2026-01-01"
