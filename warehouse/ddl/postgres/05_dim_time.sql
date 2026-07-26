-- PostgreSQL DDL for dim_time
CREATE TABLE IF NOT EXISTS dim_time (
    time_key INTEGER PRIMARY KEY,
    datetime TIMESTAMP NOT NULL,
    date DATE NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    hour INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL DEFAULT FALSE,
    is_peak_hour BOOLEAN NOT NULL DEFAULT FALSE,
    quarter INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dim_time_date ON dim_time(date);
CREATE INDEX IF NOT EXISTS idx_dim_time_datetime ON dim_time(datetime);

COMMENT ON TABLE dim_time IS 'Dimension: Time hierarchy for time-based analysis';
COMMENT ON COLUMN dim_time.time_key IS 'Mã thời gian dạng YYYYMMDDHH';
COMMENT ON COLUMN dim_time.datetime IS 'Thời gian gốc';
COMMENT ON COLUMN dim_time.date IS 'Ngày';
COMMENT ON COLUMN dim_time.year IS 'Năm';
COMMENT ON COLUMN dim_time.month IS 'Tháng (1-12)';
COMMENT ON COLUMN dim_time.month_name IS 'Tên tháng';
COMMENT ON COLUMN dim_time.day IS 'Ngày trong tháng';
COMMENT ON COLUMN dim_time.day_of_week IS 'Thứ (1=Thứ 2, 7=Chủ nhật)';
COMMENT ON COLUMN dim_time.day_name IS 'Tên thứ';
COMMENT ON COLUMN dim_time.hour IS 'Giờ (0-23)';
COMMENT ON COLUMN dim_time.is_weekend IS 'Đánh dấu cuối tuần';
COMMENT ON COLUMN dim_time.is_peak_hour IS 'Đánh dấu giờ cao điểm';
COMMENT ON COLUMN dim_time.quarter IS 'Quý (1-4)';