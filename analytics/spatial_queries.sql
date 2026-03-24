-- Colorado Fire Watch Spatial Queries

-- Reads in NASA Firms data and checks its plausability 
SELECT
    COUNT(*) as total_detections,
    MIN(detection_date) as earliest,
    MAX(detection_date) as latest,
    AVG(brightness) as avg_brightness,
    COUNT(CASE WHEN confidence  = 'h' THEN 1 END) as high_confidence,
    COUNT(CASE WHEN confidence  = 'n' THEN 1 END) as nominal_confidence,
    COUNT(CASE WHEN confidence  = 'l' THEN 1 END) as low_confidence,
    COUNT(CASE WHEN geom is NULL THEN 1 END) as null_geometry,
    COUNT(CASE WHEN latitude < 36.99
                OR latitude > 41.00
                OR longitude < -109.06
                OR longitude > -102.04 THEN 1 END) as outside_colorado
FROM raw_fire_detections;

-- Find the nearest detections to Boulder
-- Note that this is all thermal anomalies, not just confirmed fires
SELECT
    detection_id,
    detection_date,
    latitude,
    longitude,
    brightness,
    confidence,
    ST_Distance(
        geom::geography,
        ST_SetSRID(ST_MakePoint(-105.2705,40.0150), 4326)::geography
    ) / 1000 as distance_km
FROM raw_fire_detections
ORDER BY geom <-> ST_SetSRID(ST_MakePoint(-105.2705, 40.0150), 4326) -- Uses the spatial index w/o scanning the whole table
LIMIT 5;


-- This query focuses on any high-confidence anomalies detected that are within 50 km of Boulder
-- Returned zero is still a valid response. Can adjust interval time and distance to include more detections
SELECT
    detection_id,
    detection_date,
    brightness,
    confidence,
    ST_Distance(
        geom::geography,
        ST_SetSRID(ST_MakePoint(-105.2705, 40.0150), 4326)::geography
    )/1000 as distance_km
FROM raw_fire_detections
WHERE ST_DWithin(
    geom::geography,
    ST_SetSRID(ST_MakePoint(-105.2705, 40.0150), 4326)::geography,
    50000 -- This is for 50 km, can change
)
AND confidence = 'h'
AND detection_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY geom <-> ST_SetSRID(ST_MakePoint(-105.2705, 40.0150), 4326);