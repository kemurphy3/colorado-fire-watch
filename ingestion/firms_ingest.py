# Import libraries
import os
import logging
from datetime import datetime

from sqlalchemy import create_engine, text
import requests
import pandas as pd
from dotenv import load_dotenv
from io import StringIO

# Load in .env file
load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fetch_firms_data(api_key: str, days_back: int = 7, bounding_box = (-109.06, 36.99, -102.04, 41.00)):
    """ 
    This function reads in the api_key and pulls data from the number of days assigned to the days_back variable
    Args:
        api_key: NASA FIRMS API key
        days_back: Number of days of data to fetch, max is 10 for free tier
    Returns:
        Dataframe of raw fire detections, or empty dataframe is the fetch fails
    """
    bbox_str = ",".join(str(coord) for coord in bounding_box)
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{api_key}/VIIRS_SNPP_NRT/{bbox_str}/{days_back}"

    # Make the HTTP request
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        logger.info(f"Fetched {len(df)} fire detections")
        return df
    except requests.exceptions.RequestException as e:
        logger.error(f"Something went wrong: {e}")
        return pd.DataFrame()
    

def validate_detections(df: pd.DataFrame, bounding_box = (-109.06, 36.99, -102.04, 41.00)):
    """
    This function acts as a QA gate. It checks the necessary columns exist upon ingest, that the coordinates are not null,
    that the coordinates are within bounds (starting with within CO), and that the values are physically plausible.

    It returns only validated detections.
    """
    # Assign coordinates
    west, south, east, north = bounding_box

    # Establish required format
    required_columns = ['latitude', 'longitude', 'bright_ti4', 'frp', 'confidence', 'acq_date', 'acq_time']
    
    # Track record count and how many rows are removed for which reason
    initial_count = len(df)
    logger.info(f"There are initially {initial_count} entries")

    missing_columns = [col for col in required_columns if col not in df.columns] # Checks format
    if missing_columns:
        logger.error(f"Missing required columns: {missing_columns}")
        return pd.DataFrame()

    df = df.dropna(subset=['latitude', 'longitude']) # Drops na in lat / long columns
    na_drop_count = len(df)
    logger.info(f"There are now {na_drop_count} entries")

    df = df[
        (df['latitude'] >= south) &
        (df['latitude'] <= north) &
        (df['longitude'] >= west) &
        (df['longitude'] <= east)
    ] # Makes sure coordiantes are within bounds

    # Check brightness plausibility
    df = df[(df['bright_ti4'] >= 200) & (df['bright_ti4'] <= 500)]

    # Check FRP plausibility
    df = df[df['frp'] > 0]

    logger.info(f"{len(df)} of {initial_count} records passed all QA checks")
    return df


def load_to_postgres(df: pd.DataFrame, database_url: str):
    """
    This function takes the validated DataFrame and writes it to the PostgreSQL database.

    It connects to the database, inserts each row, and returns a count.
    """
    # Check that the DataFrame exists and isn't empty
    if df.empty:
        return 0
    
    # Create the database engine
    engine = create_engine(database_url)

    # Create a count to track records loaded. Initialized to 0.
    records_loaded = 0

    # Insert one row into raw_detections_table
    insert_sql = text("""
        INSERT INTO raw_fire_detections(
                source_satellite,
                detection_date,
                detection_time,
                latitude,
                longitude,
                brightness,
                confidence,
                frp,
                geom
            ) VALUES (
                :satellite,
                :detection_date,
                :detection_time,
                :latitude,
                :longitude,
                :brightness,
                :confidence,
                :frp,
                ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)
            )
    """)
    
    # Roll into loop. Log error, but do not exit if single row does not ingest
    with engine.connect() as conn:
        for _, row in df.iterrows():
            try:
                conn.execute(insert_sql, {
                    'satellite': 'VIIRS_SNPP',
                    'detection_date': row['acq_date'],
                    'detection_time': row['acq_time'],
                    'latitude': float(row['latitude']),
                    'longitude': float(row['longitude']),
                    'brightness': row['bright_ti4'],
                    'confidence': str(row['confidence']),
                    'frp': float(row['frp']),
                })
                records_loaded += 1
            except Exception as e:
                logger.error(f"Failed to insert row: {e}")
                continue
        conn.commit()
    
    logger.info(f"There were {records_loaded} records loaded")
    return records_loaded
    

def main():
    """
    This function reads in the data from FIRMS using fetch_firms_data. 
    Then it runs the DataFrame through the QA checks in validate_detections.
    Then that cleaned data gets passed to load_to_postgres
    """
    
    # Read in the values from .env file
    api_key = os.getenv('FIRMS_API_KEY')
    database_url = os.getenv('DATABASE_URL')

    # Check validity of values from .env
    if not api_key:
        logger.error(f"The FIRMS API key not found in the environment")
        return 
    if not database_url:
        logger.error(f"The database url not found in the environment")
        return 
    
    start_time = datetime.now()
    raw_df = fetch_firms_data(api_key)
    qa_df = validate_detections(raw_df, database_url)
    records_loaded_count = load_to_postgres(qa_df)

    if records_loaded_count > 0:
        logger.info(f"{records_loaded_count} loaded into the database successfully")
    
    elapsed = datetime.now() - start_time
    logger.info(f"FIRMS ingest completed in {elapsed.total_seconds():.1f} seconds")

if __name__ == "__main__":
    main()