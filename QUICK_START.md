# 🚀 Docker Quick Start - NYC Taxi Project

## 📋 Tổng Quan

Dự án này có 2 services chính:
- **Spark ETL**: Chạy ETL jobs (extract, transform, load data)
- **dbt**: Transform data thành models (sạch, organized)

Cả 2 chạy trong Docker containers, không cần cài trên máy.

---

## 🛠️ Cài Đặt

### 1. Chuẩn Bị (lần đầu tiên)

```bash
# Clone project (nếu chưa có)
git clone <your-repo> nyc_taxi_project
cd nyc_taxi_project

# Cài Docker Desktop nếu chưa có
# Download từ: https://www.docker.com/products/docker-desktop
```

### 2. Tạo `.env` file (config database)

```bash
# Tạo file .env ở project root
cat > .env << EOF
# PostgreSQL Config (dùng khi chạy local)
PG_HOST=postgres
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=your_password_here
PG_DATABASE=nyc_taxi

# Hoặc nếu dùng Supabase (remote)
# PG_HOST=your-supabase-host.supabase.co
# PG_PASSWORD=your-supabase-password
EOF
```

### 3. Build Docker images

```bash
cd infrastructure/docker

# Build Spark image
docker build -f Dockerfile.spark -t spark-etl:latest ../../.

# Build dbt image  
docker build -f Dockerfile.dbt -t dbt-transformer:latest ../../.

# Kiểm tra images được tạo chưa
docker images | grep -E "spark-etl|dbt-transformer"
```

---

## 🎯 Chạy Docker

### Option A: Chạy Spark ETL + dbt

```bash
cd infrastructure/docker

# Chạy docker-compose
docker-compose -f docker-compose.yml up

# Logs sẽ hiển thị real-time
# Press Ctrl+C để dừng
```

**Khi chạy:**
1. Spark ETL container khởi động
2. Kiểm tra Java, Spark, Python packages
3. Kiểm tra PostgreSQL connection
4. Chạy ETL job (`/app/spark/etl/main.py`)
5. Khi Spark xong, dbt container tự động chạy
6. dbt transform data

### Option B: Chạy chỉ Spark ETL (debug)

```bash
docker-compose -f docker-compose.yml up spark-etl

# Hoặc chạy interactive mode (vào container)
docker-compose -f docker-compose.yml run --rm spark-etl bash
```

---

## 📊 Debug & Monitoring

### Xem logs real-time

```bash
# Xem tất cả logs
docker-compose -f docker-compose.yml logs -f

# Xem chỉ Spark logs
docker-compose -f docker-compose.yml logs -f spark-etl

# Xem chỉ dbt logs
docker-compose -f docker-compose.yml logs -f dbt
```

### Vào container để debug

```bash
# Vào Spark container bash
docker-compose -f docker-compose.yml exec spark-etl bash

# Bên trong container, bạn có thể:
# - python /app/spark/etl/main.py     (chạy lại ETL)
# - python -c "import pyspark"        (test PySpark)
# - psql -h postgres -U postgres      (connect PostgreSQL)
```

### Kiểm tra running containers

```bash
# Xem containers đang chạy
docker ps

# Xem tất cả containers (kể cả dừng rồi)
docker ps -a

# Kiểm tra resource usage
docker stats
```

---

## 🛑 Dừng & Cleanup

```bash
# Dừng containers
docker-compose -f docker-compose.yml down

# Dừng + xóa volumes (⚠️ xóa data!)
docker-compose -f docker-compose.yml down -v

# Xóa tất cả Docker containers (⚠️ aggressive)
docker system prune -a
```

---

## ❌ Troubleshooting

### 1. Error: "docker: command not found"
```
❌ Docker không cài hoặc không trong PATH
✅ Giải: Cài Docker Desktop, restart terminal
```

### 2. Error: "Cannot connect to PostgreSQL"
```
❌ Database không chạy hoặc connection string sai
✅ Giải: Check .env file, Kiểm tra PG_HOST, PG_PASSWORD
```

### 3. Error: "Out of Memory"
```
❌ Docker không có đủ memory cho Spark
✅ Giải: Tăng Docker memory settings hoặc giảm Spark memory
```

### 4. Build image thất bại
```
❌ Dockerfile có lỗi hoặc requirements.txt sai
✅ Giải: Xem logs, kiểm tra requirements.txt tồn tại
```

### 5. Container exit ngay

```
❌ Entrypoint script failed
✅ Giải: docker logs spark-etl-container, vào bash debug
```

---

## 📁 File Structure

```
infrastructure/docker/
├── Dockerfile.spark            # Image cho Spark (có comments)
├── Dockerfile.dbt              # Image cho dbt
├── entrypoint-spark.sh         # Script chạy Spark start
├── docker-compose.yml          # Orchestrate containers
└── .dockerignore               # Files bỏ qua khi build
```

**Mỗi file có comments Tiếng Việt giải thích từng dòng!**

---

## 🎓 Học Thêm

### Docker là gì?

```
Image      = Blueprint (như class)
Container  = Instance chạy từ image
docker build = Tạo image từ Dockerfile
docker run   = Tạo + chạy container từ image
```

### Tại sao dùng Docker?

✅ **Isolate**: Services chạy riêng, không ảnh hưởng
✅ **Reproducible**: Chạy ở đâu cũng giống nhau
✅ **No setup**: Không cần cài Java, Spark trên máy
✅ **Easy cleanup**: `docker-compose down` là xong

---

## ✅ Checklist

- [ ] Docker Desktop cài đã
- [ ] `.env` file tạo rồi
- [ ] `docker build` chạy thành công
- [ ] `docker-compose up` chạy được
- [ ] Xem logs không có error
- [ ] Spark ETL chạy xong
- [ ] dbt chạy xong

---

**Happy Dockerizing! 🐳**

Logs: `docker-compose logs -f spark-etl`
