#!/bin/bash


set -e  # Exit nếu có error

echo " Starting Spark ETL Container..."

# Kiểm tra Java đã cài chưa
echo "✓ Checking Java..."
if ! command -v java &> /dev/null; then
    echo "Java not found! Exiting..."
    exit 1
fi
java -version

# Kiểm tra Spark đã cài chưa
echo "✓ Checking Spark..."
if [ ! -d "$SPARK_HOME" ]; then
    echo "Spark not found at $SPARK_HOME! Exiting..."
    exit 1
fi
echo "Spark version: $(ls $SPARK_HOME/jars/spark-core*.jar | head -1)"

# Kiểm tra Python packages
echo "Checking Python packages..."
python -c "import pyspark; print('PySpark version:', pyspark.__version__)"

# Kiểm tra GCP credentials
echo "✓ Checking GCP Credentials..."
if [ ! -f "/app/gcp_service_account.json" ]; then
    echo "❌ GCP Service Account key not found at /app/gcp_service_account.json! Exiting..."
    exit 1
fi
echo "✓ GCP Credentials found!"

# Chạy Spark ETL job (nếu có main script)

echo ""
echo "✓ All checks passed! Running Spark ETL..."
echo "============================================================================"

# Kiểm tra xem có spark/etl/main.py không
if [ -f "/app/spark/etl/main.py" ]; then
    echo "Running /app/spark/etl/main.py..."
    python /app/spark/etl/main.py
else
    echo "No main.py found. Container running in idle mode."
    echo "To run Spark job: python /app/spark/etl/main.py"
    # Keep container running
    tail -f /dev/null
fi
