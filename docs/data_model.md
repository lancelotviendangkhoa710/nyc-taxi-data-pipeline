# Data Model — NYC Taxi Star Schema

## Schema Type: Star Schema

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

Bảng sự kiện trung tâm, mỗi row = 1 chuyến đi.

| Column | Type | Source Column | Mô tả |
|---|---|---|---|
| `trip_id` | BIGINT PK | _(generated)_ | Surrogate key |
| `vendor_key` | INT FK | `VendorID` | FK → DIM_VENDOR |
| `pickup_time_key` | INT FK | `tpep_pickup_datetime` | FK → DIM_TIME |
| `dropoff_time_key` | INT FK | `tpep_dropoff_datetime` | FK → DIM_TIME |
| `pickup_location_key` | INT FK | `PULocationID` | FK → DIM_LOCATION |
| `dropoff_location_key` | INT FK | `DOLocationID` | FK → DIM_LOCATION |
| `payment_key` | INT FK | `payment_type` | FK → DIM_PAYMENT |
| `rate_key` | INT FK | `RatecodeID` | FK → DIM_RATE |
| `passenger_count` | INT | `passenger_count` | Số hành khách |
| `trip_distance` | FLOAT | `trip_distance` | Khoảng cách (miles) |
| `trip_duration_min` | FLOAT | _(derived)_ | Thời gian chuyến đi (phút) |
| `fare_amount` | FLOAT | `fare_amount` | Giá cơ bản |
| `extra` | FLOAT | `extra` | Phụ phí |
| `mta_tax` | FLOAT | `mta_tax` | Thuế MTA |
| `tip_amount` | FLOAT | `tip_amount` | Tiền tip |
| `tip_ratio` | FLOAT | _(derived)_ | tip / fare |
| `tolls_amount` | FLOAT | `tolls_amount` | Phí cầu đường |
| `improvement_surcharge` | FLOAT | `improvement_surcharge` | Phụ phí cải tiến |
| `congestion_surcharge` | FLOAT | `congestion_surcharge` | Phụ phí tắc đường |
| `airport_fee` | FLOAT | `Airport_fee` | Phí sân bay |
| `cbd_congestion_fee` | FLOAT | `cbd_congestion_fee` | Phí tắc đường CBD |
| `total_amount` | FLOAT | `total_amount` | Tổng tiền |
| `store_and_fwd_flag` | VARCHAR | `store_and_fwd_flag` | Lưu trước khi gửi? |
| `pickup_date` | DATE | _(derived)_ | Ngày đón khách |

---

## DIM_TIME

| Column | Type | Mô tả |
|---|---|---|
| `time_key` | INT PK | Surrogate key |
| `datetime` | TIMESTAMP | Timestamp gốc |
| `date` | DATE | Ngày |
| `year` | INT | Năm |
| `month` | INT | Tháng (1-12) |
| `month_name` | VARCHAR | Tên tháng |
| `day` | INT | Ngày trong tháng |
| `day_of_week` | INT | Thứ (0=Mon, 6=Sun) |
| `day_name` | VARCHAR | Tên thứ |
| `hour` | INT | Giờ (0-23) |
| `is_weekend` | BOOLEAN | Cuối tuần? |
| `is_peak_hour` | BOOLEAN | Giờ cao điểm? |
| `quarter` | INT | Quý (1-4) |

---

## DIM_LOCATION

| Column | Type | Mô tả |
|---|---|---|
| `location_key` | INT PK | LocationID gốc từ TLC |
| `zone` | VARCHAR | Tên zone |
| `borough` | VARCHAR | Quận (Manhattan, Brooklyn,...) |
| `service_zone` | VARCHAR | Khu vực dịch vụ |

---

## DIM_VENDOR

| Column | Type | Mô tả |
|---|---|---|
| `vendor_key` | INT PK | VendorID gốc |
| `vendor_name` | VARCHAR | Tên công ty |

Mapping hiện tại:
- `1` = Creative Mobile Technologies (CMT)
- `2` = Curb Mobility (VeriFone)

---

## DIM_PAYMENT

| Column | Type | Mô tả |
|---|---|---|
| `payment_key` | INT PK | payment_type gốc |
| `payment_name` | VARCHAR | Tên phương thức |

Mapping hiện tại:
- `1` = Credit card
- `2` = Cash
- `3` = No charge
- `4` = Dispute
- `0` = Unknown

---

## DIM_RATE

| Column | Type | Mô tả |
|---|---|---|
| `rate_key` | INT PK | RatecodeID gốc |
| `rate_name` | VARCHAR | Tên loại giá |

Mapping hiện tại:
- `1` = Standard rate
- `2` = JFK
- `3` = Newark
- `4` = Nassau/Westchester
- `5` = Negotiated fare
- `6` = Group ride

---

## Derived Columns (tính toán trong ETL)

| Column | Công thức |
|---|---|
| `trip_duration_min` | `(dropoff_ts - pickup_ts) / 60` |
| `tip_ratio` | `tip_amount / fare_amount` |
| `pickup_date` | `to_date(tpep_pickup_datetime)` |

---

## Notes

- Source file: `data/raw/yellow_tripdata_*.parquet`
- Rows per month: ~3.7 triệu (ví dụ Jan 2026)
- Columns source: 20 columns
- Sau ETL: ~24+ columns (có thêm derived columns)
