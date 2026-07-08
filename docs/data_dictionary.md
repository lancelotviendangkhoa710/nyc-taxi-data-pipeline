# Data Dictionary — NYC Yellow Taxi Dataset

Tài liệu này giải thích ý nghĩa, kiểu dữ liệu và mô tả chi tiết của từng cột trong tập dữ liệu **Yellow Taxi Trip Records** được sử dụng trong dự án.

---

## Danh Sách Các Cột Dữ Liệu

| Tên Cột | Kiểu Dữ Liệu (Spark) | Mô Tả Ý Nghĩa | Ghi Chú / Mã Phân Loại |
| :--- | :--- | :--- | :--- |
| **VendorID** | `Integer` | Mã định danh nhà cung cấp dịch vụ công nghệ taxi. | 1 = Creative Mobile Technologies, LLC<br>2 = VeriFone Inc. |
| **tpep_pickup_datetime** | `Timestamp` | Thời điểm bắt đầu chuyến đi (khách lên xe). | Định dạng: `YYYY-MM-DD HH:MM:SS` |
| **tpep_dropoff_datetime** | `Timestamp` | Thời điểm kết thúc chuyến đi (khách xuống xe). | Định dạng: `YYYY-MM-DD HH:MM:SS` |
| **passenger_count** | `Long` | Số lượng hành khách trên xe. | Do tài xế nhập thủ công trên đồng hồ đo. |
| **trip_distance** | `Double` | Khoảng cách chuyến đi tính bằng dặm (miles). | Được đo bởi đồng hồ taxi (taximeter). |
| **RatecodeID** | `Long` | Mã loại giá/cước áp dụng cho chuyến đi. | 1 = Standard rate (Giá chuẩn)<br>2 = JFK (Sân bay JFK)<br>3 = Newark (Sân bay Newark)<br>4 = Nassau or Westchester<br>5 = Negotiated fare (Giá thỏa thuận)<br>6 = Group ride (Đi chung) |
| **store_and_fwd_flag** | `String` | Cờ chỉ định chuyến đi có được lưu trữ trên bộ nhớ xe trước khi gửi về máy chủ hay không (khi mất kết nối). | Y = Store and forward (Có lưu trữ)<br>N = Not a store and forward (Gửi trực tiếp) |
| **PULocationID** | `Integer` | Mã vùng đón khách (Pickup Taxi Zone). | Tham chiếu đến danh mục Zone của TLC. |
| **DOLocationID** | `Integer` | Mã vùng trả khách (Dropoff Taxi Zone). | Tham chiếu đến danh mục Zone của TLC. |
| **payment_type** | `Long` | Mã phương thức thanh toán của khách hàng. | 1 = Credit card (Thẻ tín dụng)<br>2 = Cash (Tiền mặt)<br>3 = No charge (Không tính phí)<br>4 = Dispute (Tranh chấp)<br>5 = Unknown (Không rõ)<br>6 = Voided trip (Hủy chuyến) |
| **fare_amount** | `Double` | Giá cước tính theo thời gian và khoảng cách của đồng hồ. | Chưa bao gồm các loại thuế phí bổ sung và tiền tip. |
| **extra** | `Double` | Phụ phí bổ sung. | Thường gồm $0.50 (giờ thấp điểm/đêm) hoặc $1.00 (giờ cao điểm). |
| **mta_tax** | `Double` | Thuế MTA ($0.50) tự động áp dụng. | Metropolitan Transportation Authority tax. |
| **tip_amount** | `Double` | Tiền tip (tiền boa) của hành khách. | **Lưu ý:** Chỉ ghi nhận tiền tip qua thẻ tín dụng. Khách tip tiền mặt sẽ hiển thị bằng 0. |
| **tolls_amount** | `Double` | Tổng phí cầu đường hành khách chi trả trong chuyến đi. | |
| **improvement_surcharge** | `Double` | Phụ phí cải tạo hạ tầng ($0.30/chuyến). | Bắt đầu áp dụng từ năm 2015. |
| **total_amount** | `Double` | Tổng số tiền hành khách phải trả. | Công thức: `fare_amount` + `extra` + `mta_tax` + `tip_amount` + `tolls_amount` + `improvement_surcharge` + `congestion_surcharge` + `Airport_fee` + `cbd_congestion_fee` (Không bao gồm tip tiền mặt). |
| **congestion_surcharge** | `Double` | Phụ phí ùn tắc ($2.50). | Áp dụng cho các chuyến đi qua vùng ùn tắc ở Manhattan. |
| **Airport_fee** | `Double` | Phí sân bay ($1.25). | Áp dụng cho các chuyến đón khách tại sân bay LaGuardia hoặc JFK. |
| **cbd_congestion_fee** | `Double` | Phí ùn tắc khu trung tâm (Central Business District). | Phí bổ sung tại các khu vực trung tâm sầm uất. |

---

## Các Cột Dữ Liệu Phái Sinh Dự Kiến (Derived Columns)

Trong quá trình biến đổi dữ liệu (ETL Phase 2), chúng ta sẽ tạo thêm các trường sau để phục vụ phân tích:

1. **trip_duration_min**: Thời gian chuyến đi tính bằng phút.
   $$\text{trip\_duration\_min} = \frac{\text{tpep\_dropoff\_datetime} - \text{tpep\_pickup\_datetime}}{60 \text{ (giây)}}$$
2. **tip_ratio**: Tỷ lệ tiền tip trên giá cước gốc.
   $$\text{tip\_ratio} = \frac{\text{tip\_amount}}{\text{fare\_amount}}$$
3. **pickup_date**: Ngày đón khách dạng YYYY-MM-DD (tách ra từ trường timestamp để phân vùng dữ liệu và làm chiều thời gian).
