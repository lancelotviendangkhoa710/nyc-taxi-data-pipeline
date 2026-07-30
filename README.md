# Nền tảng Kỹ thuật Dữ liệu Taxi Vàng NYC

Một nền tảng kỹ thuật dữ liệu cấp sản xuất để phân tích dữ liệu chuyến đi của Taxi Vàng NYC bằng Apache Spark, dbt và PostgreSQL. Dự án này minh họa kiến trúc data lakehouse hiện đại với xử lý hàng loạt, chuyển đổi dữ liệu và bảng điều khiển thông minh kinh doanh.

## 🎯 Tổng quan dự án

Nền tảng này thu thập, xử lý và phân tích hàng triệu bản ghi chuyến đi taxi NYC để cung cấp thông tin chi tiết về:

- Xu hướng doanh thu và mô hình nhu cầu taxi
- Phân tích thời gian và khoảng cách chuyến đi
- Phân phối phương thức thanh toán
- Phân tích điểm nóng địa lý theo khu vực đón/trả khách
- Chỉ số hiệu suất của tài xế

**Công nghệ sử dụng:**

- **Thu thập dữ liệu**: Tệp Parquet NYC TLC
- **Xử lý**: Apache Spark (PySpark) với thực thi cục bộ
- **Lưu trữ**: PostgreSQL (Supabase hoặc tự lưu trữ)
- **Chuyển đổi**: dbt (data build tool)
- **Điều phối**: Apache Airflow
- **Trực quan hóa**: Metabase
- **Cơ sở hạ tầng**: Docker (triển khai container)

---

## 📊 Kiến trúc

### Đường ống luồng dữ liệu

```
Dữ liệu NYC TLC (Parquet)
    ↓
[Lớp thô] - data/raw/*.parquet
    ↓ (PySpark ETL)
[Lớp đã xử lý] - data/processed/*.parquet
    ↓ (PostgreSQL JDBC)
[Lớp kho dữ liệu] - PostgreSQL (Star Schema)
    ↓ (Chuyển đổi dbt)
[Lớp chuyển đổi] - Staging → Intermediate → Mart
    ↓
[Lớp trình bày] - Bảng điều khiển Metabase
```

### Luồng thực thi (Airflow DAG)

```
download_data
    ↓
run_spark_etl (làm sạch, xác thực, làm giàu)
    ↓
load_to_postgres (kho dữ liệu PostgreSQL)
    ↓
run_dbt_models (mô hình hóa chiều)
    ↓
refresh_dashboard (bảng điều khiển phân tích)
```

### Cấu trúc thư mục

```
.
├── data/
│   ├── raw/                 # Tệp Parquet NYC TLC chưa xử lý
│   └── processed/           # Tệp parquet đã làm sạch và xác thực
├── spark/
│   ├── config.py           # Cấu hình Spark
│   ├── utils/              # Hàm hỗ trợ
│   └── etl/
│       ├── main.py         # Điểm vào điều phối ETL
│       ├── pipeline.py     # Logic chuyển đổi cốt lõi
│       ├── load.py         # Tiện ích tải dữ liệu
│       └── load_warehouse.py  # Tải vào PostgreSQL
├── warehouse/
│   ├── credentials/        # Thông tin kết nối cơ sở dữ liệu
│   └── ddl/                # Định nghĩa lược đồ kho dữ liệu
│       ├── fact_trip.sql   # Bảng sự kiện chuyến đi
│       ├── dim_vendor.sql  # Chiều nhà cung cấp
│       ├── dim_time.sql    # Chiều thời gian
│       ├── dim_location.sql # Chiều địa điểm
│       ├── dim_payment.sql # Chiều thanh toán
│       └── dim_rate.sql    # Chiều mã giá cước
├── dbt/                     # Mô hình, kiểm thử, tài liệu dbt
├── airflow/
│   └── dags/               # Định nghĩa Airflow DAG
├── docker/                 # Cấu hình Docker Compose
├── docs/                   # Tài liệu dự án
└── .gitnexus/             # Chỉ mục thông minh mã nguồn GitNexus
```

---

## 📋 Tập dữ liệu

**Nguồn:** Bản ghi chuyến đi Taxi Vàng của Ủy ban Taxi và Limousine NYC (TLC)

**Các trường chính:**

