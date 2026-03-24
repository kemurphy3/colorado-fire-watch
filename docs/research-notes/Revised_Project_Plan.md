Colorado Fire Watch: Full Revised Project Plan

Project Vision
Colorado Fire Watch is a two layer wildfire intelligence system for Colorado.
The operational layer ingests satellite data, weather observations, and active fire detections daily to produce a current fire danger assessment updated on Sentinel-2's five day revisit cycle. This layer synthesizes existing data sources into a publicly accessible, clearly visualized risk map.
The hyperspectral intelligence layer uses NEON's airborne observation data to detect early drought stress and bark beetle damage in conifers using spectral absorption features that standard vegetation indices miss. This capability is validated against the 2020 Cameron Peak Fire where pre-fire NEON data exists, then transferred to Sentinel-2 through a crosswalk model for statewide application between NEON flight years.
The system is research grade, not operationally certified. It is designed to demonstrate what is possible with publicly available data and domain expertise, contribute a novel scientific method to the fire science community, and serve as a public resource for Colorado residents and researchers.

Guiding Principles
Every phase must produce something that can be pushed to the public repo and ideally to coloradofirewatch.com. No phase produces only internal work product.
Uncertainty is always visible. Every risk score, model output, and index value carries documented uncertainty that is communicated to users.
Interpretability over performance. A model whose outputs can be explained to a fire manager is more valuable than a marginally more accurate black box.
Honest documentation of limitations is a feature not a weakness. The scientific community and fire professionals trust systems that acknowledge what they cannot do.

User Personas
Persona 1: Fire Operations Manager
Uses the system 3 to 5 days ahead of potential fire weather for resource pre-positioning. Needs geographic specificity, update recency, and jurisdictional context. Does not need to understand the methodology. Does need to trust the output.
Persona 2: Fuels Specialist or Forest Ecologist
Uses the hyperspectral stress layer for annual fuel treatment planning. Needs accuracy, uncertainty quantification, methodology documentation, and data download capability. Will read the technical documentation.
Persona 3: Informed Colorado Resident
Wants to understand fire risk in their community. Needs plain language explanations and a simple interface. Will not read technical documentation but will read a well-written summary.

Data Sources and Licenses
Before any code is written these licenses must be read and documented in DATA_LICENSES.md.
NASA FIRMS: Open with attribution. Cite NASA FIRMS and the specific satellite product.
NEON: Requires acknowledgment of NSF funding award EF-1929435 and the NEON program. Review current data use policy at data.neonscience.org before publication.
Sentinel-2: Open under Copernicus Data Policy. Requires attribution to European Space Agency and Copernicus program.
MTBS: USGS public domain. Cite USGS and the MTBS program.
USGS 3DEP Elevation: Public domain. Cite USGS.
NOAA Weather: Public domain. Cite NOAA and specific data product.
OpenStreetMap: Open Database License. Requires share-alike for derived works.

Phase 0: Foundation Hardening
Purpose: Close current gaps in what is already built before adding new complexity.
Deliverable: Clean, tested, documented foundation that is ready for public viewing.

Step 0.1: Unit tests for validate_detections
Create tests/test_validate.py.
Write exactly these five tests:
Test 1: DataFrame with null latitude returns empty DataFrame.
Test 2: DataFrame with null longitude returns empty DataFrame.
Test 3: DataFrame with latitude outside Colorado bounds returns empty DataFrame.
Test 4: DataFrame with brightness below 200 returns empty DataFrame.
Test 5: Valid DataFrame with 10 records all passing constraints returns DataFrame with 10 records and all original columns intact.
Add pytest==7.4.0 to requirements.txt.
Update .github/workflows/validate.yml to add a pytest step after the syntax check:
yaml- name: Run unit tests
  run: pytest tests/ -v
  env:
    DATABASE_URL: postgresql://postgres:firewatch@localhost:5432/firewatch
    FIRMS_API_KEY: test_key
```

Commit message: "Add unit tests for validate_detections"

Measurable outcome: pytest passes in GitHub Actions. Green checkmark on repo.

---

**Step 0.2: Create .dockerignore**

Create .dockerignore in project root with these contents:
```
.env
.git
.github
__pycache__
*.pyc
*.pyo
tests/
docs/
*.md
data/
logs/
.pytest_cache/
Commit message: "Add .dockerignore to reduce image size"
Measurable outcome: Docker image build time decreases. Image size decreases.

Step 0.3: Pipeline run logging table
Add to schema.sql:
sqlCREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id          SERIAL PRIMARY KEY,
    pipeline_name   VARCHAR(50),
    started_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at    TIMESTAMP,
    status          VARCHAR(20),
    records_fetched INTEGER,
    records_loaded  INTEGER,
    error_message   TEXT
);
Update main() in firms_ingest.py to insert a row into pipeline_runs at the start and update it at the end with status, counts, and any error message.
This is your data quality monitoring foundation. You can query pipeline_runs to see if anything failed silently.
Commit message: "Add pipeline run logging"
Measurable outcome: pipeline_runs table populated after each run. One row per execution with accurate status.

