# IMPLEMENT PLAN (Kế hoạch thực thi)

## 1. MỤC TIÊU

- Triển khai và kiểm thử mô hình staging `stg_trip` từ nguồn `fact_trip`.
- Cấu hình kiểm thử chất lượng dữ liệu (Data Quality Test) bằng file YAML.
- Thiết lập luồng xử lý từ Staging qua Intermediate (nếu có) đến Marts phục vụ BI/Analytics.

## 2. PHẠM VI

- **Công cụ**: dbt (data build tool), Supabase PostgreSQL (data warehouse hiện tại).
- **Phạm vi code**:
  - `dbt/models/staging/stg_trip.sql` (Đã khởi tạo)
  - `dbt/models/staging/_stg_sources.yml` hoặc file schema tương đương để định nghĩa test.
  - Tầng tiếp theo: Tạo mô hình intermediate hoặc mart phân tích doanh thu/hiệu suất.

## 3. CÁC BƯỚC THỰC HIỆN

1. **Khảo sát nguồn**: Đảm bảo bảng `fact_trip` tồn tại trong schema nguồn (`warehouse`).
2. **Triển khai Staging Model**:
   - Viết SQL SELECT từ `fact_trip`.
   - Áp dụng các điều kiện lọc cơ bản (ví dụ: `trip_duration_min > 0`, `trip_distance > 0`).
3. **Cấu hình YAML Tests**:
   - Khai báo các cột khóa chính (`trip_id`) là `unique` và `not_null`.
   - Khai báo các khóa ngoại (`pickup_location_key`, `payment_key`) tham chiếu đúng bảng danh mục.
4. **Kiểm tra và Vận hành**:
   - Chạy lệnh `dbt run --select stg_trip` để biên dịch và tạo bảng/view.
   - Chạy lệnh `dbt test --select stg_trip` để xác thực chất lượng dữ liệu.
5. **Mở rộng (Production/Doanh nghiệp)**:
   - Tích hợp CI/CD để tự động chạy test khi pull request.
   - Xây dựng tầng Intermediate và Marts.

## 4. RÀNG BUỘC

- Dữ liệu khóa chính không được trùng lặp và không được NULL.
- Hiệu năng truy vấn: Tầng staging nên được lưu ở dạng View để tránh nhân bản dữ liệu vật lý không cần thiết (YAGNI).
