from pyspark.sql import DataFrame
import pyspark.sql.functions as F
from spark.utils.logger import get_logger

logger = get_logger("spark.etl.transform")

def handle_null_values(df: DataFrame) -> DataFrame:
    logger.info("Đang xử lý các giá trị Null...")
    default_values = {
        "passenger_count": 1,
        "payment_type": 5,
        "extra": 0.0,
        "mta_tax": 0.0,
        "tip_amount": 0.0,
        "tolls_amount": 0.0,
        "improvement_surcharge": 0.0,
        "congestion_surcharge": 0.0,
        "Airport_fee": 0.0,
        "cbd_congestion_fee": 0.0
    }
    df_cleaned = df.fillna(default_values)
    return df_cleaned



def filter_outliers(df: DataFrame) -> DataFrame:
    logger.info("Đang lọc bỏ Outliers...")
    
    # Bắt buộc phải có ngoặc đơn () quanh từng điều kiện so sánh
    df_filtered = df.filter(
        (df["trip_distance"] > 0) & (df["trip_distance"] <= 100)
    )
    df_filtered = df_filtered.filter(
        (df_filtered["fare_amount"] >= 2.5) & (df_filtered["fare_amount"] <= 1000)
    )
    
    return df_filtered

def add_derived_columns(df: DataFrame) -> DataFrame:
    """
    Thêm các cột phái sinh (Feature Engineering) phục vụ báo cáo.
    
    Các cột cần tạo:
    1. `trip_duration_min`: Thời gian di chuyển tính bằng phút.
       - Công thức: (dropoff_datetime - pickup_datetime) quy ra phút.
       - Gợi ý: Sử dụng `F.unix_timestamp()` hoặc tính hiệu trực tiếp bằng phép trừ chuyển thành giây rồi chia 60.
       
    2. `tip_ratio`: Tỷ lệ tiền tip trên giá cước gốc (fare_amount).
       - Insight quan trọng: Tránh lỗi chia cho 0 (Division by Zero) nếu `fare_amount` bằng 0.
       - Gợi ý: Sử dụng hàm điều kiện `F.when(F.col("fare_amount") > 0, F.col("tip_amount") / F.col("fare_amount")).otherwise(0.0)`
       
    3. `pickup_date`: Trích xuất ngày (YYYY-MM-DD) từ `tpep_pickup_datetime` để phân vùng (partition) khi lưu dữ liệu.
       - Gợi ý: Sử dụng `F.to_date()`
    """
    logger.info("Đang tạo các cột phái sinh (derived columns)...")
    
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
