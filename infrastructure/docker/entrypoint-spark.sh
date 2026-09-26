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
echo "Spark version: $(ls $SPARK_HOME/jars/spark-core*.jar 2>/dev/null | head -1 || python -c "import pyspark; print(pyspark.__version__)")"

# Kiểm tra Python packages
echo "Checking Python packages..."
python -c "import pyspark; print('PySpark version:', pyspark.__version__)"

# Kiểm tra AWS credentials (static key hoặc IMDS/IAM role)
echo "Checking AWS Credentials..."
if python -c "
import boto3, sys
try:
    sts = boto3.client('sts')
    identity = sts.get_caller_identity()
    print('AWS Credentials OK - ARN:', identity['Arn'])
except Exception as e:
    print('AWS Credentials not found:', e)
    sys.exit(1)
"; then
    :
else
    echo "AWS credentials unavailable. Exiting..."
    exit 1
fi

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
