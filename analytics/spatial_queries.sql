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

-- Determines which current fire detections fall inside a historical burn area
-- Fire behaves differently inside burn scars vs in unburned forest
SELECT
    detection_id,
    detection_date,
    brightness,
    confidence,
    fire_name,
    fire_year,
    ST_Distance(f.geom::geography, ST_Boundary(p.geom)::geography) / 1000 as km_from_edge
FROM raw_fire_detections f
JOIN fire_perimeters p ON ST_Within(f.geom, p.geom)
WHERE detection_date >= CURRENT_DATE - INTERVAL '14 days'
ORDER BY detection_date DESC;

-- Considers the boundaries of historical burn scars and determines whether detections are within 10km of a perimeter boundary
SELECT
    detection_id,
    detection_date,
    brightness,
    confidence,
    fire_name,
    fire_year,
    ST_Distance(f.geom::geography, ST_Boundary(p.geom)::geography) / 1000 as km_outside_boundary
FROM raw_fire_detections f
JOIN fire_perimeters p ON ST_DWithin(f.geom::geography, p.geom::geography, 10000)
WHERE NOT ST_Within(f.geom, p.geom)
    AND detection_date >= CURRENT_DATE - INTERVAL '14 days'
ORDER BY km_outside_boundary DESC;


-- Clusters nearby detections into likely fires
SELECT 
    detection_id,
    detection_date,
    latitude,
    longitude,
    brightness,
    confidence,
    ST_ClusterDBSCAN(ST_Transform(geom, 26913), eps := 5000, minpoints := 2) OVER () as cluster_id
FROM raw_fire_detections
WHERE detection_date >= CURRENT_DATE - INTERVAL '14 days'
ORDER BY cluster_id NULLS LAST, brightness DESC;


-- Group clusters together and store one centroid as the source of the fire to illustrate on maps
-- Wraps above in a CTE and then groups by cluster_id
WITH clustered AS (
    SELECT 
        detection_id,
        detection_date,
        latitude,
        longitude,
        brightness,
        confidence,
        ST_ClusterDBSCAN(ST_Transform(geom, 26913), eps := 5000, minpoints := 2) OVER () as cluster_id
    FROM raw_fire_detections
    WHERE detection_date >= CURRENT_DATE - INTERVAL '14 days'
    ORDER BY cluster_id NULLS LAST, brightness DESC
)
SELECT 
    cluster_id,
    COUNT(clustered.detection_id),
    AVG(clustered.longitude) AS centroid_lon,
    AVG(clustered.latitude) AS centroid_lat,
    MAX(clustered.brightness) AS max_brightness,
    AVG(clustered.brightness) AS avg_brightness,
    MIN(detection_date) AS first_detected,
    MAX(detection_date) AS last_detected,
    bool_or(confidence='h') AS has_high_confidence
FROM clustered
WHERE cluster_id IS NOT NULL
GROUP BY cluster_id
ORDER BY max_brightness DESC;


-- Divides CO into a grid and then counts the detections per cell over the last 30 days
-- Limitation to note, degree-based cells aren't exactly equal area so lower latitude cells
-- Will be larger than higher latitude cells
SELECT
    ST_X(ST_SnapToGrid(geom, 0.5)) AS cell_lon,
    ST_Y(ST_SnapToGrid(geom, 0.5)) AS cell_lat,
    COUNT(*) AS detection_count,
    AVG(brightness) AS avg_brightness,
    MAX(frp) AS max_frp,
    MIN(detection_date) AS early_date,
    MAX(detection_date) AS last_date
FROM raw_fire_detections
WHERE detection_date >=CURRENT_DATE - INTERVAL '30 days'
GROUP BY ST_SnapToGrid(geom, 0.5);


-- Group detections by the hour of day they were recorded
SELECT 
    COUNT(*) AS detection_count,
    AVG(brightness) AS avg_brightness,
    (LEFT(detection_time, LENGTH(detection_time) - 2))::integer AS hour_of_day
FROM raw_fire_detections
GROUP BY (LEFT(detection_time, LENGTH(detection_time) - 2))::integer
ORDER BY (LEFT(detection_time, LENGTH(detection_time) - 2))::integer


-- Create a rolling average to show whether detections are increasing or decreasing over time
WITH daily_counts AS (
    SELECT
        detection_date,
        COUNT(*) AS detection_count
    FROM raw_fire_detections
    GROUP BY detection_date
)
SELECT 
    detection_count,
    detection_date,
    LAG(detection_count, 1) OVER (
        ORDER BY detection_date) AS previous_day,
    AVG(detection_count) OVER (
        ORDER BY detection_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)
        AS rolling_3_day_average,
    detection_count - LAG(detection_count, 1) OVER (
        ORDER BY detection_date) AS day_over_day_change
FROM daily_counts
ORDER BY detection_date DESC;


-- Creates a summary of each active cluster from the past 48 hours
WITH clustered AS (
    SELECT 
        detection_id,
        detection_date,
        latitude,
        longitude,
        brightness,
        confidence,
        ST_ClusterDBSCAN(ST_Transform(geom, 26913), eps := 5000, minpoints := 2) OVER () as cluster_id
    FROM raw_fire_detections
    WHERE detection_date >= CURRENT_DATE - INTERVAL '2 days'
    ORDER BY cluster_id NULLS LAST, brightness DESC
),
cluster_summary AS (
    SELECT 
        cluster_id,
        COUNT(clustered.detection_id) AS detection_count,
        AVG(clustered.longitude) AS centroid_lon,
        AVG(clustered.latitude) AS centroid_lat,
        MAX(clustered.brightness) AS max_brightness,
        AVG(clustered.brightness) AS avg_brightness,
        MIN(detection_date) AS first_detected,
        MAX(detection_date) AS last_detected,
        bool_or(confidence='h') AS has_high_confidence,
        ST_SetSRID(ST_MakePoint(AVG(longitude), AVG(latitude)), 4326) AS centroid_geom
    FROM clustered
    WHERE cluster_id IS NOT NULL
    GROUP BY cluster_id
)
SELECT
    cs.cluster_id,
    cs.detection_count,
    cs.centroid_lon,
    cs.centroid_lat,
    cs.max_brightness,
    cs.avg_brightness,
    cs.first_detected,
    cs.last_detected,
    cs.has_high_confidence,
    CASE WHEN fp.fire_name IS NOT NULL THEN true ELSE false END AS near_burn_perimeter,
    fp.fire_name AS nearest_perimeter
FROM cluster_summary cs
LEFT JOIN fire_perimeters fp
    ON ST_DWithin(cs.centroid_geom::geography, fp.geom::geography, 50000)
ORDER BY cs.max_brightness DESC;


-- Explain and analyze for performance analysis and confirm GiST usage
EXPLAIN ANALYZE
SELECT
    detection_id,
    detection_date,
    latitude,
    longitude,
    brightness,
    confidence,
    ST_Distance(
        geom::geography,
        ST_SetSRID(ST_MakePoint(-105.2705, 40.0150), 4326)::geography
    ) / 1000 as distance_km
FROM raw_fire_detections
ORDER BY geom <-> ST_SetSRID(ST_MakePoint(-105.2705, 40.0150), 4326)
LIMIT 5;
