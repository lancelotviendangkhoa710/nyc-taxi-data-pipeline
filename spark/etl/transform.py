from pyspark.sql import DataFrame
import pyspark.sql.functions as F
from spark.utils.logger import get_logger

logger = get_logger("spark.etl.transform")


def handle_null_values(df: DataFrame) -> DataFrame:
    """T1: Fill missing values với defaults hợp lý — không có business logic."""
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
    """T1: Xóa duplicate rows từ source."""
    logger.info("Removing duplicate records...")
    return df.dropDuplicates()


def standardize_data_types(df: DataFrame) -> DataFrame:
    """T1: Cast kiểu dữ liệu về đúng type — không transform value."""
    logger.info("Standardizing column data types...")
    df = df.withColumn("tpep_pickup_datetime",  F.col("tpep_pickup_datetime").cast("timestamp"))
    df = df.withColumn("tpep_dropoff_datetime", F.col("tpep_dropoff_datetime").cast("timestamp"))
    df = df.withColumn("passenger_count",       F.col("passenger_count").cast("integer"))
    df = df.withColumn("trip_distance",         F.col("trip_distance").cast("double"))
    df = df.withColumn("fare_amount",           F.col("fare_amount").cast("double"))
    df = df.withColumn("tip_amount",            F.col("tip_amount").cast("double"))
    return df


def add_pickup_date(df: DataFrame) -> DataFrame:
    """T1: Thêm pickup_date — cần thiết để partition Parquet theo ngày."""
    logger.info("Adding pickup_date column for partitioning...")
    return df.withColumn("pickup_date", F.to_date("tpep_pickup_datetime"))

