# Từ Local lên BigQuery — Flow, hàm, và cơ chế vận hành

## 1. Flow của project này

> Project hiện **upload Parquet trực tiếp từ local lên BigQuery**, không qua GCS.

```text
NYC TLC HTTP
  → data/raw/yellow/yellow_tripdata_YYYY-MM.parquet
  → Spark: validate, chuẩn hóa kiểu, xử lý null, dedup
  → data/processed/yellow_taxi/source_month=YYYY-MM/*.parquet
  → BigQuery load job
  → nyc_taxi_raw.yellow_taxi_raw
  → dbt: staging → intermediate → marts
  → Power BI
```

Điểm vào: `spark/etl/pipeline.py`.

| Bước | Hàm/phương thức | Nhiệm vụ |
|---|---|---|
| Chọn batch | `ETLMetadata.get_latest_unprocessed()` | Tìm file chưa hoàn tất |
| Đọc local | `YellowTaxiETLPipeline.extract()` | Spark đọc Parquet raw |
| Kiểm tra | `validate()` | Kiểm schema, DataFrame rỗng |
| T1 transform | `transform()` | Type, null, duplicate, `pickup_date` |
| Ghi local | `load()` | Ghi Parquet processed |
| Upload BQ | `load_bigquery()` | Gọi `BigQueryLoader.load_batch()` |
| T2 transform | `dbt run`, `dbt test` | Tạo bảng analytics, kiểm data quality |

## 2. “Hàm”, “phương thức”, “class”, “object”

```python
def add(a: int, b: int) -> int:
    return a + b
```

- `add`: **hàm**. Gọi độc lập: `add(2, 3)`.
- `a`, `b`: tham số. `2`, `3`: đối số.
- `return`: giá trị trả về.

```python
class BigQueryLoader:
    def load_batch(self, parquet_dir: Path, source_month: str) -> None:
        ...

loader = BigQueryLoader()
loader.load_batch(batch_dir, "2026-05")
```

- `BigQueryLoader`: **class**, bản thiết kế.
- `loader`: **object/instance**, một đối tượng tạo từ class.
- `load_batch`: **phương thức**; là hàm nằm trong class, gọi qua object.
- `self`: chính object đang chạy. `self.client` là BigQuery client thuộc `loader` đó.
- `__init__`: phương thức khởi tạo; tự chạy khi gọi `BigQueryLoader()`.

Ví dụ đời thường: class là bản thiết kế xe; object là một chiếc xe; method `car.start()` là thao tác của chiếc xe đó.

## 3. Đọc dòng upload quan trọng

Nguồn: `spark/etl/load_bigquery.py`.

```python
credentials = service_account.Credentials.from_service_account_file(
    GCP_KEYFILE_PATH,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
client = bigquery.Client(project=GCP_PROJECT_ID, credentials=credentials)
```

1. `from_service_account_file(...)` đọc JSON service account.
2. Thư viện Google dùng private key trong JSON để chứng minh danh tính với Google.
3. Google trả access token tạm thời, theo `scope` đã xin.
4. `bigquery.Client(...)` giữ project, credentials, logic gọi BigQuery API.
5. Mọi lệnh `client.*` sau đó gửi HTTPS request có token. Google kiểm IAM role, rồi cho phép hoặc từ chối.

JSON key là bí mật. Không in, gửi chat, commit Git, hay chép vào document. File hiện đã bị `.gitignore` bỏ qua.

## 4. Vì sao dữ liệu “đi lên cloud” được?

Lệnh thực sự gửi byte file là:

```python
with open(fpath, "rb") as file_obj:
    job = self.client.load_table_from_file(
        file_obj,
        table_ref,
        job_config=job_config,
    )
job.result()
```

Diễn giải:

| Phần | Nghĩa |
|---|---|
| `open(fpath, "rb")` | Mở file local dạng binary; `rb` = read binary |
| `file_obj` | Luồng byte đọc từ file, không phải toàn bộ file bắt buộc nằm trong RAM |
| `load_table_from_file(...)` | Google SDK upload byte qua HTTPS, yêu cầu BigQuery tạo **load job** |
| `job` | Handle/biên nhận của tác vụ async trên BigQuery |
| `job.result()` | Chờ BigQuery nhận file, đọc Parquet, suy schema, ghi table; lỗi thì raise exception |

Nói ngắn: Python SDK là lớp bọc của BigQuery REST API. Nó đọc bytes từ ổ đĩa, gửi qua mạng HTTPS; BigQuery xử lý bytes trong hạ tầng Google và ghi thành table.

## 5. Table reference, dataset, schema

```python
table_ref = f"{self.project}.{self.dataset}.{table_name}"
# nyc-taxi-data-pipeline-507015.nyc_taxi_raw.yellow_taxi_raw
```

Format đầy đủ:

```text
project_id.dataset_id.table_id
```

- `project_id`: GCP project, nơi tính quyền và chi phí.
- `dataset_id`: nhóm table, gần giống schema.
- `table_id`: bảng cụ thể.

