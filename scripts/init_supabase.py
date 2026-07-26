#!/usr/bin/env python3
"""
Initialize Supabase PostgreSQL database with DDL schemas.
Reads all SQL files from warehouse/ddl/postgres/ and executes them in order.
"""

import os
import sys
from pathlib import Path

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("Lỗi: Thư viện 'psycopg2' chưa được cài đặt hoặc bị chặn bởi hệ thống.")
    print("Vui lòng chạy: python -m pip install psycopg2-binary")
    sys.exit(1)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from spark.config import PG_HOST, PG_PORT, PG_DATABASE, PG_USER, PG_PASSWORD


def get_ddl_files():
    """Get all DDL files in order."""
    ddl_dir = Path(__file__).parent.parent / "warehouse" / "ddl" / "postgres"
    if not ddl_dir.exists():
        raise FileNotFoundError(f"DDL directory not found: {ddl_dir}")
    
    files = sorted(ddl_dir.glob("*.sql"))
    return files


def execute_ddl(connection, file_path):
    """Execute a single DDL file."""
    print(f"\nExecuting: {file_path.name}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        ddl_content = f.read()
    
    cursor = connection.cursor()
    try:
        cursor.execute(ddl_content)
        connection.commit()
        print(f"Success: {file_path.name}")
    except Exception as e:
        connection.rollback()
        print(f"Error in {file_path.name}: {e}")
        raise
    finally:
        cursor.close()


def init_database():
    """Initialize database with all DDL files."""
    print("=" * 60)
    print(" Initializing Supabase PostgreSQL Database")
    print("=" * 60)
    print(f"Host: {PG_HOST}")
    print(f"Database: {PG_DATABASE}")
    print(f"User: {PG_USER}")
    
    # Connect to database
    try:
        connection = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD
        )
        print("\nConnected to database")
    except psycopg2.OperationalError as e:
        print(f"\nConnection failed: {e}")
        return False
    
    try:
        # Get and execute all DDL files
        ddl_files = get_ddl_files()
        print(f"\nFound {len(ddl_files)} DDL files")
        
        for file_path in ddl_files:
            execute_ddl(connection, file_path)
        
        print("\n" + "=" * 60)
        print("✨ Database initialization completed successfully!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n Initialization failed: {e}")
        return False
    finally:
        connection.close()


def verify_tables():
    """Verify that all tables were created."""
    print("\n🔍 Verifying tables...")
    
    try:
        connection = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD
        )
        
        cursor = connection.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        expected_tables = [
            'dim_vendor', 'dim_payment', 'dim_rate', 
            'dim_location', 'dim_time', 'fact_trip'
        ]
        
        actual_tables = [t[0] for t in tables]
        print(f"\n📊 Tables found ({len(actual_tables)}):")
        for table in actual_tables:
            status = "✅" if table in expected_tables else "⚠️"
            print(f"  {status} {table}")
        
        missing = set(expected_tables) - set(actual_tables)
        if missing:
            print(f"\n⚠️  Missing tables: {missing}")
            return False
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


if __name__ == "__main__":
    success = init_database()
    
    if success:
        verify_ok = verify_tables()
        sys.exit(0 if verify_ok else 1)
    else:
        sys.exit(1)