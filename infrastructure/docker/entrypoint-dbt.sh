#!/bin/bash
# ============================================================================
# Entrypoint script cho dbt container
# ============================================================================
# Chạy khi container start - verify dbt và chạy transformations
# ============================================================================

set -e  # Exit nếu có error

echo "🚀 Starting dbt Container..."

# Kiểm tra dbt đã cài chưa
echo "✓ Checking dbt..."
if ! command -v dbt &> /dev/null; then
    echo "❌ dbt not found! Exiting..."
    exit 1
fi
dbt --version

# Kiểm tra PostgreSQL client
echo "✓ Checking PostgreSQL client..."
if ! command -v psql &> /dev/null; then
    echo "❌ psql not found! Exiting..."
    exit 1
fi

# Kiểm tra dbt project tồn tại
echo "✓ Checking dbt project..."
if [ ! -f "/app/dbt/dbt_project.yml" ]; then
    echo "❌ dbt_project.yml not found at /app/dbt/! Exiting..."
    exit 1
fi

# Kiểm tra database connection
echo "✓ Checking PostgreSQL connection..."
if ! psql_error=$(PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -U "$PG_USER" -d "$PG_DATABASE" -c "SELECT 1" 2>&1); then
    echo "❌ PostgreSQL connection failed!"
    echo "  Host: $PG_HOST"
    echo "  User: $PG_USER"
    echo "  Database: $PG_DATABASE"
    echo "  Detail: $psql_error"
    exit 1
fi
echo "✓ PostgreSQL connected!"

# Chạy dbt commands
echo ""
echo "✓ All checks passed! Running dbt..."
echo "============================================================================"

cd /app/dbt

# dbt debug: Test dbt config và database connection
echo "Running: dbt debug"
dbt debug || exit 1

# dbt deps: Cài dbt packages (nếu có packages.yml)
echo ""
echo "Running: dbt deps"
dbt deps || exit 1

# dbt run: Chạy transformations (tạo models)
echo ""
echo "Running: dbt run"
dbt run || exit 1

# dbt test: Chạy data quality tests
echo ""
echo "Running: dbt test"
dbt test || exit 1

# dbt docs generate: Tạo documentation (optional)
echo ""
echo "Running: dbt docs generate"
dbt docs generate || true

echo ""
echo "✓ dbt finished successfully!"
echo "============================================================================"
