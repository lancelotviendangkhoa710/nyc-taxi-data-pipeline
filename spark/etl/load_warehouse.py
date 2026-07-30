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
        
        logger.info(f"Khởi tạo Warehouse Loader thành công")
        logger.info(f"PostgreSQL Connection: {PG_HOST}:{PG_PORT}/{PG_DATABASE}")
        
    def _write_to_postgres(self, df: DataFrame, table_name: str, mode: str = "append") -> None:
   
        logger.info(f"Đang ghi dữ liệu lên bảng PostgreSQL: {table_name} (Mode: {mode})...")
        try:
            writer = df.write \
                .format("jdbc") \
                .option("url", self.jdbc_url) \
                .option("dbtable", table_name) \
                .option("user", self.properties["user"]) \
                .option("password", self.properties["password"]) \
                .option("driver", self.properties["driver"])
            # Xử lý overwrite thủ công để tránh lỗi FK constraint
            if mode == "overwrite":
                import psycopg2
                from spark.config import PG_HOST, PG_PORT, PG_DATABASE, PG_USER, PG_PASSWORD
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
            logger.info(f"Ghi thành công bảng: {table_name}")
        except Exception as e:
            logger.error(f"Lỗi khi ghi dữ liệu lên PostgreSQL bảng {table_name}: {e}")
            raise e

    def load_dim_vendor(self) -> None:
        """Tạo và load bảng chiều tĩnh DIM_VENDOR"""
        logger.info("Đang tạo dữ liệu chiều DIM_VENDOR...")
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
        """Tạo và load bảng chiều tĩnh DIM_PAYMENT"""
        logger.info("Đang tạo dữ liệu chiều DIM_PAYMENT...")
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
        """Tạo và load bảng chiều tĩnh DIM_RATE"""
        logger.info("Đang tạo dữ liệu chiều DIM_RATE...")
        rate_data = [
            (1, "Standard rate"),
            (2, "JFK"),
            (3, "Newark"),
            (4, "Nassau/Westchester"),
            (5, "Negotiated fare"),
            (6, "Group ride")
        ]
        df_rate = self.spark.createDataFrame(rate_data, ["rate_key", "rate_name"])
        df_rate = df_rate.select(
            F.col("rate_key").cast("long"),
            F.col("rate_name").cast("string")
        )
        self._write_to_postgres(df_rate, "dim_rate", mode="overwrite")

    def load_dim_location(self) -> None:
        """Tải dữ liệu zones lookup từ GitHub và load lên DIM_LOCATION"""
        logger.info("Đang xử lý dữ liệu chiều DIM_LOCATION...")
        csv_path = os.path.join(str(RAW_DIR), "taxi_zone_lookup.csv")
        
        # Tải file CSV lookup nếu chưa tồn tại
        if not os.path.exists(csv_path):
            s3_url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"
            logger.info(f"Đang tải file zone lookup: {s3_url}")
            try:
                req = urllib.request.Request(
                    s3_url, 
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                with urllib.request.urlopen(req) as response, open(csv_path, 'wb') as out_file:
                    out_file.write(response.read())
                logger.info("Tải zone lookup thành công.")
            except Exception as e:
                logger.error(f"Lỗi khi tải file taxi_zone_lookup: {e}")
                raise e
                
        # Đọc bằng Spark
        df_csv = self.spark.read.option("header", "true").csv(csv_path)
        
        # Map sang cấu hình DIM_LOCATION
        df_location = df_csv.select(
            F.col("LocationID").cast("long").alias("location_key"),
            F.col("Zone").cast("string").alias("zone"),
            F.col("Borough").cast("string").alias("borough"),
            F.col("service_zone").cast("string").alias("service_zone")
        )
        self._write_to_postgres(df_location, "dim_location", mode="overwrite")

    def load_dim_time(self, df_processed: DataFrame) -> None:
        """Trích xuất và tính toán chiều DIM_TIME từ dữ liệu chuyến đi thực tế"""
        logger.info("Đang trích xuất dữ liệu chiều DIM_TIME...")
        
        # Lấy danh sách duy nhất các timestamp đón/trả khách
        pickups = df_processed.select("tpep_pickup_datetime").withColumnRenamed("tpep_pickup_datetime", "dt")
        dropoffs = df_processed.select("tpep_dropoff_datetime").withColumnRenamed("tpep_dropoff_datetime", "dt")
        unique_dts = pickups.union(dropoffs).distinct().filter(F.col("dt").isNotNull())
        
        # Làm tròn đến giờ (hour grain)
        unique_hours = unique_dts.select(F.date_trunc("hour", F.col("dt")).alias("datetime")).distinct()
        
        # Tạo cấu trúc DIM_TIME
        df_time = unique_hours.withColumn(
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
            F.dayofweek("datetime").cast("long") # 1=Chủ nhật, 7=Thứ 7
        ).withColumn(
            "day_name",
            F.date_format("datetime", "EEEE")
        ).withColumn(
            "hour",
            F.hour("datetime").cast("long")
        ).withColumn(
            "is_weekend",
            F.col("day_of_week").isin(1, 7).cast("boolean")
        ).withColumn(
            "is_peak_hour",
            ((~F.col("is_weekend")) & (F.col("hour").isin(7, 8, 9, 16, 17, 18, 19))).cast("boolean")
        ).withColumn(
            "quarter",
            F.quarter("datetime").cast("long")
        )
        
        # Lưu vào PostgreSQL
        self._write_to_postgres(df_time, "dim_time", mode="overwrite")

    def load_fact_trip(self, df_processed: DataFrame, mode: str = "append") -> None:
        """Map các cột của Processed DataFrame sang Fact table schema và lưu vào PostgreSQL"""
        logger.info("Đang chuẩn bị mapping dữ liệu cho bảng FACT_TRIP...")
        
        # Tạo khóa surrogate key ngẫu nhiên nhưng lặp lại được bằng cách hash MD5 các trường chính
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
        
        # Tạo khóa thời gian liên kết DIM_TIME
        df_fact = df_fact.withColumn(
            "pickup_time_key",
            F.date_format("tpep_pickup_datetime", "yyyyMMddHH").cast("long")
        ).withColumn(
            "dropoff_time_key",
            F.date_format("tpep_dropoff_datetime", "yyyyMMddHH").cast("long")
        )
        
        # Chọn và đổi tên các cột tương ứng với PostgreSQL DDL
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
            F.col("mta_tax").cast("double"),
            F.col("tip_amount").cast("double"),
            F.col("tip_ratio").cast("double"),
            F.col("tolls_amount").cast("double"),
            F.col("improvement_surcharge").cast("double"),
            F.col("congestion_surcharge").cast("double"),
            F.col("Airport_fee").cast("double").alias("airport_fee"),
            F.col("cbd_congestion_fee").cast("double"),
            F.col("total_amount").cast("double"),
            F.col("store_and_fwd_flag").cast("string")
        )
        df_fact_mapped = df_fact_mapped.limit(200)
        
        # Bảng fact thường append theo phân vùng
        self._write_to_postgres(df_fact_mapped, "fact_trip", mode=mode)

    def load_all(self, df_processed: DataFrame) -> None:
        """Khởi động toàn bộ luồng load warehouse"""
        logger.info("=== BẮT ĐẦU QUY TRÌNH LOAD WAREHOUSE (POSTGRESQL) ===")
        self.load_dim_vendor()
        self.load_dim_payment()
        self.load_dim_rate()
        self.load_dim_location()
        self.load_dim_time(df_processed)
        # Sử dụng append cho fact_trip để tránh lỗi unique constraint khi đã có dữ liệu
        self.load_fact_trip(df_processed, mode="overwrite")
        logger.info("=== QUY TRÌNH LOAD WAREHOUSE HOÀN THÀNH ===")