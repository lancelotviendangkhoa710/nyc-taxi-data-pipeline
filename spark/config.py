import os
import platform as _platform
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# 1. ROOT DIRECTORY
# ─────────────────────────────────────────
# Tự động detect root dự án (thư mục chứa file config.py)
ROOT_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────
# 2. DATA PATHS
# ─────────────────────────────────────────
DATA_DIR       = ROOT_DIR / "data"
RAW_DIR        = DATA_DIR / "raw/yellow"
PROCESSED_DIR  = DATA_DIR / "processed"

# ─────────────────────────────────────────
# 3. JAVA & HADOOP (Windows)
# ─────────────────────────────────────────
JAVA_HOME    = r"C:\Program Files\Eclipse Adoptium\jdk-21.0.11.10-hotspot"
HADOOP_HOME  = str(ROOT_DIR / "infrastructure" / "hadoop")

def setup_java_env():
    """
    Cấu hình biến môi trường Java/Hadoop cho Spark trên Windows.
    """
    os.environ["JAVA_HOME"]   = JAVA_HOME
    os.environ["HADOOP_HOME"] = HADOOP_HOME
    java_bin    = os.path.join(JAVA_HOME, "bin")
    hadoop_bin  = os.path.join(HADOOP_HOME, "bin")
    current_path = os.environ.get("PATH", "")
    if java_bin not in current_path:
        os.environ["PATH"] = current_path + os.pathsep + java_bin
    if hadoop_bin not in current_path:
        os.environ["PATH"] = os.environ["PATH"] + os.pathsep + hadoop_bin

# ─────────────────────────────────────────
# 4. SPARK CONFIGURATION
# ─────────────────────────────────────────
SPARK_APP_NAME   = "nyc-taxi"
SPARK_MASTER     = "local[*]"
SPARK_LOG_LEVEL  = "WARN"

# PostgreSQL JDBC: Docker đã baked JAR vào image; Windows dùng packages để auto-download
if _platform.system() == "Windows":
    _pg_jdbc = {"spark.jars.packages": "org.postgresql:postgresql:42.7.1"}
else:
    _pg_jdbc = {"spark.jars": "/opt/spark/jars/postgresql-42.7.1.jar"}

SPARK_CONFIGS = {
    "spark.sql.shuffle.partitions": "8",
    "spark.sql.adaptive.advisoryPartitionSizeInBytes": str(
        int(
            os.getenv(
                "ETL_TARGET_FILE_SIZE_MB",
                "512" if os.getenv("ETL_PARTITION_PROFILE", "standard").lower() == "heavy" else "256",
            )
        ) * 1024 * 1024
    ),
    "spark.driver.memory": "4g",
    "spark.sql.adaptive.enabled": "true",
    **_pg_jdbc,
}

# ─────────────────────────────────────────
# 5. POSTGRESQL WAREHOUSE CONFIGURATION
# ─────────────────────────────────────────
PG_HOST     = os.getenv("PG_HOST", "localhost")
PG_PORT     = os.getenv("PG_PORT", "5432")
PG_DATABASE = os.getenv("PG_DATABASE", "nyc_taxi_dw")
PG_USER     = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "Tmo2159@@##")

PG_JDBC_URL = f"jdbc:postgresql://{PG_HOST}:{PG_PORT}/{PG_DATABASE}"

# ─────────────────────────────────────────
# 6. FILE PATTERNS
# ─────────────────────────────────────────
# Tên file parquet theo tháng: yellow_tripdata_YYYY-MM.parquet
YELLOW_TAXI_PATTERN  = "yellow_tripdata_*.parquet"

# ─────────────────────────────────────────
# 7. ETL SETTINGS
# ─────────────────────────────────────────
# Số partitions khi ghi ra file
ETL_PARTITION_PROFILE = os.getenv("ETL_PARTITION_PROFILE", "standard").lower()
_DEFAULT_TARGET_FILE_SIZE_MB = 512 if ETL_PARTITION_PROFILE == "heavy" else 256
TARGET_FILE_SIZE_BYTES = int(
    os.getenv("ETL_TARGET_FILE_SIZE_MB", str(_DEFAULT_TARGET_FILE_SIZE_MB))
) * 1024 * 1024
MIN_WRITE_PARTITIONS = int(os.getenv("ETL_MIN_WRITE_PARTITIONS", "1"))
MAX_WRITE_PARTITIONS = int(os.getenv("ETL_MAX_WRITE_PARTITIONS", "2000"))

# Columns được giữ lại sau ETL
SELECTED_COLUMNS = [
    "VendorID",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "RatecodeID",
    "store_and_fwd_flag",
    "PULocationID",
    "DOLocationID",
    "payment_type",
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "total_amount",
    "congestion_surcharge",
    "Airport_fee",
    "cbd_congestion_fee",
    # Derived columns (thêm vào bởi ETL)
    "trip_duration_min",
    "tip_ratio",
    "pickup_date",
]
