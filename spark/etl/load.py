import os
from pyspark.sql import DataFrame
from spark.config import SELECTED_COLUMNS, PROCESSED_DIR
from spark.utils.logger import get_logger

logger = get_logger("spark.etl.load")

def load_data(df: DataFrame, output_path: str = None, partition_col: str = "pickup_date") -> None:
    """
    Lưu DataFrame đã xử lý ra thư mục đích dưới định dạng Parquet,
    được phân vùng (partitioned) theo cột quy định.
    
    Parameters:
    -----------
    df : DataFrame
        Spark DataFrame chứa dữ liệu đã transform và sẵn sàng ghi.
    output_path : str, optional
        Đường dẫn thư mục để ghi dữ liệu. Nếu None, sẽ dùng PROCESSED_DIR / "yellow_taxi".
    partition_col : str, optional
        Cột được sử dụng để phân vùng (default: "pickup_date").
    """
    if output_path is None:
        output_path = str(PROCESSED_DIR / "yellow_taxi")
        
    logger.info(f"Đang chuẩn bị ghi dữ liệu ra đường dẫn: {output_path}")
    
    # 1. Chỉ giữ lại các cột được cấu hình trong config
    logger.info("Đang lọc các cột theo cấu hình SELECTED_COLUMNS...")
    try:
        df_selected = df.select(*SELECTED_COLUMNS)
    except Exception as e:
        logger.error(f"Lỗi khi lọc các cột SELECTED_COLUMNS: {e}")
        raise e
        
    # 2. Ghi dữ liệu ra định dạng Parquet với phân vùng
    logger.info(f"Đang thực hiện ghi dữ liệu dạng Parquet, phân vùng theo: {partition_col}...")
    try:
        # Sử dụng write.mode("overwrite") để có thể ghi đè/chạy lại ETL một cách idempotent
        (
            df_selected.write
            .mode("overwrite")
            .partitionBy(partition_col)
            .parquet(output_path)
        )
        logger.info(f"Ghi dữ liệu thành công ra: {output_path}")
    except Exception as e:
        logger.error(f"Lỗi khi ghi dữ liệu ra Parquet: {e}")
        raise e
