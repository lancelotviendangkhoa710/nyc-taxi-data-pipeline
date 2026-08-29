# CV Project Review — NYC Taxi Data Engineering

> Đánh giá từ góc nhìn HR + AI CV Scanner  
> Generated: 2026-08-28 | Status: In Progress

---

## ✅ ĐIỂM MẠNH — "Instantly impressive"

**1. Tech Stack đúng chuẩn thị trường**
Spark + PostgreSQL + dbt + Docker + Power BI — đây là **Data Engineering stack phổ biến nhất** ở các công ty mid-to-large. HR/AI scanner sẽ match keyword rất cao với JD Data Engineer.

**2. Kiến trúc end-to-end có tư duy**
Không chỉ "load CSV lên DB" — có đầy đủ layers: Raw → Processed → Warehouse → dbt → Dashboard. Thể hiện hiểu **Medallion/Lakehouse architecture** dù chạy local.

**3. Code quality có ý thức**

- Type hints (`DataFrame`, `SparkSession`, `list[Path]`) — dấu hiệu của người đã học production code
- Separation of concerns rõ ràng: `extract.py`, `transform.py`, `validate.py`, `load.py` riêng biệt
- OOP Hybrid pattern trong `pipeline.py` — orchestration qua class, logic qua pure functions — đây là pattern đúng

**4. Adaptive partition sizing thực sự thú vị**
`calculate_write_partitions()` trong `load.py` — tự tính toán số partition dựa trên input size, có min/max bound, dùng `coalesce` vs `repartition` đúng trường hợp. Đây **không phải tutorial code** — người viết đã suy nghĩ về performance.

**5. Benchmark harness chuyên nghiệp**
`etl_benchmark.py` với CSV output, CLI args, đo từng phase (read/transform/write seconds) — ít portfolio project nào có cái này. HR tech sẽ ấn tượng.

**6. Documentation đầy đủ**
README đẹp với badges, `architecture.md`, `data_dictionary.md`, `PROGRESS.md` — thể hiện tư duy sản phẩm, không chỉ code.

**7. Star Schema thiết kế đúng**
`fact_trip` + 5 dimension tables, MD5 surrogate key, time key dạng `yyyyMMddHH` — thể hiện hiểu data modeling.

---

## ⚠️ ĐIỂM YẾU — "Red flags HR/AI sẽ chú ý"

**1. `df_fact_mapped = df_fact_mapped.limit(200)` — hardcode trong production code** *(Critical)* - Cái này tui cố tình để chạy test tiết kiệm thời gian

- **File:** `spark/etl/load_warehouse.py` dòng 286
- Fact table chỉ load 200 dòng — nếu interviewer chạy thử sẽ hỏi ngay
- **Fix:** Xóa dòng này hoặc chuyển thành env var `ETL_TEST_ROW_LIMIT`
- **Status:** [ ] Chưa fix

**2. Password hardcode trong `config.py`** *(Critical — Security)*

- **File:** `spark/config.py` dòng 77
- `PG_PASSWORD = os.getenv("PG_PASSWORD", "Tmo2159@@##")` — lộ password thật
- **Fix:** Xóa default value, raise `EnvironmentError` nếu thiếu biến môi trường
- **Status:** [ ] Chưa fix

**3. Comment lẫn lộn BigQuery/PostgreSQL**

- **File:** `spark/etl/pipeline.py` dòng 115
- Comment ghi `# Load Warehouse (Google BigQuery)` nhưng thực ra load PostgreSQL
- **Fix:** Sửa comment thành `# Load Warehouse (PostgreSQL)`
- **Status:** [ ] Chưa fix

**4. Tests quá mỏng**

- `test_pipeline.py` không có assertions — chỉ gọi `df.show()`
- `test_etl_benchmark.py` tốt hơn nhưng coverage thấp
- **Fix:** Thêm unit test có assertions cho transform logic (null handling, outlier filter, derived columns)
- **Status:** [ ] Chưa fix

**5. Spark chạy `local[*]` — không có cluster**

- Cần ghi rõ trong README: bao nhiêu GB, bao nhiêu rows đã xử lý
- **Fix:** Thêm data volume cụ thể vào README
- **Status:** [ ] Chưa fix

**6. Airflow "Planned" — mentioned nhiều lần nhưng không có code**

- Architecture diagram có Airflow, `architecture.md` mô tả Airflow DAG nhưng không implement
- **Fix:** Implement DAG đơn giản HOẶC xóa mention khỏi README/architecture
- **Status:** [ ] Chưa fix

**7. Power BI trạng thái không nhất quán**

- File `Dashboard.pbix` tồn tại nhưng README ghi "Planned"
- **Fix:** Update README status cho đúng thực tế
- **Status:** [ ] Chưa fix

---

## 🚀 ĐIỂM CẦN PHÁT TRIỂN ĐỂ LEVEL UP CV

### Ưu tiên cao — làm ngay

| # | Việc cần làm | File liên quan | Status |
| --- | --- | --- | --- |
| 1 | Xóa `limit(200)` khỏi production code | `spark/etl/load_warehouse.py:286` | [ ] |
| 2 | Fix hardcode password → raise exception | `spark/config.py:77` | [ ] |
| 3 | Thêm pytest assertions thực vào test | `tests/test_pipeline.py` | [ ] |
| 4 | Ghi rõ data volume trong README (X GB, Y million rows) | `README.md` | [ ] |

### Ưu tiên trung bình — tăng điểm mạnh

| # | Việc cần làm | Tác động |
| --- | --- | --- |
| 5 | Implement Airflow DAG đơn giản hoặc xóa mention | Không bị hỏi về thứ không có |
| 6 | Thêm CI/CD (GitHub Actions) chạy `pytest` + `dbt test` | Thể hiện DevOps awareness |
| 7 | Thêm data quality metrics vào `validate.py` — đếm null %, outlier % | Data Quality mindset |
| 8 | Screenshot Power BI dashboard vào README | Visual proof of work |

### Ưu tiên thấp — nice to have

| # | Việc cần làm | Tác động |
| --- | --- | --- |
| 9 | Thêm `great-expectations` hoặc `soda` cho data quality | Keyword bonus cho Senior JD |
| 10 | Deploy lên cloud (GCS/S3 + BigQuery/Redshift) dù free tier | "Cloud experience" trên CV |
| 11 | Viết blog post/Medium article về project | SEO cho tên, thể hiện communication skill |

---

## 📊 Verdict tổng thể

| Tiêu chí | Đánh giá | Điểm (1-10) |
| --- | --- | --- |
| Tech stack relevance | Rất phù hợp thị trường | 9/10 |
| Architecture thinking | Tốt, có chiều sâu | 8/10 |
| Code quality | Khá tốt, có vài chỗ cần clean | 7/10 |
| Testing | Yếu, cần cải thiện | 5/10 |
| Documentation | Tốt | 8/10 |
| Production readiness | Chưa đủ (`limit(200)`, hardcode password) | 5/10 |
| **Overall** | **Junior-to-Mid Data Engineer** | **7/10** |

> **Tóm lại:** Project đủ để pass ATS và gây ấn tượng HR ban đầu. Sẽ gặp khó trong technical interview nếu interviewer đọc code kỹ — cụ thể là `limit(200)` và test coverage. Fix 4 điểm Critical trước, sau đó project có thể lên **8.5/10** và compete được với ứng viên 1-2 năm kinh nghiệm.
