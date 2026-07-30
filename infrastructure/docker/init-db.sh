#!/bin/bash
set -e

# Create extensions
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS uuid-ossp;
    CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
EOSQL

# Run all DDL files in order
for file in /docker-entrypoint-initdb.d/ddl/*.sql; do
    if [ -f "$file" ]; then
        echo "Executing $file"
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f "$file"
    fi
done

echo "Database initialization completed"