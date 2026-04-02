# This script takes the full burn area boundaries file, parses it by the keyword of interest
# and then pushes that boundary to the Postgres database

# Import packages
import geopandas as gpd
from sqlalchemy import create_engine, text
import os
import logging
from dotenv import load_dotenv

# Load the environment and start the processing clock
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Load fire perimeters from MTBS shapefile to PostgreSQL
# For testing, hardcoding variables for the Cameron Peak 2020 fire
def load_fire_perimeters(shapefile_path: str, fire_names: list, years: list, state: str, database_url: str):
    # Read in the geopandas file
    gdf = gpd.read_file(shapefile_path, engine = 'pyogrio')
    gdf['year'] = gdf['Ig_Date'].dt.year
    
    # Establish empty records loaded count
    records_loaded = 0
    engine = create_engine(database_url)

    for f in fire_names:
        for y in years:
            fires = gdf[gdf['Incid_Name'].str.contains(f, case=False, na=False) & (gdf['year']==y) &
                        (gdf['BurnBndLat'].astype(float) >=36.99) & 
                        (gdf['BurnBndLat'].astype(float) <=41.00) & 
                        (gdf['BurnBndLon'].astype(float) >=-109.06) & 
                        (gdf['BurnBndLon'].astype(float) <=-102.04)].copy()
            if fires.empty:
                logger.warning(f"No parameters found for {f} in {y}")
                continue
            fires = fires.to_crs(epsg=4326)
            #print(fires[['Incid_Name', 'year', 'BurnBndAc']].to_string())
            
            with engine.connect() as conn:
                for _, row in fires.iterrows():
                    try:
                        conn.execute(text('''
                                          INSERT INTO fire_perimeters
                                            (fire_name, fire_year, state, acres, geom)
                                          VALUES
                                            (:name, :year, :state, :acres, ST_Multi(ST_SetSRID(ST_GeomFromText(:geom), 4326)))
                                          '''), {
                                              'name': row['Incid_Name'],
                                              'year': int(row['year']),
                                              'state': state,
                                              'acres': float(row['BurnBndAc']),
                                              'geom': row['geometry'].wkt
                                          })
                        records_loaded +=1
                        conn.commit()
                        logger.info(f"Loaded {row['Incid_Name']} {row['year']}")
                    except Exception as e:
                        logger.error(f"Failed to load {row['Incid_Name']}: {e}")
                        continue
                
    return records_loaded
        


# Sets the variable names for the Cameron Peak fire case study
def main():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error('DATABASE_URL not found in .env')
        return
    
    shapefile_path = os.getenv(
        "MTBS_SHAPEFILE_PATH",
        "/tmp/mtbs/mtbs_perims_DD.shp",
    )
    load_fire_perimeters(
        shapefile_path=shapefile_path,
        fire_names=['CAMERON PEAK', 'CREEK', 'EAST TROUBLESOME'],
        years=[2020],
        state='CO',
        database_url=database_url
    )


if __name__ == '__main__':
    main()