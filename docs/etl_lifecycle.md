# Vòng đời batch ETL và retention local

## Mục tiêu

NYC TLC thường phát hành file trễ 2–3 tháng. Pipeline dùng metadata manifest làm source of truth; `raw/` và `processed/` chỉ là staging có thể dọn sau khi Redshift và dbt xác nhận thành công.

## Luồng batch

```text
fetch → raw/yellow/yellow_tripdata_YYYY-MM.parquet
      → Spark validate/transform
      → processed/yellow_taxi/source_month=YYYY-MM/
       → S3 silver/yellow_taxi/source_month=YYYY-MM/ → Redshift yellow_taxi_raw
      → dbt run → dbt test
      → manifest completed → cleanup local
```

`source_month` được ghi vào Parquet và S3 key để nhận diện batch Redshift. Loader xóa batch cùng tháng trước `COPY`, nên rerun thay thế dữ liệu cũ mà không duplicate.

## Metadata

Manifest: `data/metadata/etl_metadata.json`. File này **không được cleanup**.

| Status | Ý nghĩa | Retry tiếp theo |
|---|---|---|
| `fetched` | Raw có trên local | Spark process |
| `processed` | Parquet batch đã ghi | DWH load, không Spark lại |
| `dwh_loaded` | Redshift load thành công | Chờ dbt run/test |
| `dbt_tested` | dbt test thành công | Dọn khi hết retention |
| `completed` | Raw/processed đã dọn | Skip fetch/process/load |
| `failed` | Bước gần nhất lỗi | Retry thủ công từ batch đó |

## Cleanup

- Chỉ chạy sau `dbt test` thành công qua `spark/etl/finalize.py`.
- Chỉ dọn source batch có `status=dbt_tested`.
- Chỉ xóa `data/raw/yellow/<filename>` và `data/processed/yellow_taxi/source_month=YYYY-MM` cùng batch.
- Manifest chuyển sang `completed` sau cleanup.
- Mặc định giữ 7 ngày. Cấu hình `ETL_LOCAL_RETENTION_DAYS=0` để cleanup ngay. Không đặt số âm.
- `ETL_TEST_ROW_LIMIT` không được dùng cho production cleanup.

## Dữ liệu trễ và backfill

Fetcher bỏ qua source `completed`, kể cả raw local đã bị dọn. Các tháng chưa completed vẫn được kiểm tra/tải. Với TLC trễ 2–3 tháng, scheduler nên chạy monthly và look back ít nhất 4 tháng.

Khi cần backfill, không xóa record manifest. Tạo lệnh force riêng để tải, process, replace Redshift batch và chạy dbt cho tháng cần xử lý; lưu lịch sử reprocess trong manifest.

Các dbt models incremental reprocess `source_month` mới nhất trong normal run. Khi backfill một tháng cũ hơn tháng mới nhất, chạy `dbt run --full-refresh` để rebuild chính xác các facts affected. Sau lần deploy thay đổi này, chạy một lần `dbt run --full-refresh` để thêm `source_month` vào các bảng incremental hiện có.

## Vận hành Docker

`docker compose -f infrastructure/docker/docker-compose.yml up --build` chạy Spark trước. Container dbt chạy `dbt run`, `dbt test`, rồi finalizer. Nếu dbt fail, shell `set -e` dừng trước finalizer: raw/processed giữ nguyên để retry.