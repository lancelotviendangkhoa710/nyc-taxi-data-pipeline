
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from spark.config import RAW_DIR, YELLOW_TAXI_PATTERN
from spark.etl.extract import get_spark_session, extract_data
from spark.etl.transform import handle_null_values, filter_outliers, add_derived_columns, remove_duplicates
from spark.etl.load_warehouse import YellowTaxiWarehouseLoader

def main():
    print("=" * 60)
    print(" NYC Taxi ETL Pipeline -> Supabase PostgreSQL")
    print("=" * 60)

    # 1. Extract
    print("\n[1/3] EXTRACT: Initializing Spark & reading raw data...")
    spark = get_spark_session()
    df_raw = extract_data(spark,RAW_DIR, "yellow_tripdata_2026-01.parquet")#YELLOW_TAXI_PATTERN
    df_raw.show(5, truncate=False)
    raw_count = df_raw.count()
    print(f"  → Read {raw_count:,} records")

    # 2. Transform
    print("\n[2/3] TRANSFORM: Processing nulls, outliers, and derived columns...")
    df = handle_null_values(df_raw)
    df = filter_outliers(df)
    df = add_derived_columns(df)
    df = remove_duplicates(df)
    transformed_count = df.count()
    print(f"  → Post-transform: {transformed_count:,} records (removed {raw_count - transformed_count:,} outliers)")

    # 3. Load Warehouse
    print("\n[3/3] LOAD: Writing data to Supabase PostgreSQL...")
    loader = YellowTaxiWarehouseLoader(spark)
    loader.load_all(df)

    print("\n" + "=" * 60)
    print("  Pipeline completed successfully!")
    print("=" * 60)

    spark.stop()

if __name__ == "__main__":
    main()
