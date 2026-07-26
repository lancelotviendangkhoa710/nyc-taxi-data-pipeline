# Từ điển dữ liệu: Kho dữ liệu NYC Taxi

## 1. Bảng sự kiện: `fact_trip`
Bảng trung tâm chứa các chỉ số về chuyến đi.

| Cột | Kiểu dữ liệu | Mô tả |
| :--- | :--- | :--- |
| `trip_id` | STRING | Khóa thay thế duy nhất |
| `vendor_key` | INT64 | Khóa ngoại tới `dim_vendor` |
| `pickup_time_key` | INT64 | Khóa ngoại tới `dim_time` (Thời điểm đón) |
| `dropoff_time_key` | INT64 | Khóa ngoại tới `dim_time` (Thời điểm trả) |
| `pickup_location_key` | INT64 | Khóa ngoại tới `dim_location` (Điểm đón) |
| `dropoff_location_key` | INT64 | Khóa ngoại tới `dim_location` (Điểm trả) |
| `payment_key` | INT64 | Khóa ngoại tới `dim_payment` |
| `rate_key` | INT64 | Khóa ngoại tới `dim_rate` |
| `passenger_count` | INT64 | Số lượng hành khách |
| `trip_distance` | FLOAT64 | Khoảng cách (dặm) |
| `trip_duration_min` | FLOAT64 | Thời gian chuyến đi (phút) |
| `fare_amount` | FLOAT64 | Cước phí cơ bản |
| `tip_amount` | FLOAT64 | Tiền tip |
| `total_amount` | FLOAT64 | Tổng chi phí |
| `pickup_date` | DATE | Khóa phân vùng |

## 2. Bảng danh mục (Dimension)

### `dim_location`
| Cột | Kiểu dữ liệu | Mô tả |
| :--- | :--- | :--- |
| `location_key` | INT64 | Mã vùng TLC |
| `zone` | STRING | Tên khu vực |
| `borough` | STRING | Tên quận |
| `service_zone` | STRING | Khu vực dịch vụ |

### `dim_time`
| Cột | Kiểu dữ liệu | Mô tả |
| :--- | :--- | :--- |
| `time_key` | INT64 | YYYYMMDDHH |
| `datetime` | TIMESTAMP | Thời gian gốc |
| `date` | DATE | Ngày |
| `year` | INT64 | Năm |
| `month` | INT64 | Tháng (1-12) |
| `day_of_week` | INT64 | 1=Thứ 2, 7=Chủ nhật |
| `is_peak_hour` | BOOL | Cờ giờ cao điểm |

### `dim_vendor`
| Cột | Kiểu dữ liệu | Mô tả |
| :--- | :--- | :--- |
| `vendor_key` | INT64 | 1=CMT, 2=VeriFone |
| `vendor_name` | STRING | Tên nhà cung cấp |

### `dim_rate`
| Cột | Kiểu dữ liệu | Mô tả |
| :--- | :--- | :--- |
| `rate_key` | INT64 | Mã loại cước |
| `rate_name` | STRING | Tên loại cước |