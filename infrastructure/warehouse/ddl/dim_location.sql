CREATE OR REPLACE TABLE dim_location (
    location_key INT64 OPTIONS(description="Mã vùng (LocationID) từ TLC"),
    zone STRING OPTIONS(description="Tên khu vực taxi (Taxi Zone)"),
    borough STRING OPTIONS(description="Tên quận (Borough)"),
    service_zone STRING OPTIONS(description="Khu vực dịch vụ (Service Zone)")
);