Dataset được tạo nếu chưa có:

```python
dataset_ref = bigquery.Dataset("project_id.nyc_taxi_raw")
dataset_ref.location = "US"
client.create_dataset(dataset_ref, exists_ok=True)
```

`exists_ok=True`: dataset đã tồn tại thì không lỗi. Đây là thao tác **idempotent**: chạy lại cho cùng kết quả mong muốn.

## 6. Load job config: BigQuery phải đọc và ghi thế nào?

```python
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.PARQUET,
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    autodetect=True,
)
```

| Field | Tác dụng |
|---|---|
| `source_format=PARQUET` | Báo file là Parquet; BigQuery biết cách giải mã cột, type, metadata |
| `autodetect=True` | Suy schema từ file khi cần |
| `WRITE_APPEND` | Giữ row cũ, thêm row mới |
| `WRITE_TRUNCATE` | Xóa/ghi đè toàn table rồi nạp data mới |

Ví dụ 2 file tháng 05 và 06:

```text
05 load với WRITE_TRUNCATE: table = [05]
06 load với WRITE_APPEND:   table = [05, 06]
```

Trong `_load_parquet_files()`, file đầu dùng disposition truyền vào; file thứ hai trở đi luôn dùng `WRITE_APPEND`. Lý do: tránh file sau xóa dữ liệu file trước trong cùng batch.

## 7. Batch state và retry

Manifest: `data/metadata/etl_metadata.json`.

```text
fetched → processed → bq_loaded → dbt_tested → completed
```

- `processed`: Spark thành công, file local processed còn đó. Chạy lại sẽ retry BigQuery, không chạy Spark lại.
- `bq_loaded`: BigQuery load thành công. Sau đó chạy dbt.
- `dbt_tested`: `dbt run` và `dbt test` pass.
- `completed`: cleanup đã xóa raw/processed theo retention; manifest vẫn giữ record để không xử lý lại.

## 8. Cảnh báo retry hiện tại

`BigQueryLoader.load_batch()` trong code hiện chọn:

```python
WRITE_APPEND if table_da_co_rows else WRITE_TRUNCATE
```

Nó **không xóa row cũ theo `source_month`** trước khi append. Vì vậy không tự chạy lại một batch đã load thành công: có thể duplicate data tháng đó.

Trước backfill/retry batch đã load, kiểm tra:

```sql
SELECT source_month, COUNT(*) AS row_count
FROM `nyc-taxi-data-pipeline-507015.nyc_taxi_raw.yellow_taxi_raw`
GROUP BY source_month
ORDER BY source_month;
```

Mục tiêu đúng cho replace-batch là: xóa `source_month` cũ, rồi append Parquet batch mới. Đây cũng là ý định mô tả trong `docs/architecture.md`; cần đối chiếu code trước khi vận hành reprocess.

## 9. Local trực tiếp khác GCS thế nào?

| Flow | Cách upload | Dùng khi |
|---|---|---|
| Local → BigQuery | `load_table_from_file(file_obj, ...)` | Project hiện tại, file/batch vừa phải |
| Local → GCS → BigQuery | Upload Cloud Storage, rồi `load_table_from_uri("gs://...")` | Data lake, file lớn, nhiều service/scheduler dùng chung raw data |

GCS URI ví dụ:

```text
gs://nyc-taxi-raw/yellow/year=2026/month=05/file.parquet
```

GCS không phải bắt buộc để BigQuery nhận Parquet. Nó là một landing zone cloud bền vững, tách storage raw khỏi máy local.

## 10. Checklist vận hành

```bash
# Chạy một ETL batch trong Docker từ project root
docker compose -f infrastructure/docker/docker-compose.yml run --rm spark-etl

# Build T2 + kiểm tra chất lượng
docker compose -f infrastructure/docker/docker-compose.yml run --rm dbt
```

1. Kiểm service account có quyền tạo dataset/load table.
2. Kiểm `GCP_PROJECT_ID`, `GCP_DATASET_RAW`, `GCP_KEYFILE_PATH`.
3. Kiểm `processed/.../source_month=YYYY-MM/` có Parquet trước BQ load.
4. Đọc log `total rows` sau `job.result()`.
5. Chạy `dbt run`, rồi `dbt test`.
6. Chỉ cleanup khi dbt test pass.

## 11. Câu hỏi tự kiểm tra

1. `job.result()` bỏ đi thì sao? Upload/load chạy async; script có thể kết thúc trước khi biết thành công hay thất bại.
2. Vì sao Parquet tốt? Schema/type có sẵn, dạng cột, nén tốt; ít lỗi type hơn CSV.
3. Vì sao cần service account? BigQuery không tin máy local mặc định; token từ account xác định “ai” đang gọi và IAM quyết định “được làm gì”.
4. `WRITE_TRUNCATE` nguy hiểm khi nào? Khi table chứa nhiều tháng nhưng lại dùng nó để nạp một tháng; các tháng cũ bị xóa.