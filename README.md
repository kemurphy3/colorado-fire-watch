# Colorado Fire Watch

A wildfire intelligence system for Colorado combining near-real-time satellite fire detection with historical burn analysis.

## What this is

Living in Colorado, wildfire season feels inevitable. Most fire risk tools focus on weather patterns and simple vegetation indices, but they miss important spatial patterns in the detection data itself.

This project works on two levels.

The first is an operational layer that ingests near-real-time NASA satellite fire detections for Colorado, stores them in a spatial database, and enables spatial queries that answer specific questions: where detections cluster into likely fires, what the nearest detection is to a given location, which detections fall inside or near previous burn perimeters, and how activity changes over time.

The second is a scientific layer in development. NEON's Airborne Observation Platform flies over field sites in Colorado and captures hyperspectral imagery at 1-meter resolution. Traditional vegetation indices like NDVI often show drought-stressed conifers as healthy even when they are effectively dry fuel. The hyperspectral water content and red edge indices catch that stress earlier. The Cameron Peak Fire burned through terrain near NEON's Niwot Ridge site in 2020, and NEON has pre-fire flight data from 2019. That before-and-after dataset is the validation case for this approach. The goal is to transfer that detection capability to Sentinel-2 satellite data through a spectral crosswalk, enabling statewide vulnerability mapping that updates on Sentinel's five-day revisit cycle.

## Why I built this

The Cameron Peak Fire in 2020 burned right through terrain near NEON's NIWO site. That site has detailed hyperspectral and lidar data from the year before. That is a rare and valuable dataset for understanding what pre-fire vegetation stress actually looks like in the data.

Standard NDVI would show those forests as healthy in 2019. The question this project is investigating is whether stress-sensitive hyperspectral indices would have shown something different before the fire started.

I spent several years building and maintaining the AOP processing pipelines at NEON, so I understand this data from the inside. This project is what I kept thinking we could do with it.

## What works right now
### Data pipeline

Near-real-time NASA FIRMS satellite fire detections for Colorado load automatically into a PostGIS spatial database. The pipeline validates data quality, prevents duplicates, logs every run, and sends an alert if something fails.

### Historical fire perimeters

Cameron Peak 2020, East Troublesome 2020, and Grizzly Creek 2020 are loaded from MTBS. These enable spatial queries asking whether current detections are occurring inside or near previous burn areas.

### Spatial queries

A set of PostGIS queries that convert raw detections into usable signals: nearest detection to a location, detections within a radius, clustering detections into likely fires, and spatial joins with historical burn perimeters.

###  Infrastructure

Runs locally with a single docker-compose up. Automated validation and tests run on every code push.

## What is being built next

Clustering detections into likely fires rather than individual points. Point-in-polygon joins showing which detections fall inside historical burn perimeters. A full operational situation report combining all of the above.

After that, the hyperspectral work begins. Loading NEON AOP data for Niwot Ridge 2019, calculating stress indices that NDVI misses, and comparing the pre-fire signal against where Cameron Peak actually burned.

Eventually a live map at coloradofirewatch.com showing current detections, historical context, and the vulnerability layer derived from the hyperspectral analysis.

## Running locally

You need Docker installed.
```bash
git clone https://github.com/kemurphy3/colorado-fire-watch
cd colorado-fire-watch
cp .env.example .env
```

Edit `.env` with your credentials:
```
FIRMS_API_KEY=your_nasa_firms_api_key_here
DATABASE_URL=postgresql://postgres:firewatch@localhost:5432/firewatch
ALERT_EMAIL=your_email_here
ALERT_PASSWORD=your_gmail_app_password_here
```

Get a free FIRMS API key at https://firms.modaps.eosdis.nasa.gov/api/

Then start the pipeline:
```bash
docker-compose up
```

Fire detections for Colorado load into the database automatically. Connect to PostgreSQL at localhost:5432, database firewatch, user postgres to run queries directly.

## Data sources
NASA FIRMS VIIRS SNPP NRT: Near-real-time active fire detections. Citation: NASA FIRMS.
MTBS Burned Area Boundaries: Historical fire perimeters 1984-2024. Citation: USGS and the MTBS program.
NEON AOP (planned): Hyperspectral and lidar data from Colorado field sites. Funded by NSF award EF-1929435.
Sentinel-2 (planned): ESA Copernicus program surface reflectance imagery

## Disclaimer
This system is research grade and has not been operationally certified by any fire management agency. Data may be delayed, incomplete, or inaccurate. Decisions about life safety should never be based solely on this system.