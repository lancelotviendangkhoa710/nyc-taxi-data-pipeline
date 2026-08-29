import os

from pyspark.sql import DataFrame
from spark.config import (
    RAW_DIR,
    PROCESSED_DIR,
    YELLOW_TAXI_PATTERN,
    SELECTED_COLUMNS,
    SPARK_LOG_LEVEL
)
from spark.etl.extract import get_spark_session, extract_data
from spark.etl.validate import validate_schema, is_empty_dataframe
from spark.etl.transform import handle_null_values, filter_outliers, add_derived_columns
from spark.etl.load import load_data
from spark.utils.logger import get_logger

class YellowTaxiETLPipeline:

    def __init__(self):
        self.logger = get_logger("spark.etl.pipeline")
        self.spark = None
    
        derived_cols = ["trip_duration_min", "tip_ratio", "pickup_date"]
        self.required_cols = [col for col in SELECTED_COLUMNS if col not in derived_cols]
        
    def initialize_spark(self):
        self.logger.info("Khá»Ÿi táº¡o Spark Session...")
        self.spark = get_spark_session()
        self.spark.sparkContext.setLogLevel(SPARK_LOG_LEVEL)
        self.logger.info(f"ÄÃ£ cáº¥u hÃ¬nh log level: {SPARK_LOG_LEVEL}")
        
    def extract(self) -> DataFrame:
        self.logger.info("=== Báº®T Äáº¦U PHáº¦N EXTRACT ===")
        df = extract_data(self.spark, str(RAW_DIR), YELLOW_TAXI_PATTERN)
        return df
        
    def validate(self, df: DataFrame) -> bool:
        self.logger.info("=== Báº®T Äáº¦U PHáº¦N VALIDATE ===")
        
        self.logger.info("Äang kiá»ƒm tra schema Ä‘áº§u vÃ o...")
        if not validate_schema(df, self.required_cols):
            self.logger.error("Kiá»ƒm tra schema tháº¥t báº¡i!")
            return False
            
        self.logger.info("Äang kiá»ƒm tra DataFrame rá»—ng...")
        if is_empty_dataframe(df):
            self.logger.error("DataFrame nguá»“n khÃ´ng cÃ³ dÃ²ng dá»¯ liá»‡u nÃ o!")
            return False
            
        self.logger.info("Táº¥t cáº£ cÃ¡c kiá»ƒm tra validate thÃ nh cÃ´ng!")
        return True
        
    def transform(self, df: DataFrame) -> DataFrame:
        self.logger.info("=== TRANSFORMING ===")
        
        # Xá»­ lÃ½ cÃ¡c giÃ¡ trá»‹ Null
        df_nulls_handled = handle_null_values(df)
        
        # Lá»c Outliers
        df_filtered = filter_outliers(df_nulls_handled)
        
        # ThÃªm cÃ¡c cá»™t phÃ¡i sinh
        df_transformed = add_derived_columns(df_filtered)
        
        return df_transformed
        
    def load(self, df: DataFrame) -> None:
        self.logger.info("=== Starting Load ===")
        output_path = str(PROCESSED_DIR / "yellow_taxi")
        load_data(df, output_path, partition_col="pickup_date")
        
    def load_warehouse(self, df: DataFrame) -> None:
        self.logger.info("=== Starting Load to Warehouse ( PostgreSQL) ===")
        from spark.etl.load_warehouse import YellowTaxiWarehouseLoader
        loader = YellowTaxiWarehouseLoader(self.spark)
        loader.load_all(df)
        
    def run(self):
      
        self.logger.info("=== Báº®T Äáº¦U CHáº Y ETL PIPELINE (OOP) ===")
        try:
            self.initialize_spark()
            
            # 1. Extract
            df_raw = self.extract()
            
            # 2. Validate
            if not self.validate(df_raw):
                raise ValueError("Dá»¯ liá»‡u nguá»“n khÃ´ng há»£p lá»‡ Ä‘á»ƒ xá»­ lÃ½!")
                
            # 3. Transform
            df_transformed = self.transform(df_raw)

            # Optional cap for fast, repeatable test runs.
            test_row_limit = os.getenv("ETL_TEST_ROW_LIMIT")
            if test_row_limit:
                row_limit = int(test_row_limit)
                if row_limit <= 0:
                    raise ValueError("ETL_TEST_ROW_LIMIT must be a positive integer")
                self.logger.info(f"Limiting test run to {row_limit} transformed rows")
                df_transformed = df_transformed.limit(row_limit)
            
            # 4. Load
            self.load(df_transformed)
            
            # 5. Load Warehouse (Google BigQuery)
            try:
                self.load_warehouse(df_transformed)
            except Exception as bq_err:
                self.logger.warning(
                    f"KhÃ´ng thá»ƒ tá»± Ä‘á»™ng táº£i dá»¯ liá»‡u lÃªn BigQuery (CÃ³ thá»ƒ do tÃ i khoáº£n Sandbox chÆ°a kÃ­ch hoáº¡t Billing/Thanh toÃ¡n).\n"
                    f"Chi tiáº¿t lá»—i: {bq_err}\n"
                    f"Dá»¯ liá»‡u Ä‘Ã£ Ä‘Æ°á»£c xá»­ lÃ½ vÃ  lÆ°u thÃ nh cÃ´ng táº¡i thÆ° má»¥c processed cá»¥c bá»™ (data/processed/yellow_taxi/). "
                    f"Báº¡n cÃ³ thá»ƒ tiáº¿p tá»¥c táº£i lÃªn thá»§ cÃ´ng báº±ng cÃ¡ch sá»­ dá»¥ng giao diá»‡n web Console."
                )
            
            self.logger.info("=== ETL PIPELINE COMPLETED SUCCESSFULLY ===")
            
        except Exception as e:
            self.logger.error(f"ETL Pipeline failed extren: {e}", exc_info=True)
            raise e
        finally:
            if self.spark is not None:
                self.logger.info("Äang giáº£i phÃ³ng tÃ i nguyÃªn Spark Session...")
                self.spark.stop()
                self.logger.info("Spark Session Ä‘Ã£ dá»«ng thÃ nh cÃ´ng.")

