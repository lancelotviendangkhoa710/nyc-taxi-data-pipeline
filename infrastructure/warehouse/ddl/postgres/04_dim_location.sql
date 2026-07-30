-- PostgreSQL DDL for dim_location
CREATE TABLE IF NOT EXISTS dim_location (
    location_key INTEGER PRIMARY KEY,
    zone TEXT NOT NULL,
    borough TEXT,
    service_zone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE dim_location IS 'Dimension: NYC taxi location zones';
COMMENT ON COLUMN dim_location.location_key IS 'Mã vùng (LocationID) từ TLC';
COMMENT ON COLUMN dim_location.zone IS 'Tên khu vực taxi (Taxi Zone)';
COMMENT ON COLUMN dim_location.borough IS 'Tên quận (Borough)';
COMMENT ON COLUMN dim_location.service_zone IS 'Khu vực dịch vụ (Service Zone)';