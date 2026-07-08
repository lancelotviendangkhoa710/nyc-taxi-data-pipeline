# Schema Report — NYC Yellow Taxi (January 2026)

Tài liệu này báo cáo cấu trúc schema thực tế của tập dữ liệu `yellow_tripdata_2026-01.parquet` sau khi import vào PySpark.

---

## 1. Thông Tin Chung
*   **Tổng số dòng (Rows):** 3,724,889
*   **Tổng số cột (Columns):** 20
*   **Kích thước tệp tin:** ~63 MB (định dạng Parquet nén)

---

## 2. Chi Tiết Schema Thực Tế (PySpark printSchema)

```
root
 |-- VendorID: integer (nullable = true)
 |-- tpep_pickup_datetime: timestamp_ntz (nullable = true)
 |-- tpep_dropoff_datetime: timestamp_ntz (nullable = true)
 |-- passenger_count: long (nullable = true)
 |-- trip_distance: double (nullable = true)
 |-- RatecodeID: long (nullable = true)
 |-- store_and_fwd_flag: string (nullable = true)
 |-- PULocationID: integer (nullable = true)
 |-- DOLocationID: integer (nullable = true)
 |-- payment_type: long (nullable = true)
 |-- fare_amount: double (nullable = true)
 |-- extra: double (nullable = true)
 |-- mta_tax: double (nullable = true)
 |-- tip_amount: double (nullable = true)
 |-- tolls_amount: double (nullable = true)
 |-- improvement_surcharge: double (nullable = true)
 |-- total_amount: double (nullable = true)
 |-- congestion_surcharge: double (nullable = true)
 |-- Airport_fee: double (nullable = true)
 |-- cbd_congestion_fee: double (nullable = true)
```

> [!NOTE]
> Kiểu dữ liệu thời gian trong Parquet được nhận diện là `timestamp_ntz` (Timestamp No Timezone) trong PySpark, phù hợp cho việc phân tích không phụ thuộc vào múi giờ địa phương trên máy chủ chạy Spark.

---

## 3. Nhận Xét Quan Trọng về Cấu Trúc
1.  **Dữ liệu khuyết thiếu đồng bộ (29.21%):** 
    Có 5 cột có tỷ lệ Null giống hệt nhau là `passenger_count`, `RatecodeID`, `store_and_fwd_flag`, `congestion_surcharge`, và `Airport_fee`. Điều này cho thấy khoảng 1.08 triệu dòng dữ liệu bị thiếu thông tin ghi nhận từ thiết bị của nhà cung cấp đối với các trường này.
2.  **Cột Phân Loại dạng Số:** 
    Các trường phân loại như `VendorID`, `RatecodeID`, và `payment_type` được lưu trữ dưới dạng số (`integer`/`long`). Chúng ta cần map các mã số này sang tên danh mục tương ứng khi đưa vào Warehouse hoặc dbt layer.
