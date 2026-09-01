# Mô hình dữ liệu — Star Schema Taxi NYC

## Loại lược đồ: Star Schema

```
                    DIM_TIME
                        │
          DIM_VENDOR ───┤
                        │
         DIM_LOCATION ──┼──── FACT_TRIP
                        │
          DIM_PAYMENT ───┤
                        │
             DIM_RATE ───┘
```

---

## FACT_TRIP

Bảng sự kiện trung tâm, mỗi hàng = 1 chuyến đi.

| Cột | Kiểu dữ liệu | Cột nguồn | Mô tả |
| --- | --- | --- | --- |
| `trip_id` | BIGINT PK | _(tạo tự động)_ | Khóa thay thế |
| `vendor_key` | INT FK | `VendorID` | FK → DIM_VENDOR |
| `pickup_time_key` | INT FK | `tpep_pickup_datetime` | FK → DIM_TIME |
| `dropoff_time_key` | INT FK | `tpep_dropoff_datetime` | FK → DIM_TIME |
| `pickup_location_key` | INT FK | `PULocationID` | FK → DIM_LOCATION |
| `dropoff_location_key` | INT FK | `DOLocationID` | FK → DIM_LOCATION |
| `payment_key` | INT FK | `payment_type` | FK → DIM_PAYMENT |
| `rate_key` | INT FK | `RatecodeID` | FK → DIM_RATE |
| `passenger_count` | INT | `passenger_count` | Số hành khách |
| `trip_distance` | FLOAT | `trip_distance` | Khoảng cách (dặm) |
| `trip_duration_min` | FLOAT | _(dẫn xuất)_ | Thời gian chuyến đi (phút) |
| `fare_amount` | FLOAT | `fare_amount` | Giá cơ bản |
| `extra` | FLOAT | `extra` | Phụ phí |
| `tip_amount` | FLOAT | `tip_amount` | Tiền tip |
| `tip_ratio` | FLOAT | _(dẫn xuất)_ | tip / fare |
| `tolls_amount` | FLOAT | `tolls_amount` | Phí cầu đường |
| `congestion_surcharge` | FLOAT | `congestion_surcharge` | Phụ phí tắc đường |
| `airport_fee` | FLOAT | `Airport_fee` | Phí sân bay |
| `cbd_congestion_fee` | FLOAT | `cbd_congestion_fee` | Phí tắc đường CBD |
| `total_amount` | FLOAT | `total_amount` | Tổng tiền |
| `pickup_date` | DATE | _(dẫn xuất)_ | Ngày đón khách |

---

## DIM_TIME

| Cột | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `time_key` | INT PK | Khóa thay thế |
| `datetime` | TIMESTAMP | Dấu thời gian gốc |
| `date` | DATE | Ngày |
| `year` | INT | Năm |
| `month` | INT | Tháng (1-12) |
| `month_name` | VARCHAR | Tên tháng |
| `day` | INT | Ngày trong tháng |
| `day_of_week` | INT | Thứ (0=Thứ 2, 6=Chủ nhật) |
| `day_name` | VARCHAR | Tên thứ |
| `hour` | INT | Giờ (0-23) |
| `is_weekend` | BOOLEAN | Cuối tuần? |
| `is_peak_hour` | BOOLEAN | Giờ cao điểm? |
| `quarter` | INT | Quý (1-4) |

---

## DIM_LOCATION

| Cột | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `location_key` | INT PK | LocationID gốc từ TLC |
| `zone` | VARCHAR | Tên zone |
| `borough` | VARCHAR | Quận (Manhattan, Brooklyn,...) |
| `service_zone` | VARCHAR | Khu vực dịch vụ |

---

## DIM_VENDOR

| Cột | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `vendor_key` | INT PK | VendorID gốc |
| `vendor_name` | VARCHAR | Tên công ty |

Ánh xạ hiện tại:

- `1` = Creative Mobile Technologies (CMT)
- `2` = Curb Mobility (VeriFone)

---

## DIM_PAYMENT

| Cột | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `payment_key` | INT PK | payment_type gốc |
| `payment_name` | VARCHAR | Tên phương thức |

Ánh xạ hiện tại:

- `1` = Thẻ tín dụng
- `2` = Tiền mặt
- `3` = Không tính phí
- `4` = Tranh chấp
- `0` = Không xác định

---

## DIM_RATE

| Cột | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `rate_key` | INT PK | RatecodeID gốc |
| `rate_name` | VARCHAR | Tên loại giá |

Ánh xạ hiện tại:

- `1` = Giá tiêu chuẩn
- `2` = JFK
- `3` = Newark
- `4` = Nassau/Westchester
- `5` = Giá thỏa thuận
- `6` = Chuyến đi nhóm

---

## Cột dẫn xuất (tính toán trong ETL)

| Cột | Công thức |
| --- | --- |
| `trip_duration_min` | `(dropoff_ts - pickup_ts) / 60` |
| `tip_ratio` | `tip_amount / fare_amount` |
| `pickup_date` | `to_date(tpep_pickup_datetime)` |

---

## Ghi chú

- Tệp nguồn: `data/raw/yellow_tripdata_*.parquet`
- Số hàng mỗi tháng: ~3.7 triệu (ví dụ: tháng 1/2026)
- Nguồn cột: 20 cột
- Sau ETL: ~24+ cột (có thêm các cột dẫn xuất)
