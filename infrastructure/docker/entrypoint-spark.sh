#!/bin/bash
# ============================================================================
# Entrypoint script cho Spark ETL container
# ============================================================================
# Chạy khi container start - verify dependencies và chạy ETL jobs
# ============================================================================

set -e  # Exit nếu có error

echo "🚀 Starting Spark ETL Container..."

# Kiểm tra Java đã cài chưa
echo "✓ Checking Java..."
if ! command -v java &> /dev/null; then
    echo "❌ Java not found! Exiting..."
    exit 1
fi
java -version

# Kiểm tra Spark đã cài chưa
echo "✓ Checking Spark..."
if [ ! -d "$SPARK_HOME" ]; then
    echo "❌ Spark not found at $SPARK_HOME! Exiting..."
    exit 1
fi
echo "Spark version: $(ls $SPARK_HOME/jars/spark-core*.jar | head -1)"

# Kiểm tra Python packages
echo "✓ Checking Python packages..."
python -c "import pyspark; print('PySpark version:', pyspark.__version__)"

# Kiểm tra database connection (nếu có)
if [ ! -z "$PG_HOST" ]; then
    echo "✓ Checking PostgreSQL connection..."
    python -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='$PG_HOST',
        port='$PG_PORT',
        user='$PG_USER',
        password='$PG_PASSWORD',
        database='$PG_DATABASE'
    )
    print('✓ PostgreSQL connected!')
    conn.close()
except Exception as e:
    print('❌ PostgreSQL connection failed:', str(e))
    exit(1)
"
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
    echo "⚠️  No main.py found. Container running in idle mode."
    echo "To run Spark job: python /app/spark/etl/main.py"
    # Keep container running
    tail -f /dev/null
fi
