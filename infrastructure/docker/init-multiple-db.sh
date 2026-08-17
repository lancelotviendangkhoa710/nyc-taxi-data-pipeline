#!/bin/bash
# Tạo multiple databases trong 1 PostgreSQL instance
set -e

function create_db() {
    local db=$1
    echo "Creating database: $db"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        SELECT 'CREATE DATABASE $db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$db')\gexec
EOSQL
}

# Tạo từng DB từ POSTGRES_MULTIPLE_DATABASES (comma-separated)
if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    for db in $(echo "$POSTGRES_MULTIPLE_DATABASES" | tr ',' ' '); do
        create_db "$db"
    done
fi