Step 0.4: Email alerting on pipeline failure
Create utils/alerting.py. Write a send_alert function that uses Python's smtplib to send an email via Gmail when called with a subject and message body.
Update main() in firms_ingest.py to call send_alert if the pipeline fails or if records_loaded is zero when records were expected.
Store Gmail credentials in .env as ALERT_EMAIL and ALERT_PASSWORD. Add these to .gitignore.
Add ALERT_EMAIL and ALERT_PASSWORD to docker-compose.yml environment section.
Commit message: "Add email alerting on pipeline failure"
Measurable outcome: Send a test alert manually and confirm receipt.

Step 0.5: DATA_LICENSES.md
Create docs/DATA_LICENSES.md. Review and document the license requirements for each data source listed above. Include the specific attribution text required for each source.
This file must be complete before the repo goes public.
Commit message: "Add data licenses documentation"
Measurable outcome: File exists with complete attribution requirements for all data sources.

Step 0.6: Legal disclaimer
Create DISCLAIMER.md in the project root. Base the language on USGS standard disclaimer language. Key elements to include:
This system is research grade and has not been operationally certified by any fire management agency.
Data may be delayed, incomplete, or inaccurate.
Decisions about life safety should never be based solely on this system.
This system does not replace official fire danger ratings from the National Weather Service or the National Fire Danger Rating System.
Commit message: "Add legal disclaimer"
Measurable outcome: Disclaimer file exists. Link to it from README.

Step 0.7: Commit and push everything
Verify GitHub Actions passes. Verify Docker builds cleanly. Verify pipeline runs successfully.
At the end of Phase 0 the repo is clean, tested, legally documented, and ready for public viewing. Make it public after this step if desired. The current scope is honest and the foundation is solid.

Phase 1: NEON Data Foundation
Purpose: Establish the NEON data ingestion layer. This is the foundation for everything scientifically novel in the project.
Deliverable: Working NEON data ingestion pipeline with CHM, hyperspectral indices, and CDW data for NIWO in the database.

Step 1.1: NEON API research and data inventory
Spend two hours at data.neonscience.org. Do not write any code. Document answers to these specific questions:
What NEON flight dates are available for NIWO between 2018 and 2023?
What are the download URLs for DP3.30014.001 hyperspectral reflectance for NIWO 2019?
What are the download URLs for DP3.30015.001 CHM for NIWO 2019?
What are the available dates for DP1.10058.001 CDW survey data for NIWO?
What is the file size of a typical NIWO hyperspectral HDF5 file?
How many flight lines does a typical NIWO acquisition consist of?
Create docs/NEON_DATA_INVENTORY.md with answers to all six questions plus the specific download URLs.
Commit message: "Add NEON data inventory for NIWO"
Measurable outcome: NEON_DATA_INVENTORY.md exists with complete and accurate information.

