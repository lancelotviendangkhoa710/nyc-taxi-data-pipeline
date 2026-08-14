# 🐳 Docker Setup Guide

## 1. Dockerfile.spark
File: `infrastructure/docker/Dockerfile.spark`

```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y openjdk-17-jdk-headless curl wget && apt-get clean && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 SPARK_HOME=/opt/spark PATH=$PATH:$JAVA_HOME/bin:$SPARK_HOME/bin PYTHONUNBUFFERED=1
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt
RUN curl -fsSL https://archive.apache.org/dist/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz | tar xz -C /opt && mv /opt/spark-3.5.0-bin-hadoop3 /opt/spark && rm -rf /opt/spark/examples /opt/spark/data
WORKDIR /app
COPY spark/ /app/spark/
COPY .env /app/.env
COPY infrastructure/docker/entrypoint-spark.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD python -c "import pyspark; print('OK')" || exit 1
```

## 2. Dockerfile.dbt
File: `infrastructure/docker/Dockerfile.dbt`

```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y git && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir dbt-postgres==1.7.0 python-dotenv
WORKDIR /app
COPY dbt/ /app/dbt/
COPY .env /app/.env
COPY infrastructure/docker/entrypoint-dbt.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD python -c "import dbt; print('OK')" || exit 1
```

## 3. entrypoint-spark.sh
File: `infrastructure/docker/entrypoint-spark.sh`

```bash
#!/bin/bash
set -e
java -version 2>&1 || { echo "❌ Java missing"; exit 1; }
python3 << 'EOF'
import os, psycopg2
from dotenv import load_dotenv
load_dotenv()
try:
    conn = psycopg2.connect(host=os.getenv("PG_HOST"), port=int(os.getenv("PG_PORT", 5432)), user=os.getenv("PG_USER"), password=os.getenv("PG_PASSWORD"), database=os.getenv("PG_DATABASE"))
    conn.close()
except Exception as e:
    print(f"❌ DB: {e}")
    exit(1)
EOF
cd /app && python3 -m spark.etl.run_pipeline
```

## 4. entrypoint-dbt.sh
File: `infrastructure/docker/entrypoint-dbt.sh`

```bash
#!/bin/bash
set -e
dbt --version 2>&1 || { echo "❌ dbt missing"; exit 1; }
python3 << 'EOF'
import os, psycopg2
from dotenv import load_dotenv
load_dotenv()
try:
    conn = psycopg2.connect(host=os.getenv("PG_HOST"), port=int(os.getenv("PG_PORT", 5432)), user=os.getenv("PG_USER"), password=os.getenv("PG_PASSWORD"), database=os.getenv("PG_DATABASE"))
    conn.close()
except Exception as e:
    print(f"❌ DB: {e}")
    exit(1)
EOF
cd /app/dbt && dbt deps && dbt run && dbt test && dbt docs generate
```

## 5. .dockerignore
File: `infrastructure/docker/.dockerignore`

```
__pycache__ *.pyc *.egg-info .venv venv/ .git .DS_Store logs/ *.log data/raw data/processed tests/ .cache tmp/
```

## 6. docker-compose.yml
File: `infrastructure/docker/docker-compose.yml`

```yaml
version: '3.8'
services:
  spark-etl:
    build: {context: ../.. , dockerfile: infrastructure/docker/Dockerfile.spark}
    container_name: spark-etl-container
    env_file: [../../.env]
    environment: {PG_HOST: '${PG_HOST:-localhost}', PG_PORT: '${PG_PORT:-5432}', PG_USER: '${PG_USER:-postgres}', PG_PASSWORD: '${PG_PASSWORD}', PG_DATABASE: '${PG_DATABASE:-postgres}'}
    volumes: [../../data:/app/data, ../../spark:/app/spark:ro]
    networks: [nyc-taxi-net]
    restart: "no"

  dbt:
    build: {context: ../.. , dockerfile: infrastructure/docker/Dockerfile.dbt}
    container_name: dbt-transformer-container
    env_file: [../../.env]
    environment: {PG_HOST: '${PG_HOST:-localhost}', PG_PORT: '${PG_PORT:-5432}', PG_USER: '${PG_USER:-postgres}', PG_PASSWORD: '${PG_PASSWORD}', PG_DATABASE: '${PG_DATABASE:-postgres}'}
    volumes: [../../dbt:/app/dbt]
    networks: [nyc-taxi-net]
    restart: "no"
    depends_on:
      spark-etl:
        condition: service_completed_successfully

networks:
  nyc-taxi-net:
    driver: bridge
```

## 7. docker-compose.local.yml
File: `infrastructure/docker/docker-compose.local.yml`

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:16-alpine
    container_name: postgres-local
    environment: {POSTGRES_DB: nyc_taxi, POSTGRES_USER: postgres, POSTGRES_PASSWORD: '${PG_PASSWORD:-postgres}'}
    ports: ["5432:5432"]
    volumes: [postgres_data:/var/lib/postgresql/data]
    healthcheck: {test: ["CMD-SHELL", "pg_isready -U postgres"], interval: 10s, timeout: 5s, retries: 5}
    networks: [nyc-taxi-net]
    restart: unless-stopped

  spark-etl:
    build: {context: ../.. , dockerfile: infrastructure/docker/Dockerfile.spark}
    container_name: spark-etl-container
    env_file: [../../.env]
    environment: {PG_HOST: postgres, PG_PORT: '5432', PG_USER: postgres, PG_PASSWORD: '${PG_PASSWORD:-postgres}', PG_DATABASE: nyc_taxi}
    volumes: [../../data:/app/data, ../../spark:/app/spark:ro]
    networks: [nyc-taxi-net]
    depends_on: {postgres: {condition: service_healthy}}

  dbt:
    build: {context: ../.. , dockerfile: infrastructure/docker/Dockerfile.dbt}
    container_name: dbt-transformer-container
    env_file: [../../.env]
    environment: {PG_HOST: postgres, PG_PORT: '5432', PG_USER: postgres, PG_PASSWORD: '${PG_PASSWORD:-postgres}', PG_DATABASE: nyc_taxi}
    volumes: [../../dbt:/app/dbt]
    networks: [nyc-taxi-net]
    depends_on: {spark-etl: {condition: service_completed_successfully}}

volumes: {postgres_data: {}}
networks: {nyc-taxi-net: {driver: bridge}}
```

## Run Commands

```bash
cd infrastructure/docker
docker build -f Dockerfile.spark -t spark-etl:latest ../../.
docker build -f Dockerfile.dbt -t dbt-transformer:latest ../../.
docker-compose -f docker-compose.yml up
docker-compose -f docker-compose.local.yml up
docker-compose logs -f spark-etl
docker-compose down
```

✅ Copy 7 files above into your project!
