from pyspark.sql import DataFrame
from spark.utils.logger import get_logger

logger = get_logger("spark.etl.validate")

def validate_schema(df: DataFrame, required_columns: list) -> bool:
    """
    Check if the input DataFrame contains all required columns.
    """
    current_columns = df.columns
    
    missing_columns = []
    for col in required_columns:
      if col not in current_columns:
        missing_columns.append(col)
    if missing_columns:
        logger.error(f"Validation failed! Missing required columns: {missing_columns}")
        return False
    logger.info("Schema validation successful: All required columns present.")
    return True

def is_empty_dataframe(df: DataFrame) -> bool:
    if df.isEmpty():
        logger.warning("Empty DataFrame detected! No records to process.")
        return True
    return False
