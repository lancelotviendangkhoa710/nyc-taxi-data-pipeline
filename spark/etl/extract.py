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
    logger.info("SparkSession initialized successfully")
    return spark

def extract_data(spark: SparkSession, raw_dir_path: str, file_pattern: str) -> DataFrame:
  import os
  import glob
  from pyspark.sql.utils import AnalysisException
  
  full_path = os.path.join(raw_dir_path, file_pattern)
  logger.info(f"Searching for raw files matching: {full_path}")
  
  try:
    resolved_paths = glob.glob(full_path)
    if not resolved_paths:
      logger.error(f"No files found matching pattern: {full_path}")
      raise FileNotFoundError(f"No files found matching pattern: {full_path}")
      
    logger.info(f"Found files: {resolved_paths}. Reading data...")

    df = spark.read.parquet(*resolved_paths)
    
    # Drop columns that do not carry statistical meaning for analysis
    cols_to_drop = ["improvement_surcharge", "mta_tax", "store_and_fwd_flag"]
    existing_drops = [c for c in cols_to_drop if c in df.columns]
    if existing_drops:
        logger.info(f"Dropping unnecessary columns from raw data: {existing_drops}")
        df = df.drop(*existing_drops)

    if len(df.columns) == 0:
      logger.warning(f"Warning: Data read from {full_path} contains 0 columns (empty file).")
      
    return df
    
  except AnalysisException as e:
    logger.error(f"Spark SQL error (path does not exist or file corrupt): {e}")
    raise e
  except Exception as e:
    logger.error(f"Unknown error extracting data from {full_path}: {e}")
    raise e



