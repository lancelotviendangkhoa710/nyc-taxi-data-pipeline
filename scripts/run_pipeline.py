"""
Script chạy full ETL pipeline: Extract → Transform → Load lên Supabase PostgreSQL.

Usage:
    python -m scripts.run_pipeline
    hoặc
    python scripts/run_pipeline.py
"""
import sys
import os

# Thêm root vào sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spark.config import RAW_DIR, YELLOW_TAXI_PATTERN
from spark.etl.extract import get_spark_session, extract_data
from spark.etl.transform import handle_null_values, filter_outliers, add_derived_columns
from spark.etl.load_warehouse import YellowTaxiWarehouseLoader

def main():
    print("=" * 60)
    print(" NYC Taxi ETL Pipeline -> Supabase PostgreSQL")
    print("=" * 60)

    # 1. Extract
    print("\n[1/3] EXTRACT: Khởi tạo Spark & đọc dữ liệu raw...")
    spark = get_spark_session()
    df_raw = extract_data(spark, str(RAW_DIR), YELLOW_TAXI_PATTERN)
    raw_count = df_raw.count()
    print(f"  → Đọc được {raw_count:,} bản ghi")

    # 2. Transform
    print("\n[2/3] TRANSFORM: Xử lý null, outliers, derived columns...")
    df = handle_null_values(df_raw)
    df = filter_outliers(df)
    df = add_derived_columns(df)
    transformed_count = df.count()
    print(f"  → Sau transform: {transformed_count:,} bản ghi (loại {raw_count - transformed_count:,} outliers)")

    # 3. Load Warehouse
    print("\n[3/3] LOAD: Ghi dữ liệu lên Supabase PostgreSQL...")
    loader = YellowTaxiWarehouseLoader(spark)
    loader.load_all(df)

    print("\n" + "=" * 60)
    print(" ✅ Pipeline hoàn thành!")
    print("=" * 60)

    spark.stop()

if __name__ == "__main__":
    main()