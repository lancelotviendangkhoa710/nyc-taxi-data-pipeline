# Data Profiling Report — NYC Yellow Taxi (January 2026)

Báo cáo chi tiết về chất lượng dữ liệu, các điểm dị biệt (outliers) và dữ liệu khuyết thiếu (null) của tập dữ liệu `yellow_tripdata_2026-01.parquet`.

---

## 1. Dữ Liệu Khuyết Thiếu (Missing/Null Values)

Tổng số dòng dữ liệu: **3,724,889 dòng**.

Có 5 cột có tỷ lệ khuyết thiếu dữ liệu chính xác là **29.2105%** (tương đương **1,088,058 dòng** bị Null):
*   `passenger_count`
*   `RatecodeID`
*   `store_and_fwd_flag`
*   `congestion_surcharge`
*   `Airport_fee`

Tất cả các cột còn lại có tỷ lệ Null là **0%**.

> [!WARNING]
> Cột `payment_type` không bị Null (0%) nhưng ghi nhận **1,088,058 dòng có giá trị bằng 0** (trùng khớp với số dòng Null của 5 cột trên). Trong thực tế, giá trị `0` ở cột này đại diện cho "Unknown" hoặc "Missing".

---

## 2. Các Giá Trị Ngoại Lệ (Outliers)

### a. Khoảng cách di chuyển (`trip_distance`)
*   **Khoảng cách <= 0 dặm:** **125,738 dòng (3.3756%)**. Chuyến đi có khoảng cách bằng 0 là bất thường và cần được lọc bỏ hoặc xử lý.
*   **Khoảng cách cực đại (Max):** **269,097.48 dặm**. Đây là giá trị sai số thiết bị cực kỳ nghiêm trọng (Outlier nặng).
*   **Khoảng cách > 100 dặm:** **162 dòng (0.0043%)**. Các chuyến đi trên 100 dặm trong nội đô NYC là rất hiếm và có thể coi là ngoại lệ cần xem xét loại bỏ.

### b. Các khoản phí và Tổng tiền (`total_amount`)
*   **Tổng tiền âm (`total_amount` < 0):** **39,984 dòng (1.0734%)**. 
    *   *Nguyên nhân:* Có thể là các giao dịch hoàn tiền (refunds) hoặc tranh chấp (disputes).
    *   *Min total_amount:* `-2560.2 USD`.
*   **Tổng tiền bằng 0 (`total_amount` == 0):** **433 dòng (0.0116%)**.
*   *Max total_amount:* `2560.2 USD`.

---

## 3. Dị Biệt Về Thời Gian (Datetime Anomalies)

*   **Thời gian kết thúc trước thời gian bắt đầu (`tpep_dropoff_datetime` <= `tpep_pickup_datetime`):** **45,070 dòng (1.2100%)**. Đây là lỗi logic thời gian nghiêm trọng (xe chưa đón đã trả khách hoặc lỗi thiết bị ghi nhận).
*   **Ngày đón khách nằm ngoài tháng 1/2026:** **7 dòng (0.0002%)**. Dữ liệu tháng 1 nhưng ghi nhận ngày đón ở các năm/tháng khác do đồng hồ trên xe bị sai cấu hình thời gian.

---

## 4. Phân Phối Dữ Liệu Danh Mục (Categorical Distributions)

### a. RatecodeID (Mã loại cước)
| RatecodeID | Ý Nghĩa | Số Lượng Dòng | Tỷ Lệ |
| :--- | :--- | :--- | :--- |
| **NULL** | Bị khuyết thiếu | 1,088,058 | 29.21% |
| **1** | Standard rate | 2,390,495 | 64.18% |
| **2** | JFK Airport | 83,592 | 2.24% |
| **3** | Newark Airport | 11,541 | 0.31% |
| **4** | Nassau / Westchester | 8,304 | 0.22% |
| **5** | Negotiated fare | 32,030 | 0.86% |
| **6** | Group ride | 5 | 0.00% |
| **99** | Mã lỗi thiết bị / Chưa xác định | 110,864 | 2.98% |

> [!IMPORTANT]
> `RatecodeID = 99` không nằm trong danh mục chuẩn của TLC (1-6). Đây là mã lỗi từ hệ thống ghi nhận của nhà cung cấp và cần được quy về nhóm `"Unknown"` trong ETL.

### b. payment_type (Phương thức thanh toán)
*   **0 (Unknown/Null):** 1,088,058 dòng (29.21%)
*   **1 (Credit card):** 2,249,747 dòng (60.40%)
*   **2 (Cash):** 314,043 dòng (8.43%)
*   **3 (No charge):** 16,641 dòng (0.45%)
*   **4 (Dispute):** 56,400 dòng (1.51%)

### c. passenger_count (Số lượng hành khách)
*   **NULL:** 1,088,058 dòng (29.21%)
*   **0 hành khách:** 14,787 dòng (0.40%) (Vô lý đối với một chuyến đi thương mại)
*   **1 hành khách:** 2,150,994 dòng (57.75%) (Phổ biến nhất)
*   **2 - 6 hành khách:** Phân phối bình thường.
*   **7 - 9 hành khách:** Rất ít (chỉ dưới 10 dòng), có thể là xe khách cỡ lớn hoặc lỗi nhập liệu của tài xế.

---

## 5. Đề Xuất Quy Tắc Làm Sạch Dữ Liệu (ETL Rules for Phase 2)

Từ các phát hiện trên, chúng ta thống nhất các quy tắc xử lý dữ liệu sau cho Phase 2:
1.  **Lọc bỏ các bản ghi lỗi nghiêm trọng:**
    *   Loại bỏ các dòng có `tpep_dropoff_datetime <= tpep_pickup_datetime`.
    *   Loại bỏ các dòng có `pickup_datetime` không nằm trong tháng 1/2026.
    *   Loại bỏ các dòng có `total_amount <= 0` (hoặc tách riêng để phân tích refund nếu cần, nhưng đối với DW phân tích hoạt động kinh doanh thông thường thì nên loại bỏ).
2.  **Xử lý Outliers:**
    *   Loại bỏ các chuyến đi có `trip_distance <= 0` hoặc `trip_distance > 100` dặm.
    *   Loại bỏ các chuyến đi có `passenger_count == 0` (hoặc gán về giá trị mặc định là 1 nếu muốn giữ dòng).
3.  **Chuẩn hóa dữ liệu khuyết thiếu:**
    *   Điền giá trị mặc định `"Unknown"` hoặc `-1` cho `RatecodeID` và `payment_type` nếu bị Null/0.
    *   Điền giá trị mặc định `1` cho `passenger_count` nếu bị Null.
    *   Điền `0.0` cho `congestion_surcharge` và `Airport_fee` nếu bị Null.
