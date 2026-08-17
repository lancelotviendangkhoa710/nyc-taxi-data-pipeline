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
    """
    Class điều phối toàn bộ luồng ETL cho dữ liệu Yellow Taxi trên Spark.
    Theo phong cách OOP Hybrid: quản lý tài nguyên và orchestration qua Class, 
    nhưng gọi các hàm xử lý phi trạng thái (functional) để biến đổi dữ liệu.
    """
    def __init__(self):
        self.logger = get_logger("spark.etl.pipeline")
        self.spark = None
        
        # Xác định danh sách các cột bắt buộc phải có trong schema raw trước khi transform
        # Loại trừ 3 cột phái sinh (derived) được sinh ra sau bước transform
        derived_cols = ["trip_duration_min", "tip_ratio", "pickup_date"]
        self.required_cols = [col for col in SELECTED_COLUMNS if col not in derived_cols]
        
    def initialize_spark(self):
        self.logger.info("Khởi tạo Spark Session...")
        self.spark = get_spark_session()
        self.spark.sparkContext.setLogLevel(SPARK_LOG_LEVEL)
        self.logger.info(f"Đã cấu hình log level: {SPARK_LOG_LEVEL}")
        
    def extract(self) -> DataFrame:
        self.logger.info("=== BẮT ĐẦU PHẦN EXTRACT ===")
        df = extract_data(self.spark, str(RAW_DIR), YELLOW_TAXI_PATTERN)
        return df
        
    def validate(self, df: DataFrame) -> bool:
        self.logger.info("=== BẮT ĐẦU PHẦN VALIDATE ===")
        
        self.logger.info("Đang kiểm tra schema đầu vào...")
        if not validate_schema(df, self.required_cols):
            self.logger.error("Kiểm tra schema thất bại!")
            return False
            
        self.logger.info("Đang kiểm tra DataFrame rỗng...")
        if is_empty_dataframe(df):
            self.logger.error("DataFrame nguồn không có dòng dữ liệu nào!")
            return False
            
        self.logger.info("Tất cả các kiểm tra validate thành công!")
        return True
        
    def transform(self, df: DataFrame) -> DataFrame:
        self.logger.info("=== BẮT ĐẦU PHẦN TRANSFORM ===")
        
        # Xử lý các giá trị Null
        df_nulls_handled = handle_null_values(df)
        
        # Lọc Outliers
        df_filtered = filter_outliers(df_nulls_handled)
        
        # Thêm các cột phái sinh
        df_transformed = add_derived_columns(df_filtered)
        
        return df_transformed
        
    def load(self, df: DataFrame) -> None:
        self.logger.info("=== BẮT ĐẦU PHẦN LOAD ===")
        output_path = str(PROCESSED_DIR / "yellow_taxi")
        load_data(df, output_path, partition_col="pickup_date")
        
    def load_warehouse(self, df: DataFrame) -> None:
        self.logger.info("=== BẮT ĐẦU PHẦN LOAD WAREHOUSE (BIGQUERY) ===")
        from spark.etl.load_warehouse import YellowTaxiWarehouseLoader
        loader = YellowTaxiWarehouseLoader(self.spark)
        loader.load_all(df)
        
    def run(self):
        """
        Orchestration chạy toàn bộ pipeline.
        Tự động dọn dẹp và dừng Spark Session an toàn kể cả khi có lỗi xảy ra.
        """
        self.logger.info("=== BẮT ĐẦU CHẠY ETL PIPELINE (OOP) ===")
        try:
            self.initialize_spark()
            
            # 1. Extract
            df_raw = self.extract()
            
            # 2. Validate
            if not self.validate(df_raw):
                raise ValueError("Dữ liệu nguồn không hợp lệ để xử lý!")
                
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
                    f"Không thể tự động tải dữ liệu lên BigQuery (Có thể do tài khoản Sandbox chưa kích hoạt Billing/Thanh toán).\n"
                    f"Chi tiết lỗi: {bq_err}\n"
                    f"Dữ liệu đã được xử lý và lưu thành công tại thư mục processed cục bộ (data/processed/yellow_taxi/). "
                    f"Bạn có thể tiếp tục tải lên thủ công bằng cách sử dụng giao diện web Console."
                )
            
            self.logger.info("=== ETL PIPELINE HOÀN THÀNH THÀNH CÔNG ===")
            
        except Exception as e:
            self.logger.error(f"ETL Pipeline gặp lỗi nghiêm trọng: {e}", exc_info=True)
            raise e
        finally:
            if self.spark is not None:
                self.logger.info("Đang giải phóng tài nguyên Spark Session...")
                self.spark.stop()
                self.logger.info("Spark Session đã dừng thành công.")
