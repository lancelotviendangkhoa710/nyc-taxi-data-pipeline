CREATE TABLE IF NOT EXISTS dim_time (
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

