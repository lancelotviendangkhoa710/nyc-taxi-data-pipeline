CREATE TABLE IF NOT EXISTS fact_trip (
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

CREATE INDEX IF NOT EXISTS idx_fact_trip_pickup_date     ON fact_trip (pickup_date);
CREATE INDEX IF NOT EXISTS idx_fact_trip_pickup_location ON fact_trip (pickup_location_key);
CREATE INDEX IF NOT EXISTS idx_fact_trip_vendor          ON fact_trip (vendor_key);

