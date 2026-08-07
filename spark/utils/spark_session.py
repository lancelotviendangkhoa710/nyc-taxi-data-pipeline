

import sys
import os

# Đảm bảo có thể import config dù chạy từ bất kỳ đâu
sys.path.insert(0, str(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from spark.config import (
    setup_java_env,
    SPARK_APP_NAME,
    SPARK_MASTER,
    SPARK_LOG_LEVEL,
    SPARK_CONFIGS,
)
from spark.utils.logger import get_logger

logger = get_logger(__name__)


def get_spark(app_name: str = SPARK_APP_NAME):
    """
    Tạo hoặc lấy SparkSession đã tồn tại.

    Args:
        app_name: Tên ứng dụng Spark.

    Returns:
        SparkSession: Session đã được cấu hình.

    Example:
        spark = get_spark()
        df = spark.read.parquet("data/raw/yellow_tripdata_2026-01.parquet")
    """
    # Bước 1: Setup Java và Hadoop (bắt buộc trên Windows)
    setup_java_env()

    from pyspark.sql import SparkSession

    logger.info(f"Initializing SparkSession: app_name='{app_name}', master='{SPARK_MASTER}'")

    builder = (
        SparkSession.builder
        .appName(app_name)
        .master(SPARK_MASTER)
    )

    # Áp dụng các cấu hình từ config.py
    for key, value in SPARK_CONFIGS.items():
        builder = builder.config(key, value)

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel(SPARK_LOG_LEVEL)

    logger.info(f"SparkSession created. Spark version: {spark.version}")
    return spark
