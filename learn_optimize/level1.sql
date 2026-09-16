SELECT DATE(tpep_pickup_datetime) AS pickup_day,
    COUNT(*) AS total_trips,
    SUM(total_amount) AS total_revenue
FROM `nyc_taxi_raw.yellow_taxi_raw`
GROUP BY 1
ORDER BY pickup_day;
SELECT PULocationID,
    COUNT(*) AS total_trips
FROM `nyc_taxi_raw.yellow_taxi_raw`
GROUP BY 1
ORDER BY total_trips DESC
LIMIT 10;
SELECT VendorID,
    SUM(total_amount) AS total_revenue,
    AVG(trip_distance) AS avg_distance
FROM `nyc_taxi_raw.yellow_taxi_raw`
GROUP BY 1;


SELECT VendorID, tpep_pickup_datetime, trip_distance, total_amount
 FROM `nyc_taxi_raw.yellow_taxi_raw`
QUALIFY ROW_NUMBER() OVER (PARTITION BY VendorID ORDER BY trip_distance DESC) = 1



WITH aggregated_trips AS (
    -- Bước 1: Aggregate theo PULocationID trên bảng raw
    SELECT 
        PULocationID,
        COUNT(*) AS total_trips,
        SUM(total_amount) AS total_revenue
    FROM `nyc_taxi_raw.yellow_taxi_raw`
    WHERE pickup_date BETWEEN '2025-06-01' AND '2025-06-30'
    GROUP BY PULocationID
)
-- Bước 2 & 3: Viết tiếp query nạp aggregated_trips JOIN với taxi_zone_lookup theo Borough
SELECT 
    z.Borough,
    SUM(a.total_trips) AS total_trips,
    SUM(a.total_revenue) AS total_revenue
FROM aggregated_trips a
JOIN `nyc_taxi.taxi_zone_lookup` z
  ON a.PULocationID = z.LocationID
GROUP BY z.Borough



