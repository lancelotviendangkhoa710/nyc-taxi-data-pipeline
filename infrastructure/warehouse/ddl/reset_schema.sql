-- Reset toàn bộ schema warehouse
-- Chạy file này khi cần rebuild lại từ đầu (vd: sau khi thay đổi cấu trúc cột)
-- Lệnh: psql -h localhost -U postgres -d nyc_taxi_dw -f reset_schema.sql

-- 1. Drop các bảng theo thứ tự (fact trước, dim sau để tránh FK conflict)
DROP TABLE IF EXISTS fact_trip CASCADE;
DROP TABLE IF EXISTS dim_time CASCADE;
DROP TABLE IF EXISTS dim_location CASCADE;
DROP TABLE IF EXISTS dim_vendor CASCADE;
DROP TABLE IF EXISTS dim_payment CASCADE;
DROP TABLE IF EXISTS dim_rate CASCADE;

-- 2. Recreate dim tables
CREATE TABLE dim_vendor (
    vendor_key  BIGINT PRIMARY KEY,
    vendor_name VARCHAR NOT NULL
);

CREATE TABLE dim_payment (
    payment_key  BIGINT PRIMARY KEY,
    payment_name VARCHAR NOT NULL
);

CREATE TABLE dim_rate (
    rate_key  BIGINT PRIMARY KEY,
    rate_name VARCHAR NOT NULL
);

CREATE TABLE dim_location (
    location_key BIGINT PRIMARY KEY,
    zone         VARCHAR,
    borough      VARCHAR,
    service_zone VARCHAR
);

CREATE TABLE dim_time (
    time_key     BIGINT PRIMARY KEY,
    datetime     TIMESTAMP,
    date         DATE,
    year         INTEGER,
    month        INTEGER,
    month_name   VARCHAR,
    day          INTEGER,
    day_of_week  INTEGER,
    day_name     VARCHAR,
    hour         INTEGER,
    is_weekend   BOOLEAN,
    is_peak_hour BOOLEAN,
    quarter      INTEGER
);

-- 3. Recreate fact table (schema mới — đã bỏ store_and_fwd_flag, mta_tax, improvement_surcharge)
CREATE TABLE fact_trip (
    trip_id               VARCHAR PRIMARY KEY,
    vendor_key            BIGINT,
    pickup_time_key       BIGINT,
    dropoff_time_key      BIGINT,
    pickup_location_key   BIGINT,
    dropoff_location_key  BIGINT,
    payment_key           BIGINT,
    rate_key              BIGINT,
    passenger_count       BIGINT,
    trip_distance         DOUBLE PRECISION,
    trip_duration_min     DOUBLE PRECISION,
    fare_amount           DOUBLE PRECISION,
    extra                 DOUBLE PRECISION,
    tip_amount            DOUBLE PRECISION,
    tip_ratio             DOUBLE PRECISION,
    tolls_amount          DOUBLE PRECISION,
    congestion_surcharge  DOUBLE PRECISION,
    airport_fee           DOUBLE PRECISION,
    cbd_congestion_fee    DOUBLE PRECISION,
    total_amount          DOUBLE PRECISION,
    pickup_date           DATE
);

-- Index hỗ trợ query phổ biến
CREATE INDEX idx_fact_trip_pickup_date        ON fact_trip (pickup_date);
CREATE INDEX idx_fact_trip_pickup_location    ON fact_trip (pickup_location_key);
CREATE INDEX idx_fact_trip_vendor             ON fact_trip (vendor_key);

SELECT 'Schema reset completed successfully.' AS status;
