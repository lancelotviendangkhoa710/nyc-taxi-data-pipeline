CREATE TABLE IF NOT EXISTS dim_location (
    location_key BIGINT PRIMARY KEY,
    zone         VARCHAR,
    borough      VARCHAR,
    service_zone VARCHAR
);

