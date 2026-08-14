# ✅ Docker Dockerization Complete - NYC Taxi Project

## 📋 Summary

Bạn đã hoàn thành Dockerization của NYC Taxi Project với đầy đủ giải thích chi tiết!

### 📁 Files Created

**1. Dockerfiles (2 files)**
- `infrastructure/docker/Dockerfile.spark` - Build image cho Spark ETL
- `infrastructure/docker/Dockerfile.dbt` - Build image cho dbt

**2. Entrypoint Scripts (2 files)**
- `infrastructure/docker/entrypoint-spark.sh` - Spark startup script (verify Java, DB, run ETL)
- `infrastructure/docker/entrypoint-dbt.sh` - dbt startup script (verify dbt, DB, run models)

**3. Docker Configuration (3 files)**
- `infrastructure/docker/.dockerignore` - Files NOT copied during build
- `infrastructure/docker/docker-compose.yml` - Supabase PostgreSQL (remote DB)
- `infrastructure/docker/docker-compose.local.yml` - Local PostgreSQL (for testing)

**4. Documentation (1 file)**
- `docs/DOCKER_SETUP_GUIDE.md` - Full guide with explanations

### 🎯 Key Points

**Dockerfile.spark giải thích:**
```
FROM python:3.12-slim
  → Base image 200MB (slim = nhỏ, không cần GUI)

apt-get update + openjdk-17-jdk-headless
  → Spark cần Java JDK

apt-get clean && rm -rf /var/lib/apt/lists/*
  → Xóa cache (~200MB saved per layer)

COPY requirements.txt /tmp/ + RUN pip install
  → Tách layer = Docker caches tốt hơn
  → requirements.txt thay đổi → rebuild pip layer
  → Code thay đổi → reuse pip layer (fast!)

curl | tar xz
  → Download + extract Spark direct (no disk I/O)

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
  → Auto-run script khi container start

HEALTHCHECK
  → Docker periodically check if Spark works
```

**docker-compose.yml giải thích:**
```
build: context: ../..
  → Project root directory

env_file: ../../.env
  → Load environment variables

${PG_HOST:-localhost}
  → Use $PG_HOST from .env, or default to localhost

volumes:
  ../../data:/app/data
    → Persistent storage (survives container restart)
  ../../spark:/app/spark:ro
    → Read-only (protect source code)

depends_on:
  spark-etl:
    condition: service_completed_successfully
    → Start dbt ONLY after Spark finishes successfully
```

### 🚀 How to Use

**1. Build images:**
```bash
cd infrastructure/docker

docker build -f Dockerfile.spark -t spark-etl:latest ../../.
docker build -f Dockerfile.dbt -t dbt-transformer:latest ../../.
```

**2. Run with Supabase (remote DB):**
```bash
docker-compose -f docker-compose.yml up
```

**3. Run with Local PostgreSQL (testing):**
```bash
docker-compose -f docker-compose.local.yml up
```

**4. View logs:**
```bash
docker-compose logs -f spark-etl
docker-compose logs -f dbt
```

**5. Stop:**
```bash
docker-compose down
```

### 🔍 Debugging Commands

```bash
# View all logs
docker-compose logs

# Follow specific service
docker-compose logs -f spark-etl

# Enter running container
docker-compose exec spark-etl bash

# Check environment variables
docker-compose exec spark-etl env | grep PG_

# Check DNS resolution
docker-compose exec spark-etl ping postgres

# Resource usage
docker stats

# List all containers
docker ps -a
```

### ❓ Common Issues & Solutions

**Cannot connect to PostgreSQL**
- Problem: PG_HOST=localhost doesn't work in Docker
- Solution: Use service name PG_HOST=postgres (Docker DNS)

**Out of Memory (Exit 137)**
- Solution 1: Increase Docker memory
- Solution 2: Reduce Spark memory in spark/config.py
- Solution 3: Rebuild with `docker build --no-cache`

**Port 5432 already in use**
- Solution: Use different port in docker-compose.local.yml
  ```yaml
  ports:
    - "15432:5432"  ← access via localhost:15432
  ```

### 📚 Tài Liệu Chi Tiết

Xem `docs/DOCKER_SETUP_GUIDE.md` để hiểu:
- Tại sao mỗi lệnh cần thiết
- Tại sao mỗi config được viết như vậy
- Cách Docker caching hoạt động
- Cách service DNS hoạt động
- Cách volumes mount hoạt động

### ✨ Architecture

```
Docker Network (nyc-taxi-net)
├── spark-etl container
│   └── Extract → Transform → Validate → Load (Spark)
│       ↓ (JDBC)
├── PostgreSQL (Supabase or Local)
│   └── Raw Data Storage
│       ↓
├── dbt container
│   └── Staging → Intermediate → Marts (dbt)
│       ↓
└── Analytics Ready Tables
    └── Metabase Dashboard (future)
```

### 🎓 Learning Outcomes

✅ Hiểu Docker concepts (images, containers, volumes, networks)
✅ Viết Dockerfile từ đầu (layer caching, size optimization)
✅ Viết docker-compose cho multiple services
✅ Hiểu service DNS trong Docker networks
✅ Debugging Docker containers
✅ Persistent storage với volumes
✅ Environment variables management

### 📝 Next Steps (Optional)

1. **Add Airflow** - Orchestrate Spark + dbt workflows
2. **Add Metabase** - Analytics dashboard
3. **CI/CD Integration** - GitHub Actions + Docker
4. **Production Deployment** - Kubernetes, ECS, etc.
5. **Multi-stage builds** - Optimize image size further

---

**Bạn đã hoàn thành! Bây giờ bạn có thể chạy toàn bộ pipeline bằng Docker! 🎉**
