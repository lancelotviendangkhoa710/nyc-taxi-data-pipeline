-- PostgreSQL DDL for fact_trip
CREATE TABLE IF NOT EXISTS fact_trip (
    trip_id TEXT PRIMARY KEY,
    vendor_key INTEGER NOT NULL REFERENCES dim_vendor(vendor_key),
    pickup_time_key INTEGER NOT NULL REFERENCES dim_time(time_key),
    dropoff_time_key INTEGER NOT NULL REFERENCES dim_time(time_key),
    pickup_location_key INTEGER NOT NULL REFERENCES dim_location(location_key),
    dropoff_location_key INTEGER NOT NULL REFERENCES dim_location(location_key),
    payment_key INTEGER NOT NULL REFERENCES dim_payment(payment_key),
    rate_key INTEGER NOT NULL REFERENCES dim_rate(rate_key),
    passenger_count INTEGER,
    trip_distance DOUBLE PRECISION,
    trip_duration_min DOUBLE PRECISION,
    fare_amount DOUBLE PRECISION,
    extra DOUBLE PRECISION,
    mta_tax DOUBLE PRECISION,
    tip_amount DOUBLE PRECISION,
    tip_ratio DOUBLE PRECISION,
    tolls_amount DOUBLE PRECISION,
    improvement_surcharge DOUBLE PRECISION,
    total_amount DOUBLE PRECISION,
    congestion_surcharge DOUBLE PRECISION,
    airport_fee DOUBLE PRECISION,
    cbd_congestion_fee DOUBLE PRECISION,
    store_and_fwd_flag TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_fact_trip_pickup_time ON fact_trip(pickup_time_key);
CREATE INDEX IF NOT EXISTS idx_fact_trip_dropoff_time ON fact_trip(dropoff_time_key);
CREATE INDEX IF NOT EXISTS idx_fact_trip_vendor ON fact_trip(vendor_key);
CREATE INDEX IF NOT EXISTS idx_fact_trip_pickup_location ON fact_trip(pickup_location_key);
CREATE INDEX IF NOT EXISTS idx_fact_trip_dropoff_location ON fact_trip(dropoff_location_key);
CREATE INDEX IF NOT EXISTS idx_fact_trip_payment ON fact_trip(payment_key);
CREATE INDEX IF NOT EXISTS idx_fact_trip_rate ON fact_trip(rate_key);

COMMENT ON TABLE fact_trip IS 'Fact table: NYC taxi trip records';
COMMENT ON COLUMN fact_trip.trip_id IS 'Mã surrogate key duy nhất cho mỗi chuyến đi';
COMMENT ON COLUMN fact_trip.vendor_key IS 'FK liên kết DIM_VENDOR';
COMMENT ON COLUMN fact_trip.pickup_time_key IS 'FK liên kết DIM_TIME (Thời gian đón khách)';
COMMENT ON COLUMN fact_trip.dropoff_time_key IS 'FK liên kết DIM_TIME (Thời gian trả khách)';
COMMENT ON COLUMN fact_trip.pickup_location_key IS 'FK liên kết DIM_LOCATION (Điểm đón)';
COMMENT ON COLUMN fact_trip.dropoff_location_key IS 'FK liên kết DIM_LOCATION (Điểm trả)';
COMMENT ON COLUMN fact_trip.payment_key IS 'FK liên kết DIM_PAYMENT';
COMMENT ON COLUMN fact_trip.rate_key IS 'FK liên kết DIM_RATE';
COMMENT ON COLUMN fact_trip.passenger_count IS 'Số lượng hành khách';
COMMENT ON COLUMN fact_trip.trip_distance IS 'Khoảng cách chuyến đi (miles)';
COMMENT ON COLUMN fact_trip.trip_duration_min IS 'Thời gian di chuyển (phút)';
COMMENT ON COLUMN fact_trip.fare_amount IS 'Tiền cước cơ bản';
COMMENT ON COLUMN fact_trip.extra IS 'Phụ phí';
COMMENT ON COLUMN fact_trip.mta_tax IS 'Thuế MTA';
COMMENT ON COLUMN fact_trip.tip_amount IS 'Tiền tip';
COMMENT ON COLUMN fact_trip.tip_ratio IS 'Tỉ lệ tip trên cước';