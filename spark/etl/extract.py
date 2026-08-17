from pyspark.sql import SparkSession, DataFrame
from spark.config import setup_java_env, SPARK_APP_NAME, SPARK_MASTER, SPARK_CONFIGS
from spark.utils.logger import get_logger
import os
logger = get_logger("spark.etl.extract")

def get_spark_session() -> SparkSession:
    import platform
    if platform.system() == "Windows":
        setup_java_env()

    spark = (
        SparkSession.builder
        .appName(SPARK_APP_NAME)
        .master(SPARK_MASTER)
        .config(map=SPARK_CONFIGS)
        .getOrCreate()
    )
    logger.info("SparkSession đã được khởi tạo thành công")
    return spark

def extract_data(spark: SparkSession, raw_dir_path: str, file_pattern: str) -> DataFrame:
  import os
  import glob
  from pyspark.sql.utils import AnalysisException
  
  full_path = os.path.join(raw_dir_path, file_pattern)
  logger.info(f"Đang tìm kiếm các file khớp với: {full_path}")
  
  try:
    resolved_paths = glob.glob(full_path)
    if not resolved_paths:
      logger.error(f"Không tìm thấy file nào khớp với: {full_path}")
      raise FileNotFoundError(f"Không tìm thấy file nào khớp với: {full_path}")
      
    logger.info(f"Tìm thấy các file: {resolved_paths}. Đang đọc dữ liệu...\n")

    df = spark.read.parquet(*resolved_paths)
    
    if len(df.columns) == 0:
      logger.warning(f"Cảnh báo: Dữ liệu đọc được từ {full_path} không có cột nào (file rỗng).\n")
      
    return df
    
  except AnalysisException as e:
    logger.error(f"Lỗi Spark SQL (đường dẫn không tồn tại hoặc file lỗi): {e}")
    raise e
  except Exception as e:
    logger.error(f"Lỗi không xác định khi trích xuất dữ liệu từ {full_path}: {e}")
    raise e