Step 1.2: Schema additions for NEON data
Add four tables to schema.sql.
Table 1: neon_flight_metadata
Tracks metadata about each NEON AOP acquisition.
sqlCREATE TABLE IF NOT EXISTS neon_flight_metadata (
    flight_id       SERIAL PRIMARY KEY,
    site_code       VARCHAR(10),
    flight_date     DATE,
    year            INTEGER,
    flight_lines    INTEGER,
    epsg_code       INTEGER,
    bounds_west     FLOAT,
    bounds_east     FLOAT,
    bounds_south    FLOAT,
    bounds_north    FLOAT,
    data_product    VARCHAR(20),
    local_path      TEXT,
    ingested_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
Table 2: neon_chm_tiles
Metadata for each CHM raster tile.
sqlCREATE TABLE IF NOT EXISTS neon_chm_tiles (
    tile_id         SERIAL PRIMARY KEY,
    flight_id       INTEGER REFERENCES neon_flight_metadata(flight_id),
    tile_easting    INTEGER,
    tile_northing   INTEGER,
    resolution_m    FLOAT,
    local_path      TEXT,
    geom            GEOMETRY(Polygon, 4326)
);
Table 3: neon_spectral_indices
One row per pixel per flight for derived spectral indices.
sqlCREATE TABLE IF NOT EXISTS neon_spectral_indices (
    pixel_id        SERIAL PRIMARY KEY,
    flight_id       INTEGER REFERENCES neon_flight_metadata(flight_id),
    pixel_easting   FLOAT,
    pixel_northing  FLOAT,
    ndvi            FLOAT,
    ndwi_1240       FLOAT,
    red_edge_pos    FLOAT,
    water_content   FLOAT,
    dry_matter      FLOAT,
    geom            GEOMETRY(Point, 4326)
) PARTITION BY RANGE (flight_id);
Note: Partition neon_spectral_indices by flight_id from the start. This table will be large.
Table 4: cdw_measurements
Ground plot CDW survey data.
sqlCREATE TABLE IF NOT EXISTS cdw_measurements (
    cdw_id          SERIAL PRIMARY KEY,
    site_code       VARCHAR(10),
    plot_id         VARCHAR(20),
    survey_date     DATE,
    decay_class     INTEGER,
    diameter_cm     FLOAT,
    length_m        FLOAT,
    volume_m3_ha    FLOAT,
    geom            GEOMETRY(Point, 4326)
);
Add spatial indexes for all geometry columns.
Run docker-compose down -v and docker-compose up --build. Verify all tables created.
Update GitHub Actions to verify new tables exist after schema loads.
Commit message: "Add NEON data tables to schema"
Measurable outcome: Four new tables visible in PostgreSQL. GitHub Actions passes.

Step 1.3: CHM ingestion script
Create ingestion/neon_chm_ingest.py.
The script has the same three function structure as firms_ingest.py.
fetch_neon_chm: Downloads CHM tiles for a given site and year from the NEON API. Saves files to data/neon/chm/ which is in .gitignore. Returns list of downloaded file paths.
validate_chm: Opens each GeoTIFF with rasterio. Checks file is not corrupted. Checks coordinate reference system is UTM. Checks no-data values are handled. Checks value range is physically plausible for canopy height, 0 to 60 meters. Returns list of valid file paths.
load_chm_metadata: Extracts bounding box, resolution, and CRS from each file. Reprojects bounding box to WGS84 for the geom column. Inserts metadata into neon_chm_tiles table.
main function reads NEON_API_TOKEN from .env. Calls three functions in order. Logs to pipeline_runs table.
Commit message: "Add NEON CHM ingestion script"
Measurable outcome: Running the script downloads NIWO 2019 CHM files and populates neon_chm_tiles table with correct metadata. Verify by querying tile count and checking bounding boxes overlap with NIWO location.

Step 1.4: Spectral indices calculation script
Create ingestion/neon_spectral_ingest.py.
This is the most computationally intensive script in the project. Process one flight line at a time to manage memory.
Structure:
load_hyperspectral_flightline: Opens one HDF5 file using h5py. Reads the reflectance array, wavelength array, and coordinate metadata. Returns numpy array and metadata.
calculate_indices: Takes the reflectance array and wavelength array. Calculates five indices for every pixel.
NDVI: (R800 minus R670) divided by (R800 plus R670). Find the array indices for 800nm and 670nm by matching against the wavelength array. Do not hardcode band numbers. Band positions vary slightly between flights.
NDWI 1240: (R860 minus R1240) divided by (R860 plus R1240). Uses 1240nm water absorption feature.
Red edge position: Find the wavelength of maximum first derivative of reflectance between 700nm and 740nm. This requires calculating the derivative of the spectrum across that range. Shifts toward shorter wavelengths under stress.
Water content index: R970 divided by R900. Ratio of reflectance at two wavelengths sensitive to liquid water content.
Dry matter index: 1 minus R2200 divided by R2200 max. Uses 2200nm absorption depth associated with dry plant material.
For each index mask out pixels where reflectance values are outside physically plausible range defined as 0 to 1 after scaling. Set masked pixels to null.
load_indices_to_db: Converts pixel coordinates from UTM to WGS84. Bulk inserts into neon_spectral_indices using the staging table pattern from firms_ingest.py.
main function processes all flight lines for a given site and year. Logs progress per flight line. Updates pipeline_runs table.
Commit message: "Add NEON spectral indices calculation script"
Measurable outcome: neon_spectral_indices table populated with NIWO 2019 data. Verify row count is greater than 1 million pixels. Verify NDVI values fall between minus 1 and 1. Verify red edge position values fall between 700 and 740nm.

Step 1.5: CDW ingestion script
Create ingestion/neon_cdw_ingest.py.
CDW data from NEON is tabular CSV. Download via NEON API for DP1.10058.001 at NIWO for all available years.
Structure mirrors other ingestion scripts. Fetch, validate column presence and value ranges, load to cdw_measurements table.
Validation checks: plot_id not null, coordinates within NIWO bounding box, diameter values positive, volume values positive.
Commit message: "Add NEON CDW ingestion script"
Measurable outcome: cdw_measurements table populated. Query returns plot locations within NIWO bounds. Verify against known NIWO plot count from NEON documentation.

Step 1.6: First spatial queries connecting FIRMS and NEON
Create analytics/spatial_queries.sql. Write three queries.
Query 1: Fire detections near NEON sites.
sql-- Find FIRMS detections within 50km of NEON site centroids
-- Demonstrates spatial join capability
WITH neon_sites AS (
    SELECT 
        site_code,
        ST_Centroid(ST_Extent(geom)) as site_centroid
    FROM neon_chm_tiles
    GROUP BY site_code
)
SELECT 
    f.detection_date,
    f.latitude,
    f.longitude,
    f.brightness,
    f.confidence,
    n.site_code,
    ST_Distance(
        f.geom::geography,
        n.site_centroid::geography
    ) / 1000 as distance_km
FROM raw_fire_detections f
CROSS JOIN LATERAL (
    SELECT site_code, site_centroid
    FROM neon_sites
    ORDER BY f.geom <-> site_centroid
    LIMIT 1
) n
WHERE ST_DWithin(f.geom::geography, n.site_centroid::geography, 50000)
ORDER BY f.detection_date DESC, distance_km;
Query 2: Detection density by 10km grid cell across Colorado.
sql-- Aggregate detections into 10km grid cells
-- Shows spatial distribution of fire activity
SELECT 
    ST_SnapToGrid(geom, 0.1) as grid_cell,
    COUNT(*) as detection_count,
    AVG(brightness) as avg_brightness,
    MAX(frp) as max_frp,
    COUNT(CASE WHEN confidence = 'h' THEN 1 END) as high_confidence_count
FROM raw_fire_detections
WHERE detection_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY ST_SnapToGrid(geom, 0.1)
ORDER BY detection_count DESC;
Query 3: Seasonal fire pattern for Colorado.
sql-- Monthly detection counts and average brightness
-- Shows annual fire season pattern
SELECT 
    EXTRACT(MONTH FROM detection_date) as month,
    TO_CHAR(detection_date, 'Month') as month_name,
    COUNT(*) as total_detections,
    AVG(brightness) as avg_brightness,
    COUNT(CASE WHEN confidence = 'h' THEN 1 END) as high_confidence_count
FROM raw_fire_detections
GROUP BY EXTRACT(MONTH FROM detection_date), TO_CHAR(detection_date, 'Month')
ORDER BY month;
Commit message: "Add spatial queries connecting FIRMS detections to NEON sites"
Measurable outcome: All three queries run without error in psql. Results are plausible given known fire patterns in Colorado.

Step 1.7: README update after Phase 1
Rewrite README.md using this structure:
Section 1: What this is. Two paragraphs. First describes the operational layer. Second describes the hyperspectral intelligence layer. Include the Cameron Peak hook.
Section 2: Why I built this. Keep your existing text. It is good. Add one sentence about the drought stressed conifer problem.
Section 3: What works right now. Bullet list of exactly what is functional. FIRMS ingestion, NEON CHM and spectral indices for NIWO, CDW measurements, spatial queries, Docker, CI/CD.
Section 4: What I am building next. Brief roadmap pointing to the Sentinel crosswalk and Cameron Peak validation.
Section 5: Architecture. Simple diagram using ASCII art or text showing the two layer system.
Section 6: Tech stack. Accurate list of what is actually used.
Section 7: Data sources. Each source with attribution language from DATA_LICENSES.md.
Section 8: Running locally. Step by step instructions for cloning the repo and running docker-compose up.
Section 9: Disclaimer. One paragraph. Link to DISCLAIMER.md.
Commit message: "Update README to reflect Phase 1 completion"
After this commit the repo is ready to be public.

Phase 2: Sentinel Data Integration
Purpose: Bring in the satellite data that enables statewide coverage and the crosswalk training dataset.
Deliverable: Concurrent NEON and Sentinel-2 acquisitions aligned and ready for crosswalk model training.

Step 2.1: Google Earth Engine setup
Create a Google Earth Engine account at earthengine.google.com. Request research access. This may take a few days to approve.
Spend one week learning the GEE Python API. Complete these specific tutorials from the GEE documentation: Image basics, Image collections, Reducing image collections, and Export.
Create a Jupyter notebook at notebooks/gee_exploration.ipynb documenting your learning. This is not production code. It is your working scratch space.
Commit message: "Add GEE exploration notebook"
Measurable outcome: GEE access approved. Notebook runs without error and displays a Sentinel-2 image over Colorado.

Step 2.2: Find concurrent acquisitions
Create scripts/find_concurrent_acquisitions.py.
Using the GEE Python API, query Sentinel-2 Surface Reflectance image collection for images over the NIWO bounding box within 14 days of each NEON flight date identified in Step 1.1.
Filter to cloud cover below 20 percent using the CLOUDY_PIXEL_PERCENTAGE property.
Output a CSV to docs/CONCURRENT_ACQUISITIONS.csv with columns: neon_flight_date, sentinel_acquisition_date, days_apart, cloud_cover_percent, sentinel_image_id.
Commit message: "Add concurrent acquisition finder script"
Measurable outcome: CONCURRENT_ACQUISITIONS.csv exists with at least one valid match within 14 days of a 2019 NEON flight with less than 20 percent cloud cover.

Step 2.3: Sentinel atmospheric correction and preprocessing
Create ingestion/sentinel_ingest.py.
For each concurrent acquisition identified in Step 2.2, process the Sentinel-2 image through these steps in order using GEE.
Step A: Apply Sen2Cor atmospheric correction if not already applied in the Surface Reflectance product. Surface Reflectance products are already atmospherically corrected so verify the product level before applying additional correction.
Step B: Apply cloud and cloud shadow mask using the SCL band included in Sentinel-2 Surface Reflectance products. Mask pixels classified as cloud, cloud shadow, saturated or defective, and dark area pixels.
Step C: Apply topographic correction using the SRTM elevation model to normalize for illumination differences caused by Colorado's mountainous terrain.
Step D: Resample all bands to 10m resolution. Sentinel-2 has bands at 10m, 20m, and 60m native resolution. Resample 20m bands to 10m using bilinear interpolation.
Step E: Clip to NIWO bounding box.
Export processed image as a Cloud Optimized GeoTIFF to local storage in data/sentinel/.
Add sentinel_acquisitions table to schema.sql with metadata including acquisition date, cloud cover, processing steps applied, and local file path.
Commit message: "Add Sentinel-2 preprocessing pipeline"
Measurable outcome: At least one processed Sentinel-2 image for NIWO stored locally. Metadata in sentinel_acquisitions table. Verify cloud mask removed obvious cloud pixels by visual inspection.

Step 2.4: BRDF normalization
Create transformations/brdf_normalize.py.
Download MODIS MCD43A1 BRDF parameter product for the acquisition date using GEE. This product provides the parameters needed to normalize reflectance to nadir view equivalent.
Apply Ross-Thick Li-Sparse BRDF normalization to both the NEON reflectance data and the Sentinel data. This adjusts both datasets to what they would look like if viewed from directly above at solar noon, removing angular effects.
This step is critical for the crosswalk to be scientifically valid. Without it the angular difference between NEON aircraft viewing geometry and Sentinel satellite viewing geometry introduces systematic bias.
Document the normalization approach in docs/METHODS.md.
Commit message: "Add BRDF normalization for NEON and Sentinel data"
Measurable outcome: BRDF normalized versions of both datasets saved. Document mean reflectance change before and after normalization to verify the correction had a measurable effect.

Step 2.5: Spatial alignment
Create transformations/align_neon_sentinel.py.
Reproject NEON spectral indices to the same UTM zone as the Sentinel image. NEON uses UTM but the zone may differ from Sentinel's tile zone.
Resample NEON 1m pixels to match Sentinel's 10m grid using a mean aggregation. This creates the mixed pixel issue acknowledged in the remote sensing review. Handle it using a fractional cover decomposition.
For each 10m Sentinel pixel calculate the fraction of NEON pixels within it that are sunlit canopy, shaded canopy, and background using the CHM data. A pixel with 80 percent canopy cover gets a different weighting than one with 20 percent canopy cover when comparing to Sentinel reflectance.
Store fractional cover fractions in a new neon_pixel_fractions table.
Output a paired dataset where each row has NEON derived spectral indices at 10m aggregated scale alongside Sentinel band values for the same pixel on the concurrent acquisition date.
Commit message: "Add spatial alignment pipeline for NEON and Sentinel data"
Measurable outcome: Paired dataset created as a parquet file in data/processed/. Row count matches expected pixel count for NIWO at 10m resolution. Verify correlation between NEON NDVI at 10m and Sentinel NDVI is above 0.7 as a sanity check.

Phase 3: Crosswalk and Stress Models
Purpose: Build the models that transfer hyperspectral detection capability to Sentinel and enable statewide application.
Deliverable: Trained crosswalk model, drought stress model, and beetle kill classification model with documented validation metrics.

Step 3.1: Spatial cross validation framework
Create models/utils/spatial_cv.py.
Implement a spatial blocking cross validation approach. Divide the NIWO study area into spatial blocks using k-means clustering on pixel coordinates. Create five folds where each fold holds out one spatial cluster as the test set.
This prevents spatial autocorrelation from inflating validation metrics. Adjacent pixels are correlated. If you randomly split them into train and test you are testing on data that is informationally similar to the training data. Spatial blocking forces the model to generalize to held-out geographic areas.
Write a SpatialCrossValidator class with fit and score methods compatible with scikit-learn's cross_val_score interface.
Document the approach in docs/METHODS.md. Include a figure showing the spatial fold boundaries.
Commit message: "Add spatial cross validation framework"
Measurable outcome: SpatialCrossValidator runs without error on synthetic data. Fold boundaries are visually distinct geographic areas when plotted.

Step 3.2: Feature preparation
Create models/crosswalk/prepare_features.py.
Load the paired dataset from Step 2.5.
Apply the 500m boundary buffer to exclude pixels near the Cameron Peak fire perimeter boundary. These boundary pixels have the most uncertain burned or not burned labels.
Define predictor variables: NDWI 1240, red edge position, water content index, dry matter index, canopy height from CHM, fractional canopy cover from Step 2.5.
Define target variables: All 13 Sentinel-2 bands for the crosswalk model. Drought stress binary label for the stress model.
Define the drought stress binary label. Pixels inside the Cameron Peak fire perimeter that burned at high or moderate severity according to MTBS burn severity data are positive examples. Pixels outside the perimeter at similar elevation and forest type are negative examples.
Save train and test splits as parquet files. Document the split methodology.
Commit message: "Add feature preparation for crosswalk and stress models"
Measurable outcome: Training and test parquet files exist. Class balance documented for the stress classification task.

Step 3.3: Ridge regression crosswalk baseline
Create models/crosswalk/ridge_regression.py.
Fit one ridge regression model per Sentinel-2 band using the SpatialCrossValidator from Step 3.1.
Report R squared, RMSE, and bias for each band.
Create a visualization of predicted versus observed for each band as a scatter plot saved to docs/figures/.
Save trained models as pickle files in models/saved/.
Establish minimum acceptable performance threshold: R squared above 0.5 for at least 8 of 13 bands. If this threshold is not met document why and what would be needed to meet it.
Commit message: "Add ridge regression crosswalk baseline with spatial CV"
Measurable outcome: Results CSV with per-band metrics. Visualization exists. Performance threshold met or documented reason for failure.

Step 3.4: Gradient boosting crosswalk comparison
Create models/crosswalk/gradient_boosting.py.
Fit XGBoost models for the same prediction task using the same spatial cross validation folds.
Compare to ridge regression. If mean R squared improvement across bands is less than 0.05, use ridge regression. Document the decision.
Commit message: "Add gradient boosting crosswalk comparison"
Measurable outcome: Comparison table exists in docs/. Decision documented with reasoning.

Step 3.5: Drought stress detection model
Create models/stress/drought_stress.py.
Using Cameron Peak as positive examples and matched control pixels as negative examples, fit a random forest classifier.
Features: All six spectral indices plus CHM height plus fractional canopy cover.
Use SpatialCrossValidator for validation. Report precision, recall, F1, and area under ROC curve.
Use RMNP as a completely held-out test site to assess generalization. Train on NIWO. Test on RMNP. Document the performance drop if any.
This generalization test is the scientific credibility test. If the model only works at NIWO it is not a transferable methodology. If it works at RMNP it is.
Save trained model as pickle file.
Commit message: "Add drought stress detection model with spatial CV and held-out site validation"
Measurable outcome: Model trained and saved. Validation metrics documented. RMNP generalization results documented honestly including any performance degradation.

Step 3.6: Bark beetle kill classification
Create models/stress/beetle_kill.py.
Colorado bark beetle kill has three spectral stages. Green attack, the first year when trees appear healthy but are dying. Red attack, years two and three when needles turn red. Gray attack, subsequent years when gray wood is exposed.
Each stage has documented spectral signatures in the literature. Use these as training targets rather than learning them from scratch.
Implement a rule-based classifier first using known spectral thresholds for each stage. Then test whether a data-driven classifier improves on the rule-based approach.
Output is a four-class label per pixel: no beetle damage, green attack, red attack, gray attack.
This is a parallel output to the drought stress model. Both feed into the final risk score separately.
Save trained model and document the rule-based thresholds in METHODS.md.
Commit message: "Add bark beetle kill classification model"
Measurable outcome: Beetle kill classification runs on NIWO 2019 data. Output map shows spatially coherent patterns that are visually plausible given known beetle kill history in the area.

Step 3.7: CDW proxy model
Create models/fuel/cdw_proxy.py.
Using CDW ground plot measurements as targets and AOP structural metrics as predictors.
Predictors: Canopy height from CHM, gap fraction calculated from CHM, surface roughness calculated from lidar returns, snag fraction estimated from spectral mortality indicators, basal area estimated from CHM.
Target: CDW volume in Mg per hectare from ground plots.
Fit a random forest regression model with spatial cross validation.
Report R squared and RMSE. Acknowledge uncertainty. The documented uncertainty range is plus or minus 30 percent of the estimate. Propagate this uncertainty into the risk score by calculating risk scores at the low, median, and high CDW estimates and reporting the resulting risk score range.
Commit message: "Add CDW proxy model with uncertainty quantification"
Measurable outcome: CDW estimates at plot locations within 25 percent of measured values on average. Uncertainty ranges documented.

Step 3.8: Minimal FastAPI layer
Create api/main.py.
Two endpoints only at this stage.
Endpoint 1: GET /risk/current returns current risk scores within a given bounding box as GeoJSON.
Endpoint 2: GET /pipeline/status returns the last five rows of pipeline_runs table showing recent pipeline health.
Add fastapi and uvicorn to requirements.txt.
Add an api service to docker-compose.yml that runs the FastAPI app on port 8000.
Commit message: "Add minimal FastAPI layer with risk and status endpoints"
Measurable outcome: curl localhost:8000/pipeline/status returns valid JSON with recent pipeline run data.

Phase 4: Cameron Peak Validation
Purpose: Validate the stress detection approach against a real fire event. This is the scientific proof of concept.
Deliverable: A validated finding showing whether pre-fire stress indices flag Cameron Peak area with higher values than control areas. Honest documentation of results regardless of outcome.

Step 4.1: Cameron Peak fire perimeter ingestion
Create ingestion/mtbs_ingest.py.
Download Cameron Peak fire perimeter from MTBS at mtbs.gov. The fire name is Cameron Peak. The year is 2020. The state is Colorado.
Load the perimeter polygon into fire_perimeters table.
Verify the loaded area matches the known extent of 208,913 acres.
Commit message: "Add Cameron Peak fire perimeter from MTBS"
Measurable outcome: fire_perimeters table contains Cameron Peak perimeter. Area calculation confirms correct extent.

Step 4.2: Burn severity classification
Download the MTBS burn severity raster for Cameron Peak. This classifies burned areas into unburned, low, moderate, and high severity.
Create a burn_severity table in schema.sql. Load the raster values per pixel.
For the drought stress validation use only moderate and high severity pixels as positive examples. Unburned and low severity pixels are excluded from the training label as ambiguous.
Commit message: "Add burn severity data for Cameron Peak validation"
Measurable outcome: burn_severity table populated. Distribution of severity classes matches published statistics for Cameron Peak.

Step 4.3: Control site selection
Identify control areas using these criteria. Similar elevation range to the Cameron Peak burn area, 2400 to 3500 meters. Similar dominant forest type, subalpine conifer. Within Colorado. Did not experience a major fire between 2018 and 2022.
The San Juan Mountains region meets these criteria. Specifically the Weminuche Wilderness area has similar forest composition without a coincident major fire.
Document the control area selection rationale in METHODS.md.
Commit message: "Document control site selection for Cameron Peak validation"
Measurable outcome: Control area bounding box defined and documented. Rationale written.

Step 4.4: Pre-fire stress analysis
Run the drought stress model from Step 3.5 on NIWO 2019 data covering the Cameron Peak burn area.
Run the same model on the control area using whatever NEON data is available. If no NEON data exists for the control area apply the Sentinel crosswalk to estimate the stress indices.
Compare stress index distributions between the Cameron Peak area and the control area.
Key question: Are stress indices significantly higher in the Cameron Peak area in 2019 than in the control area? If yes, what is the effect size? If no, document why not and what this means for the methodology.
Create visualizations showing the spatial distribution of stress indices overlaid on the eventual fire perimeter.
Write the findings as a plain language summary in docs/CAMERON_PEAK_FINDINGS.md and a technical summary in docs/METHODS.md.
Commit message: "Add Cameron Peak pre-fire stress analysis results"
Measurable outcome: CAMERON_PEAK_FINDINGS.md exists with honest results. Technical validation metrics documented. Visualizations created and committed to docs/figures/.

Step 4.5: Risk scoring function
Create models/risk/risk_score.py.
Build the transparent weighted scoring function combining all model outputs.
Components:
Water content index from Sentinel crosswalk: 25 percent initial weight.
Drought stress model probability: 25 percent initial weight.
Bark beetle kill stage: 20 percent initial weight. Green attack gets moderate penalty. Red attack gets high penalty. Gray attack gets lower penalty as fuels have partially decomposed.
CDW proxy estimate: 15 percent initial weight.
Slope from elevation data: 10 percent initial weight.
Time since last fire using decay function: 5 percent initial weight.
Normalize each component to 0 to 1 before weighting. Final score is 0 to 100.
Calculate risk scores at three CDW uncertainty levels to propagate model uncertainty into the final output. Report score range as well as point estimate.
Optimize weights using Cameron Peak burned versus not burned labels. Use a simple grid search over weight combinations. Document the optimized weights and the improvement over initial weights.
Commit message: "Add transparent risk scoring function with uncertainty propagation"
Measurable outcome: Risk scores calculated for Cameron Peak area. Distribution of scores inside versus outside fire perimeter shows measurable discrimination. Area under ROC curve above 0.65.

Step 4.6: Make repo public
After Step 4.5 the project has a validated scientific finding, documented methodology, working code, and honest uncertainty quantification. This is the threshold for public release.
Verify DATA_LICENSES.md is complete. Verify DISCLAIMER.md is present. Verify README accurately describes the project. Verify GitHub Actions passes.
Make the repository public.
Announce on any relevant channels. The NEON user community, the fire science community on Twitter or Mastodon, and the open geospatial community are all relevant audiences.

Phase 5: Statewide Application
Purpose: Scale the validated approach from NIWO to all of Colorado.
Deliverable: Statewide risk map updated on Sentinel's five day revisit cycle.

Step 5.1: Statewide Sentinel pipeline
Extend sentinel_ingest.py to download current Sentinel-2 data for all of Colorado.
Colorado spans multiple Sentinel-2 tiles. Identify all tiles with coverage over Colorado. Handle tile boundaries by buffering and mosaicking.
Implement scheduling using APScheduler running inside the existing Docker container. Schedule the Sentinel download every five days aligned with Sentinel's revisit cycle.
Update the pipeline failure alert from Phase 0 to specifically alert when a scheduled Sentinel run fails.
Commit message: "Add scheduled statewide Sentinel acquisition pipeline"
Measurable outcome: Sentinel data downloaded for all Colorado tiles. Mosaicking produces a seamless Colorado-wide image. Scheduled run executes without manual intervention.

Step 5.2: Statewide spectral index calculation
Apply the spectral index calculations from Phase 1 to each new Sentinel acquisition using the crosswalk model from Phase 3.
For direct Sentinel indices like NDVI calculate them natively from Sentinel bands.
For indices requiring hyperspectral resolution like red edge position and water content index apply the crosswalk model to estimate them from Sentinel bands.
Store outputs in a statewide_risk_indices table partitioned by acquisition date.
Commit message: "Add statewide spectral index calculation from Sentinel"
Measurable outcome: statewide_risk_indices table populated for at least one complete Colorado acquisition. Row count matches expected pixel count for Colorado at 10m resolution.

Step 5.3: Statewide risk map generation
Apply the risk scoring function from Phase 4 to the statewide spectral indices.
Include FIRMS detections from the last 30 days as a contextual layer.
Include terrain data from USGS 3DEP for slope calculation.
Output as a Cloud Optimized GeoTIFF stored in cloud storage. AWS S3 or Google Cloud Storage both work. Estimated size is 50GB per year at monthly cadence.
Implement a STAC catalog for the risk map outputs. This makes the data discoverable and accessible to other researchers using standard tools.
Commit message: "Add statewide risk map generation with STAC catalog"
Measurable outcome: Cloud Optimized GeoTIFF exists for at least one complete Colorado risk map. STAC catalog is queryable.

Phase 6: Visualization and Website
Purpose: Make the system accessible to all three user personas through coloradofirewatch.com.
Deliverable: Live website with operational risk map, hyperspectral stress layer, and Cameron Peak case study.

Step 6.1: Streamlit app architecture
Create visualization/app.py.
Four views implemented with a sidebar navigation.
View 1: Current Risk Map. Colorado choropleth showing latest risk scores. Color scale from green to red. Timestamp showing when data was last updated prominently displayed. Toggle to show FIRMS active detections overlay. Toggle to show NEON site boundaries.
View 2: Hyperspectral Stress Layer. Shows drought stress and beetle kill classification for NEON sites. Clearly labeled with the flight year the data represents. Opacity shows model confidence. Disclaimer that this data is updated annually not daily.
View 3: Cameron Peak Case Study. Side by side maps of 2019 pre-fire stress indices and actual burn perimeter. Plain language explanation of what the hyperspectral data showed before the fire. Key finding stated clearly.
View 4: About and Methods. Plain language description of the system for Persona 3. Link to technical methods documentation for Persona 2. Disclaimer text from DISCLAIMER.md.
Deploy to Streamlit Community Cloud which is free for public repos. Connect to coloradofirewatch.com domain.
Commit message: "Add Streamlit app with four views"
Measurable outcome: coloradofirewatch.com loads and displays current risk data. All four views functional. Timestamps visible on all data layers.

Step 6.2: Uncertainty visualization
Implement opacity-based uncertainty display on the risk map.
High confidence areas where the CDW model uncertainty is low and the stress model probability is above 0.7 are fully saturated.
Low confidence areas where CDW uncertainty is high or stress model probability is between 0.4 and 0.6 are desaturated to 50 percent opacity.
Add a legend explaining what opacity represents.
Commit message: "Add uncertainty visualization to risk map"
Measurable outcome: Visual distinction between high and low confidence areas is clear in the map display.

Step 6.3: Cameron Peak case study page content
Write the narrative for the case study page. This is science communication not technical documentation.
Lead with the hook: NEON flew over this area in the summer of 2019. The fire started in August 2020. Here is what the data showed before anyone knew what was coming.
Explain what the stress indices measure in plain language. Not spectral absorption features. Something like: these measurements detect whether the trees have enough water in their needles. Drought stressed trees have fundamentally different chemistry than healthy trees even when they still look green from the outside.
Show the before and after maps. Label them clearly with dates. Explain what the colors mean.
State the finding directly: did the stress indices flag the Cameron Peak area before the fire? What does that mean for early warning.
Acknowledge uncertainty. This is one fire. More validation is needed. But the pattern is consistent with the hypothesis.
Commit message: "Add Cameron Peak case study narrative content"
Measurable outcome: Case study page tells a coherent story that a Colorado resident with no remote sensing background can follow.

Phase 7: Documentation and Scientific Communication
Purpose: Make the project credible, reproducible, and discoverable by the scientific and fire management community.
Deliverable: Complete methods documentation, reproducibility package, and community outreach.

Step 7.1: METHODS.md technical documentation
Write docs/METHODS.md covering every modeling decision made in Phases 3 and 4.
Sections:
Data sources and preprocessing. What you downloaded, what corrections you applied, why.
Spectral index calculations. Exact band wavelengths used for each index. Rationale for each index.
BRDF normalization approach. Why it is necessary. What method you used.
Crosswalk model. Training data, validation approach, performance metrics, limitations.
Drought stress model. Features, training data, spatial cross validation approach, validation metrics, RMNP generalization results.
Bark beetle classification. Spectral thresholds used, classification stages, validation approach.
CDW proxy model. Features, training data, uncertainty quantification.
Risk scoring function. All weights, normalization approach, optimization method, uncertainty propagation.
Cameron Peak validation. Methodology, results, honest assessment of limitations.
This document should be detailed enough that another researcher could reproduce your results.
Commit message: "Add complete technical methods documentation"
Measurable outcome: METHODS.md exists and is complete. Every modeling decision is documented with rationale.

Step 7.2: Reproducibility package
Create a Makefile in the project root that documents how to reproduce each phase from scratch.
makefilesetup:
    docker-compose up --build

ingest-firms:
    docker-compose run ingest python ingestion/firms_ingest.py

ingest-neon:
    docker-compose run ingest python ingestion/neon_chm_ingest.py
    docker-compose run ingest python ingestion/neon_spectral_ingest.py
    docker-compose run ingest python ingestion/neon_cdw_ingest.py

train-models:
    docker-compose run ingest python models/crosswalk/ridge_regression.py
    docker-compose run ingest python models/stress/drought_stress.py
    docker-compose run ingest python models/stress/beetle_kill.py
    docker-compose run ingest python models/fuel/cdw_proxy.py

validate:
    docker-compose run ingest python models/risk/risk_score.py

run-app:
    streamlit run visualization/app.py
Commit message: "Add Makefile for reproducibility"
Measurable outcome: Running make setup followed by make ingest-firms produces the same results as running docker-compose up manually.

Step 7.3: Community outreach
Write a post for the NEON user community forum describing the project and inviting feedback from other researchers who have worked with NEON AOP data.
Write a plain language blog post about the Cameron Peak findings. Post it on the coloradofirewatch.com about page or a linked blog.
Share on relevant communities. The OpenGeoHub community, the NEON user community, the fire science community on academic social networks.
This is not self-promotion. It is how open science works. Other researchers can identify methodological issues, suggest improvements, and potentially collaborate.
Measurable outcome: At least two community posts made. At least one response from a researcher or practitioner with domain knowledge.

Immediate Next Steps Starting Today
Given your current session here is the exact sequence.
Today, in order:
Write unit tests for validate_detections. This is Step 0.1. Estimated time 45 minutes.
Create .dockerignore. Step 0.2. Estimated time 5 minutes.
Add pipeline_runs table to schema and update firms_ingest.py to log runs. Step 0.3. Estimated time 30 minutes.
Write spatial queries in analytics/spatial_queries.sql. Step 1.6. Estimated time 45 minutes. You can write these even before the NEON data exists because Query 1 can run with just the FIRMS data and show zero results for NEON spatial joins until Phase 1 is complete.
Update README. Step 1.7 partial. Write what is accurate now. Estimated time 30 minutes.
That is two hours and forty-five minutes of concrete work that closes real gaps and moves the project forward.

What do you want to start with? Sonnet 4.6ExtendedClaude is AI and can make mistakes. Please double-check responses