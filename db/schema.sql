-- Enable PostGIS extension
-- This adds spatial data types and functions to PostgreSQL
-- Without this, geometry columns and ST_ functions do not exist
CREATE EXTENSION IF NOT EXISTS postgis;

-- Raw fire detections from NASA FIRMS satellite data
-- This is the first table data lands in, unmodified from the source
-- We keep it raw intentionally so we always have the original
CREATE TABLE IF NOT EXISTS raw_fire_detections (
    detection_id    SERIAL PRIMARY KEY,
    ingested_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_satellite VARCHAR(20),
    detection_date  DATE,
    detection_time  VARCHAR(10),
    latitude        FLOAT,
    longitude       FLOAT,
    brightness      FLOAT,
    scan            FLOAT,
    track           FLOAT,
    confidence      VARCHAR(10),
    frp             FLOAT,
    geom            GEOMETRY(Point, 4326),
    CONSTRAINT unique_detection UNIQUE (latitude, longitude, detection_date, detection_time)
);

-- Historical fire perimeters from MTBS
-- These are polygon boundaries of past fires
-- We use these to ask: are current detections near previous burns?
CREATE TABLE IF NOT EXISTS fire_perimeters (
    perimeter_id    SERIAL PRIMARY KEY,
    fire_name       VARCHAR(100),
    fire_year       INTEGER,
    state           VARCHAR(5),
    acres           FLOAT,
    cause           VARCHAR(50),
    geom            GEOMETRY(MultiPolygon, 4326)
);

-- Risk scores calculated from detections plus context
-- This is the output layer, what downstream users consume
-- JSONB stores the contributing factors as flexible key-value pairs
CREATE TABLE IF NOT EXISTS fire_risk_scores (
    score_id            SERIAL PRIMARY KEY,
    calculated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    detection_id        INTEGER REFERENCES raw_fire_detections(detection_id),
    latitude            FLOAT,
    longitude           FLOAT,
    risk_score          FLOAT,
    risk_category       VARCHAR(20),
    contributing_factors JSONB,
    geom                GEOMETRY(Point, 4326)
);

-- Spatial indexes on geometry columns
-- Without these, spatial queries scan every row
-- With these, PostGIS can jump directly to nearby features
-- This is the difference between a query taking 0.1s vs 30s at scale
CREATE INDEX IF NOT EXISTS idx_fire_detections_geom
    ON raw_fire_detections USING GIST(geom);

CREATE INDEX IF NOT EXISTS idx_fire_perimeters_geom
    ON fire_perimeters USING GIST(geom);

CREATE INDEX IF NOT EXISTS idx_risk_scores_geom
    ON fire_risk_scores USING GIST(geom);

-- Date index on detections for time-based filtering
-- We will frequently query "detections in the last 7 days"
-- This index makes those queries fast
CREATE INDEX IF NOT EXISTS idx_fire_detections_date
    ON raw_fire_detections(detection_date);
