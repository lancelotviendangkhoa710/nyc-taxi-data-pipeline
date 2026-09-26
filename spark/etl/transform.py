from pyspark.sql import DataFrame
import pyspark.sql.functions as F
from pyspark.sql.types import TimestampType
from spark.utils.logger import get_logger

logger = get_logger("spark.etl.transform")


def handle_null_values(df: DataFrame) -> DataFrame:
    logger.info("Processing Null values...")
    default_values = {
        "passenger_count": 1,
        "payment_type": 5,
        "extra": 0.0,
        "tip_amount": 0.0,
        "tolls_amount": 0.0,
        "congestion_surcharge": 0.0,
        "Airport_fee": 0.0,
        "cbd_congestion_fee": 0.0,
    }
    existing = {k: v for k, v in default_values.items() if k in df.columns}
    return df.fillna(existing)


def remove_duplicates(df: DataFrame) -> DataFrame:
    logger.info("Removing duplicate records...")
    return df.dropDuplicates()


def standardize_data_types(df: DataFrame) -> DataFrame:

    logger.info("Standardizing column data types...")
    # PySpark 3.5 TimestampType writes microsecond parquet (timestamp_us).
    # Redshift COPY FORMAT AS PARQUET rejects nanosecond timestamps.
    df = df.withColumn("tpep_pickup_datetime",  F.col("tpep_pickup_datetime").cast(TimestampType()))
    df = df.withColumn("tpep_dropoff_datetime", F.col("tpep_dropoff_datetime").cast(TimestampType()))
    df = df.withColumn("passenger_count",       F.col("passenger_count").cast("integer"))
    df = df.withColumn("trip_distance",         F.col("trip_distance").cast("double"))
    df = df.withColumn("fare_amount",           F.col("fare_amount").cast("double"))
    df = df.withColumn("tip_amount",            F.col("tip_amount").cast("double"))
    df = df.withColumn("RatecodeID",            F.col("RatecodeID").cast("integer"))
    df = df.withColumn("payment_type",          F.col("payment_type").cast("integer"))
    return df


def add_pickup_date(df: DataFrame) -> DataFrame:
    logger.info("Adding pickup_date column for partitioning...")
    return df.withColumn("pickup_date", F.to_date("tpep_pickup_datetime"))

