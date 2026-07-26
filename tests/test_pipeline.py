import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyspark.sql import SparkSession
from spark.etl.extract import get_spark_session
from spark.etl.transform import handle_null_values, filter_outliers, add_derived_columns

def test_pipeline():
    spark = get_spark_session()
    
    # Tạo dữ liệu mẫu
    data = [
        (1, "2026-01-01 10:00:00", "2026-01-01 10:10:00", 1, 5.0, 10.0, None),
        (1, "2026-01-01 11:00:00", "2026-01-01 11:05:00", None, 2.0, 5.0, 1.0)
    ]
    columns = ["VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count", "trip_distance", "fare_amount", "tip_amount"]
    
    df = spark.createDataFrame(data, columns)
    
    # Kiểm thử Transform
    df = handle_null_values(df)
    df = add_derived_columns(df)
    
    df.show()
    print("Pipeline test thành công!")
    spark.stop()

if __name__ == "__main__":
    test_pipeline()