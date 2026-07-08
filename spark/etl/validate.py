from pyspark.sql import DataFrame
from spark.utils.logger import get_logger

logger = get_logger("spark.etl.validate")

def validate_schema(df: DataFrame, required_columns: list) -> bool:
    """
    Kiểm tra xem DataFrame đầu vào có chứa đủ các cột bắt buộc hay không.
    """
    # Lấy danh sách cột hiện tại của DataFrame
    current_columns = df.columns
    
    missing_columns = []
    for col in required_columns:
      if col not in current_columns:
        missing_columns.append(col)
    if missing_columns:
        logger.error(f"Validation thất bại! Thiếu các cột bắt buộc: {missing_columns}")
        return False
    logger.info("Validation Schema thành công: Đầy đủ các cột yêu cầu.")
    return True

def is_empty_dataframe(df: DataFrame) -> bool:
    if df.isEmpty():
        logger.warning("DataFrame rỗng! Không có dòng dữ liệu nào để xử lý.")
        return True
    return False
