import os
import urllib.request
from pyspark.sql import SparkSession, DataFrame
import spark 
from pyspark.sql import functions as F
from spark.config import (
    PG_HOST,
    PG_PORT,
    PG_DATABASE,
    PG_USER,
    PG_PASSWORD,
    PG_JDBC_URL,
    RAW_DIR
)
from spark.utils.logger import get_logger

logger = get_logger("spark.etl.load_warehouse")

class YellowTaxiWarehouseLoader:
    def __init__(self, spark_session: SparkSession):
        self.spark = spark_session
        self.jdbc_url = PG_JDBC_URL
        self.properties = {
            "user": PG_USER,
            "password": PG_PASSWORD,
            "driver": "org.postgresql.Driver"
        }
        
        logger.info("Warehouse Loader initialized successfully")
        logger.info(f"PostgreSQL Connection: {PG_HOST}:{PG_PORT}/{PG_DATABASE}")
        
    def _write_to_postgres(self, df: DataFrame, table_name: str, mode: str = "append") -> None:
        logger.info(f"Writing data to PostgreSQL table: {table_name} (Mode: {mode})...")
        try:
            writer = df.write \
                .format("jdbc") \
                .option("url", self.jdbc_url) \
                .option("dbtable", table_name) \
                .option("user", self.properties["user"]) \
                .option("password", self.properties["password"]) \
                .option("driver", self.properties["driver"])
      
            if mode == "overwrite":
                import psycopg2
                conn = psycopg2.connect(
                    host=PG_HOST, port=PG_PORT, database=PG_DATABASE, 
                    user=PG_USER, password=PG_PASSWORD
                )
                cur = conn.cursor()
                cur.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE")
                conn.commit()
                cur.close()
                conn.close()
                mode = "append"
            writer.mode(mode).save()
            logger.info(f"Successfully loaded table: {table_name}")
        except Exception as e:
            logger.error(f"Error writing data to PostgreSQL table {table_name}: {e}")
            raise e

    def load_dim_vendor(self) -> None:
        logger.info("Generating DIM_VENDOR dimension data...")
        vendor_data = [
            (1, "Creative Mobile Technologies"),
            (2, "Curb Mobility"),
            (7, "Unknown")
        ]
        df_vendor = self.spark.createDataFrame(vendor_data, ["vendor_key", "vendor_name"])
        df_vendor = df_vendor.select(
            F.col("vendor_key").cast("long"),
            F.col("vendor_name").cast("string")
        )
        self._write_to_postgres(df_vendor, "dim_vendor", mode="overwrite")

    def load_dim_payment(self) -> None:
        logger.info("Generating DIM_PAYMENT dimension data...")
        payment_data = [
            (1, "Credit card"),
            (2, "Cash"),
            (3, "No charge"),
            (4, "Dispute"),
            (5, "Unknown"),
            (6, "Voided trip")
        ]
        df_payment = self.spark.createDataFrame(payment_data, ["payment_key", "payment_name"])
        df_payment = df_payment.select(
            F.col("payment_key").cast("long"),
            F.col("payment_name").cast("string")
        )
        self._write_to_postgres(df_payment, "dim_payment", mode="overwrite")

    def load_dim_rate(self) -> None:
        logger.info("Generating DIM_RATE dimension data...")
        rate_data = [
            (1, "Standard rate"),
            (2, "JFK"),
            (3, "Newark"),
            (4, "Nassau or Westchester"),
            (5, "Negotiated fare"),
            (6, "Group ride"),
            (99, "Unknown")
        ]
        df_rate = self.spark.createDataFrame(rate_data, ["rate_key", "rate_name"])
        df_rate = df_rate.select(
            F.col("rate_key").cast("long"),
            F.col("rate_name").cast("string")
        )
        self._write_to_postgres(df_rate, "dim_rate", mode="overwrite")
    def load_dim_location(self) -> None:
        logger.info("Generating DIM_LOCATION dimension data from lookup CSV...")
        lookup_path = RAW_DIR / "taxi_zone_lookup.csv"
        
        if not lookup_path.exists():
            raise FileNotFoundError(f"Taxi zone lookup file not found at: {lookup_path}")
            
        df_lookup = (
            self.spark.read
            .option("header", "true")
            .csv(str(lookup_path))
        )
        
        df_location = df_lookup.select(
            F.col("LocationID").cast("long").alias("location_key"),
            F.col("Zone").cast("string").alias("zone"),
            F.col("Borough").cast("string").alias("borough"),
            F.col("service_zone").cast("string").alias("service_zone")
        )
        
        # Add a record for Unknown/Missing zones (LocationID 0 or missing key)
        unknown_loc = self.spark.createDataFrame(
            [(0, "Unknown", "Unknown", "Unknown")],
            ["location_key", "zone", "borough", "service_zone"]
        )
        
        df_location_final = df_location.union(unknown_loc)
        self._write_to_postgres(df_location_final, "dim_location", mode="overwrite")

    def load_dim_time(self, df_processed: DataFrame) -> None:
        logger.info("Generating DIM_TIME dimension data based on pickup/dropoff datetimes...")
        
        # Get unique hours from pickup and dropoff
        df_pickup_times = df_processed.select(F.col("tpep_pickup_datetime").alias("datetime"))
        df_dropoff_times = df_processed.select(F.col("tpep_dropoff_datetime").alias("datetime"))
        df_unique_times = df_pickup_times.union(df_dropoff_times).distinct()
        
        # Truncate to hour
        df_time_keys = df_unique_times.select(
            F.date_trunc("hour", F.col("datetime")).alias("datetime")
        ).distinct()
        
        # Generate dimension columns
        df_time = df_time_keys.withColumn(
            "time_key",
            F.date_format("datetime", "yyyyMMddHH").cast("long")
        ).withColumn(
            "date",
            F.to_date("datetime")
        ).withColumn(
            "year",
            F.year("datetime").cast("long")
        ).withColumn(
            "month",
            F.month("datetime").cast("long")
        ).withColumn(
            "month_name",
            F.date_format("datetime", "MMMM")
        ).withColumn(
            "day",
            F.dayofmonth("datetime").cast("long")
        ).withColumn(
            "day_of_week",
            # Monday=1, Sunday=7
            F.when(F.dayofweek("datetime") == 1, 7).otherwise(F.dayofweek("datetime") - 1).cast("long")
        ).withColumn(
            "day_name",
            F.date_format("datetime", "EEEE")
        ).withColumn(
            "hour",
            F.hour("datetime").cast("long")
        ).withColumn(
            "is_weekend",
            F.col("day_of_week").isin(6, 7).cast("boolean")
        ).withColumn(
            "is_peak_hour",
            F.col("hour").isin(7, 8, 9, 16, 17, 18, 19).cast("boolean")
        ).withColumn(
            "quarter",
            F.quarter("datetime").cast("long")
        )
        
        self._write_to_postgres(df_time, "dim_time", mode="overwrite")

    def load_fact_trip(self, df_processed: DataFrame, mode: str = "append") -> None:
        logger.info("Preparing fact trip data mapping for FACT_TRIP...")
        
        # MD5 surrogate key based on natural keys
        df_fact = df_processed.withColumn(
            "trip_id",
            F.md5(F.concat_ws("||",
                F.coalesce(F.col("VendorID").cast("string"), F.lit("")),
                F.coalesce(F.col("tpep_pickup_datetime").cast("string"), F.lit("")),
                F.coalesce(F.col("tpep_dropoff_datetime").cast("string"), F.lit("")),
                F.coalesce(F.col("PULocationID").cast("string"), F.lit("")),
                F.coalesce(F.col("DOLocationID").cast("string"), F.lit(""))
            ))
        )
        
        # Link time keys
        df_fact = df_fact.withColumn(
            "pickup_time_key",
            F.date_format("tpep_pickup_datetime", "yyyyMMddHH").cast("long")
        ).withColumn(
            "dropoff_time_key",
            F.date_format("tpep_dropoff_datetime", "yyyyMMddHH").cast("long")
        )
        
        # Map values to PostgreSQL DDL (excluding store_and_fwd_flag, mta_tax, improvement_surcharge)
        df_fact_mapped = df_fact.select(
            F.col("trip_id").cast("string"),
            F.when(F.col("VendorID").isin(1, 2), F.col("VendorID")).otherwise(F.lit(7)).cast("long").alias("vendor_key"),
            F.col("pickup_time_key").cast("long"),
            F.col("dropoff_time_key").cast("long"),
            F.coalesce(F.col("PULocationID"), F.lit(0)).cast("long").alias("pickup_location_key"),
            F.coalesce(F.col("DOLocationID"), F.lit(0)).cast("long").alias("dropoff_location_key"),
            F.coalesce(F.col("payment_type"), F.lit(0)).cast("long").alias("payment_key"),
            F.coalesce(F.col("RatecodeID"), F.lit(1)).cast("long").alias("rate_key"),
            F.col("passenger_count").cast("long"),
            F.col("trip_distance").cast("double"),
            F.col("trip_duration_min").cast("double"),
            F.col("fare_amount").cast("double"),
            F.col("extra").cast("double"),
            F.col("tip_amount").cast("double"),
            F.col("tip_ratio").cast("double"),
            F.col("tolls_amount").cast("double"),
            F.col("congestion_surcharge").cast("double"),
            F.col("Airport_fee").cast("double").alias("airport_fee"),
            F.col("cbd_congestion_fee").cast("double"),
            F.col("total_amount").cast("double"),
            F.col("pickup_date").cast("date")
        ).dropDuplicates(["trip_id"])
        
        self._write_to_postgres(df_fact_mapped, "fact_trip", mode=mode)

    def load_all(self, df_processed: DataFrame) -> None:
        logger.info("=== START WAREHOUSE LOADING PROCESS ===")
        self.load_dim_vendor()
        self.load_dim_payment()
        self.load_dim_rate()
        self.load_dim_location()
        self.load_dim_time(df_processed)
        self.load_fact_trip(df_processed, mode="overwrite")
        logger.info("=== WAREHOUSE LOADING COMPLETED SUCCESSFULLY ===")
        
        # Select and show 10 sample rows from each table
        tables = ["dim_vendor", "dim_payment", "dim_rate", "dim_location", "dim_time", "fact_trip"]
        logger.info("=== SHOWING 10 SAMPLE ROWS FROM EACH TABLE ===")
        for t in tables:
            try:
                logger.info(f"Table: {t.upper()}")
                df_sample = self.spark.read \
                    .format("jdbc") \
                    .option("url", self.jdbc_url) \
                    .option("dbtable", t) \
                    .option("user", self.properties["user"]) \
                    .option("password", self.properties["password"]) \
                    .option("driver", self.properties["driver"]) \
                    .load()
                df_sample.show(10, truncate=False)
            except Exception as e:
                logger.error(f"Could not select sample from table {t}: {e}")


