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