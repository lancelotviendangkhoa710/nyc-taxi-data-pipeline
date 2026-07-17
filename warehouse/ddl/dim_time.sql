CREATE OR REPLACE TABLE dim_time (
    time_key INT64 OPTIONS(description="Mã thời gian dạng YYYYMMDDHH"),
    datetime TIMESTAMP OPTIONS(description="Thời gian gốc"),
    date DATE OPTIONS(description="Ngày"),
    year INT64 OPTIONS(description="Năm"),
    month INT64 OPTIONS(description="Tháng (1-12)"),
    month_name STRING OPTIONS(description="Tên tháng"),
    day INT64 OPTIONS(description="Ngày trong tháng"),
    day_of_week INT64 OPTIONS(description="Thứ (1=Thứ 2, 7=Chủ nhật)"),
    day_name STRING OPTIONS(description="Tên thứ"),
    hour INT64 OPTIONS(description="Giờ (0-23)"),
    is_weekend BOOL OPTIONS(description="Đánh dấu cuối tuần"),
    is_peak_hour BOOL OPTIONS(description="Đánh dấu giờ cao điểm"),
    quarter INT64 OPTIONS(description="Quý (1-4)")
);