- `VendorID`: Nhà cung cấp dịch vụ taxi (1 = Creative Mobile, 2 = VeriFone)
- `tpep_pickup_datetime / tpep_dropoff_datetime`: Dấu thời gian chuyến đi
- `passenger_count`: Số lượng hành khách
- `trip_distance`: Khoảng cách tính bằng dặm
- `RatecodeID`: Loại giá cước (Tiêu chuẩn, JFK, Newark, v.v.)
- `PULocationID / DOLocationID`: Định danh khu vực đón/trả khách
- `payment_type`: Phương thức thanh toán (Thẻ tín dụng, Tiền mặt, v.v.)
- `fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, congestion_surcharge`: Các thành phần giá cước
- `total_amount`: Tổng chi phí chuyến đi

**Cột dẫn xuất (Giai đoạn ETL):**

- `trip_duration_min`: Thời gian chuyến đi tính bằng phút
- `tip_ratio`: Tiền boa tính theo phần trăm giá cước cơ bản
- `pickup_date`: Khóa phân vùng ngày (YYYY-MM-DD)

---

## 🚀 Bắt đầu nhanh

### Điều kiện tiên quyết

- Python 3.8+
- Apache Spark 3.x
- PostgreSQL 12+ (hoặc tài khoản Supabase)
- Docker & Docker Compose (để triển khai container)
- dbt 1.5+
- Apache Airflow 2.x

### Thiết lập phát triển cục bộ

1. **Sao chép kho lưu trữ:**

   ```bash
   git clone https://github.com/lancelotviendangkhoa710/nyc-taxi-de-project.git
   cd nyc-taxi-de-project
   ```

2. **Cài đặt phụ thuộc Python:**

   ```bash
   pip install pyspark pandas numpy dbt-postgres apache-airflow psycopg2-binary
   ```

3. **Cấu hình thông tin PostgreSQL:**

   ```bash
   # Cập nhật tệp .env với chi tiết kết nối PostgreSQL
   export PG_HOST=your-supabase-host.supabase.co
   export PG_PORT=5432
   export PG_DATABASE=postgres
   export PG_USER=postgres
   export PG_PASSWORD=your-password
   ```

4. **Chạy đường ống ETL cục bộ:**

   ```bash
   python spark/etl/main.py
   ```

5. **Tải dữ liệu vào kho:**

   ```bash
   python spark/etl/load_warehouse.py
   ```

6. **Thực thi chuyển đổi dbt:**

   ```bash
   cd dbt
   dbt run
   dbt test
   ```

### Triển khai Docker

```bash
docker-compose -f docker/docker-compose.yml up -d
```

---

## 🔧 Cấu hình

### Lược đồ kho dữ liệu

**Thiết kế Star Schema của PostgreSQL:**

- **fact_trip**: Bảng sự kiện trung tâm với các chỉ số chuyến đi
- **dim_vendor**: Nhà cung cấp dịch vụ taxi
- **dim_time**: Chiều thời gian (giờ, ngày, tháng, quý, năm)
- **dim_location**: Các khu vực taxi NYC với địa lý
- **dim_payment**: Phương thức thanh toán
- **dim_rate**: Các danh mục mã giá cước

Xem `warehouse/ddl/` để biết các tệp định nghĩa lược đồ cơ sở dữ liệu.

---

## 📈 Thực thi đường ống

### Giai đoạn ETL 1: Thu thập & Làm sạch dữ liệu

**Đầu vào:** Tệp Parquet NYC TLC thô
**Xử lý:**

- Xác thực lược đồ
- Xử lý giá trị null
- Ép kiểu dữ liệu
- Phát hiện và xử lý ngoại lệ
- Chuẩn hóa dấu thời gian

**Đầu ra:** Tệp parquet đã làm sạch trong `data/processed/`

### Giai đoạn ETL 2: Tải kho dữ liệu

**Đầu vào:** Tệp parquet đã xử lý
**Xử lý:**

- Tạo bảng PostgreSQL qua Spark JDBC
- Tổng hợp bảng sự kiện
- Tra cứu bảng chiều
- Tạo khóa thay thế
- Cập nhật SCD Loại 1

**Đầu ra:** Các bảng star schema trong PostgreSQL

### Giai đoạn chuyển đổi 3: Mô hình dbt

**Lớp Staging:** Bí danh bảng thô và làm sạch cơ bản
**Lớp Intermediate:** Logic kinh doanh và tính toán
**Lớp Mart:** Các bảng phân tích cuối cùng và tổng hợp

```sql
-- Ví dụ: Doanh thu theo khu vực
SELECT 
    dl.zone,
    DATE(ft.pickup_date) as trip_date,
    COUNT(*) as total_trips,
    SUM(ft.total_amount) as total_revenue,
    AVG(ft.tip_amount) as avg_tip
FROM fact_trip ft
JOIN dim_location dl ON ft.pickup_location_key = dl.location_key
GROUP BY dl.zone, trip_date
```

---

## 📊 Phân tích chính

