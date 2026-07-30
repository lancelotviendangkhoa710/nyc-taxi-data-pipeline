CREATE OR REPLACE TABLE fact_trip (
    trip_id STRING OPTIONS(description="Mã surrogate key duy nhất cho mỗi chuyến đi"),
    vendor_key INT64 OPTIONS(description="FK liên kết DIM_VENDOR"),
    pickup_time_key INT64 OPTIONS(description="FK liên kết DIM_TIME (Thời gian đón khách)"),
    dropoff_time_key INT64 OPTIONS(description="FK liên kết DIM_TIME (Thời gian trả khách)"),
    pickup_location_key INT64 OPTIONS(description="FK liên kết DIM_LOCATION (Điểm đón)"),
    dropoff_location_key INT64 OPTIONS(description="FK liên kết DIM_LOCATION (Điểm trả)"),
    payment_key INT64 OPTIONS(description="FK liên kết DIM_PAYMENT"),
    rate_key INT64 OPTIONS(description="FK liên kết DIM_RATE"),
    passenger_count INT64 OPTIONS(description="Số lượng hành khách"),
    trip_distance FLOAT64 OPTIONS(description="Khoảng cách chuyến đi (miles)"),
    trip_duration_min FLOAT64 OPTIONS(description="Thời gian di chuyển (phút)"),
    fare_amount FLOAT64 OPTIONS(description="Tiền cước cơ bản"),
    extra FLOAT64 OPTIONS(description="Phụ phí"),
    mta_tax FLOAT64 OPTIONS(description="Thuế MTA"),
    tip_amount FLOAT64 OPTIONS(description="Tiền tip"),
    tip_ratio FLOAT64 OPTIONS(description="Tỉ lệ tip / cước gốc"),
    tolls_amount FLOAT64 OPTIONS(description="Phí cầu đường"),
    improvement_surcharge FLOAT64 OPTIONS(description="Phụ phí cải tiến"),
    congestion_surcharge FLOAT64 OPTIONS(description="Phụ phí tắc đường"),
    airport_fee FLOAT64 OPTIONS(description="Phí sân bay"),
    cbd_congestion_fee FLOAT64 OPTIONS(description="Phí tắc đường CBD"),
    total_amount FLOAT64 OPTIONS(description="Tổng tiền thanh toán"),
    store_and_fwd_flag STRING OPTIONS(description="Cờ lưu trữ trước khi gửi"),
    pickup_date DATE OPTIONS(description="Ngày đón khách (dùng để phân vùng)")
)
PARTITION BY pickup_date
CLUSTER BY pickup_location_key, dropoff_location_key, vendor_key;
