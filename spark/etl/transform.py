from pyspark.sql import DataFrame
import pyspark.sql.functions as F
from spark.utils.logger import get_logger
import os
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
        "cbd_congestion_fee": 0.0
    }
    # Chỉ fill các cột thực sự tồn tại trong DataFrame
    existing = {k: v for k, v in default_values.items() if k in df.columns}
    df_cleaned = df.fillna(existing)
    return df_cleaned



def filter_outliers(df: DataFrame) -> DataFrame:
    logger.info("Filtering outliers...")

    df_filtered = df.filter(
        (df["trip_distance"] > 0) & (df["trip_distance"] <= 100)
    )
    df_filtered = df_filtered.filter(
        (df_filtered["fare_amount"] >= 2.5) & (df_filtered["fare_amount"] <= 1000)
    )
    df_clean = df_filtered.filter(df_filtered["RatecodeID"] != 99)
    return df_clean

def add_derived_columns(df: DataFrame) -> DataFrame:
    logger.info("Generating derived columns...")

    df_transformed = df.withColumn(
        "trip_duration_min",
        (F.unix_timestamp("tpep_dropoff_datetime") - F.unix_timestamp("tpep_pickup_datetime")) / 60
    ).withColumn(
        "tip_ratio",
        F.when(F.col("fare_amount") > 0, F.col("tip_amount") / F.col("fare_amount")).otherwise(0.0)
    ).withColumn(
        "pickup_date",
        F.to_date("tpep_pickup_datetime")
    )
    
    return df_transformed

def remove_duplicates(df: DataFrame) -> DataFrame:
    logger.info("Removing duplicate records...")
    df_cleaned = df.dropDuplicates()
    return df_cleaned


def standardize_data_types(df: DataFrame) -> DataFrame:
    logger.info("Standardizing column data types...")
    df_standardized = df.withColumn("tpep_pickup_datetime", F.col("tpep_pickup_datetime").cast("timestamp"))
    df_standardized = df_standardized.withColumn("tpep_dropoff_datetime", F.col("tpep_dropoff_datetime").cast("timestamp"))
    df_standardized = df_standardized.withColumn("passenger_count", F.col("passenger_count").cast("integer"))
    df_standardized = df_standardized.withColumn("trip_distance", F.col("trip_distance").cast("double"))
    df_standardized = df_standardized.withColumn("fare_amount", F.col("fare_amount").cast("double"))
    df_standardized = df_standardized.withColumn("tip_amount", F.col("tip_amount").cast("double"))
    return df_standardized