### Bảng điều khiển chỉ số kinh doanh (Metabase)

1. **Phân tích doanh thu**
   - Tổng doanh thu theo ngày/tháng/khu vực
   - Doanh thu theo phương thức thanh toán
   - Doanh thu trên mỗi khu vực taxi

2. **Phân tích chuyến đi**
   - Số lượng và tần suất chuyến đi
   - Khoảng cách chuyến đi trung bình
   - Thời gian chuyến đi trung bình
   - Giờ và khu vực cao điểm

3. **Hiệu suất tài xế**
   - Số chuyến đi theo nhà cung cấp
   - Phân phối phần trăm tiền boa
   - Thống kê số lượng hành khách

4. **Thông tin chi tiết địa lý**
   - Bản đồ nhiệt các khu vực đón/trả khách
   - Các tuyến đường phổ biến
   - Mô hình chuyến đi giữa các khu vực

---

## 🧪 Kiểm thử & Xác thực

### Kiểm thử dbt

```bash
cd dbt
dbt test  # Chạy tất cả kiểm thử
dbt test --select model_name  # Kiểm thử mô hình cụ thể
```

Các kiểm thử tích hợp:

- **unique**: Không có khóa chính trùng lặp
- **not_null**: Các trường bắt buộc đã được điền
- **relationships**: Ràng buộc khóa ngoại
- **accepted_values**: Xác thực enum

### Kiểm tra chất lượng dữ liệu

Spark ETL bao gồm:

- Xác thực số lượng hàng
- Phát hiện sai lệch lược đồ
- Ngưỡng phần trăm null
- Phát hiện trùng lặp

---

## 📚 Tài liệu

- **[Hướng dẫn kiến trúc](docs/architecture.md)** - Thiết kế hệ thống và luồng dữ liệu
- **[Từ điển dữ liệu](docs/data_dictionary.md)** - Định nghĩa trường và chuyển đổi
- **[Mô hình dữ liệu](docs/data_model.md)** - Star schema và thiết kế chiều

---

## 🛠️ Quy trình phát triển

### Thay đổi cục bộ

1. Sửa đổi mã Spark ETL trong `spark/etl/`
2. Kiểm thử cục bộ: `python spark/etl/main.py`
3. Cập nhật mô hình dbt trong `dbt/models/`
4. Chạy kiểm thử dbt: `cd dbt && dbt test`

### Chất lượng mã nguồn

Dự án này sử dụng GitNexus để thông minh hóa mã nguồn:

- Chạy phân tích tác động trước khi thay đổi: `gitnexus impact`
- Phát hiện những gì thay đổi ảnh hưởng đến: `gitnexus detect_changes`
- Khám phá mối quan hệ mã nguồn: `gitnexus query`

### Triển khai

```bash
git add .
git commit -m "feat: mô tả thay đổi"
git push origin main
```

Airflow sẽ tự động cập nhật các thay đổi DAG.

---

## 🐛 Khắc phục sự cố

### Vấn đề bộ nhớ Spark

```bash
export SPARK_LOCAL_IP=127.0.0.1
export SPARK_DRIVER_MEMORY=4g
export SPARK_EXECUTOR_MEMORY=4g
python spark/etl/main.py
```

---

## Phát triển theo đặc tả

Dự án này sử dụng [GitHub Spec Kit](https://github.com/github/spec-kit) để quản lý các đặc tả đường ống dữ liệu.

### Cài đặt

Đảm bảo `specify-cli` đã được cài đặt trong môi trường của bạn:

```bash
pip install specify-cli
```

### Sử dụng

- **Tạo/Sửa đặc tả**: Thêm hoặc sửa đổi các tệp YAML trong thư mục `specs/`.
- **Tạo mã nguồn**: Chạy tập lệnh tạo:

  ```bash
  ./scripts/generate-from-spec.sh
  ```

### Chính sách GitIgnore

Các tạo tác Spec Kit (`.specify/`, `specs/generated/`, `*.spec-cache`, `specify.log`) bị Git bỏ qua để tránh cam kết mã nguồn được tạo tự động.

## 📋 Lộ trình

- [ ] Đường ống phát trực tuyến thời gian thực (Kafka → Spark Streaming)
- [ ] Mô hình học máy (dự báo nhu cầu chuyến đi)
- [ ] Giám sát nâng cao (Great Expectations, Soda)
- [ ] Hỗ trợ đa đám mây (AWS Redshift, Azure Synapse)
- [ ] Lớp API (FastAPI cho các truy vấn phân tích)

---

## Tác giả

**Khoa Lancelot** - [GitHub](https://github.com/lancelotviendangkhoa710)
