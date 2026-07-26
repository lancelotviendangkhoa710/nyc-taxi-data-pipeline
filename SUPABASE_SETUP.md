# Supabase Setup Guide - NYC Taxi Project

## Tại sao cần Supabase làm Data Warehouse?

1. **Managed PostgreSQL** — Không cần tự host, scale tự động, backup hàng ngày
2. **Star Schema DWH** — Lưu trữ fact_trip + 5 dimension tables sau Spark ETL
3. **Free tier** — 500MB storage, đủ cho demo/development
4. **API + Dashboard** — Xem data trực tiếp, kết nối BI tools (Metabase, Looker)
5. **Giảm chi phí** — So với Redshift/BigQuery, Supabase rẻ hơn cho dữ liệu vừa

## Tại sao không có trong checklist trước?

Checklist trước tập trung vào **pipeline ETL** (Extract → Transform → Validate → Load local). Supabase là **bước cuối cùng** — đích đến của `load_warehouse.py`. Nó không phải phát triển code mới, mà là **cấu hình hạ tầng**.

---

## Option 1: Setup LOCAL (Docker)

### Bước 1: Khởi động PostgreSQL với Docker
```bash
docker-compose -f docker/docker-compose.yml up -d
```

### Bước 2: Sao chép DDL PostgreSQL vào Docker
```bash
docker cp warehouse/ddl/postgres/. supabase-postgres:/docker-entrypoint-initdb.d/ddl/
docker-compose -f docker/docker-compose.yml restart postgres
```

### Bước 3: Xác nhận kết nối
```bash
psql -h localhost -U postgres -d postgres -c "\dt"
```

**Kết quả mong đợi:**
```
           List of relations
 Schema |      Name      | Type  | Owner
--------+----------------+-------+----------
 public | dim_location   | table | postgres
 public | dim_payment    | table | postgres
 public | dim_rate       | table | postgres
 public | dim_time       | table | postgres
 public | dim_vendor     | table | postgres
 public | fact_trip      | table | postgres
```

### Bước 4: Chạy Spark ETL để load dữ liệu
```bash
python spark/etl/load.py
```

---

## Option 2: Setup SUPABASE CLOUD

### Bước 1: Tạo Project Supabase
1. Vào  
2. Sign up hoặc Login
3. Click "New Project"
4. Chọn: 
   - Organization: Tạo mới hoặc chọn cái cũ
   - Project name: `nyc-taxi-dw`
   - Region: `Southeast Asia (Singapore)` (gần nhất)
   - Password: Ghi nhớ password

### Bước 2: Lấy Connection String
1. Vào **Settings → Database → Connection pooling**
2. Copy **Connection string** (PostgreSQL)
3. Format: `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`

### Bước 3: Cập nhật `.env`
```bash
PG_HOST=db.gjrilbelpdesjaqhsjlt.supabase.co
PG_PORT=5432
PG_DATABASE=postgres
PG_USER=postgres
PG_PASSWORD=your-supabase-password
```

### Bước 4: Chạy DDL trên Supabase
1. Vào Supabase Dashboard → **SQL Editor**
2. Click "New Query"
3. Copy nội dung từ `warehouse/ddl/postgres/01_dim_vendor.sql` → Paste → Run
4. Lặp lại cho 5 file khác (02 → 06)

**Hoặc chạy script tự động:**
```bash
python scripts/init_supabase.py
```

### Bước 5: Chạy Spark ETL
```bash
python spark/etl/load.py
```

---

## Kiểm tra kết nối

### From Python
```python
import psycopg2
from spark.config import PG_HOST, PG_PORT, PG_DATABASE, PG_USER, PG_PASSWORD

conn = psycopg2.connect(
    host=PG_HOST,
    port=PG_PORT,
    database=PG_DATABASE,
    user=PG_USER,
    password=PG_PASSWORD
)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM fact_trip;")
print(cursor.fetchone())
conn.close()
```

### From CLI (psql)
```bash
psql -h $PG_HOST -U $PG_USER -d $PG_DATABASE -c "SELECT COUNT(*) FROM fact_trip;"
```

---

## File Structure

```
warehouse/
├── ddl/
│   ├── postgres/          ← PostgreSQL-compatible DDL
│   │   ├── 01_dim_vendor.sql
│   │   ├── 02_dim_payment.sql
│   │   ├── 03_dim_rate.sql
│   │   ├── 04_dim_location.sql
│   │   ├── 05_dim_time.sql
│   │   └── 06_fact_trip.sql
│   └── (originals in BigQuery syntax)

docker/
├── docker-compose.yml     ← Local PostgreSQL setup
└── init-db.sh            ← Auto-init DDL on startup
```

---

## Troubleshooting

### Lỗi: "FATAL: password authentication failed"
- Kiểm tra `.env` — password phải khớp với Supabase/Docker settings
- Supabase: Copy từ Dashboard → Settings → Database → Connection pooling

### Lỗi: "relation does not exist"
- Đảm bảo chạy DDL trong đúng thứ tự (01 → 06)
- fact_trip có FOREIGN KEY → cần dim_* chạy trước

### Slow upload?
- Spark: Tăng `spark.driver.memory` trong `spark/config.py`
- Postgres: Disable FK checks tạm thời (dev only):
  ```sql
  ALTER TABLE fact_trip DISABLE TRIGGER ALL;
  -- Load data
  ALTER TABLE fact_trip ENABLE TRIGGER ALL;
  ```

---

## Next Steps

1. ✅ Chọn setup (LOCAL hoặc CLOUD)
2. ✅ Cấu hình `.env`
3. ✅ Tạo tables trên DB
4. ✅ Chạy `python spark/etl/load.py`
5. ⏭️ Setup Airflow để orchestrate pipeline
6. ⏭️ Tạo Metabase dashboard để visualize