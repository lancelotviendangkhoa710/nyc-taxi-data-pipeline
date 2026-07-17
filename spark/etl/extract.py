from pyspark.sql import SparkSession, DataFrame
from spark.config import setup_java_env, SPARK_APP_NAME, SPARK_MASTER, SPARK_CONFIGS
from spark.utils.logger import get_logger

logger = get_logger("spark.etl.extract")

def get_spark_session() -> SparkSession:
    """
    Khởi tạo hoặc lấy SparkSession hiện tại.
    
    Tại sao phải cần hàm này?
    - SparkSession là điểm khởi đầu (Entry Point) của mọi ứng dụng Spark. Không có nó, bạn không thể
      tương tác với PySpark, không thể tạo DataFrame hay chạy câu lệnh SQL.
    - Hàm sử dụng mẫu `builder.getOrCreate()`. Ý nghĩa là nếu đã có một SparkSession đang chạy,
      nó sẽ reuse session cũ thay vì khởi tạo mới (rất quan trọng để tối ưu tài nguyên).
    - Lưu ý: Trên Windows, ta cần chạy setup_java_env() từ file config trước khi init Spark.
    """
    # 1. Thiết lập biến môi trường Java/Hadoop cho Windows
    setup_java_env()
    
    # 2. Xây dựng SparkSession sử dụng builder

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
    # Resolve wildcards in Python first to avoid Hadoop's globPath NativeIO error on Windows
    resolved_paths = glob.glob(full_path)
    if not resolved_paths:
      logger.error(f"Không tìm thấy file nào khớp với: {full_path}")
      raise FileNotFoundError(f"Không tìm thấy file nào khớp với: {full_path}")
      
    logger.info(f"Tìm thấy các file: {resolved_paths}. Đang đọc dữ liệu...")
    df = spark.read.parquet(*resolved_paths)
    
    # Một số trường hợp file tồn tại nhưng rỗng hoàn toàn (0 bytes) hoặc không có cột nào,
    # Spark vẫn đọc được nhưng DataFrame không có schema hoặc trống trơn.
    if len(df.columns) == 0:
      logger.warning(f"Cảnh báo: Dữ liệu đọc được từ {full_path} không có cột nào (file rỗng).")
      
    return df
    
  except AnalysisException as e:
    # Lỗi thường gặp nhất: Sai đường dẫn, file không tồn tại, hoặc pattern không khớp file nào
    logger.error(f"Lỗi Spark SQL (đường dẫn không tồn tại hoặc file lỗi): {e}")
    raise e
  except Exception as e:
    # Lỗi phần cứng, quyền truy cập file, hoặc định dạng parquet bị lỗi (corrupted)
    logger.error(f"Lỗi không xác định khi trích xuất dữ liệu từ {full_path}: {e}")
    raise e


