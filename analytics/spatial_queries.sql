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