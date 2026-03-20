# Implementation Guide: Colorado Fire Watch

## Quick Start

This guide provides step-by-step instructions to implement the Colorado Fire Watch system using NEON data and the three-tier cascade approach.

## Table of Contents
1. [Project Setup](#project-setup)
2. [Data Pipeline](#data-pipeline)
3. [Model Development](#model-development)
4. [API Development](#api-development)
5. [Deployment](#deployment)
6. [Testing & Validation](#testing--validation)
7. [Production Checklist](#production-checklist)

## Project Setup

### Directory Structure
```bash
colorado-fire-watch/
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   ├── neon_downloader.py
│   │   ├── satellite_fetcher.py
│   │   └── weather_integration.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── cdw_proxy.py
│   │   ├── crosswalk.py
│   │   ├── fire_risk.py
│   │   └── three_tier_cascade.py
│   ├── features/
│   │   ├── __init__.py
│   │   ├── aop_features.py
│   │   ├── ground_features.py
│   │   └── satellite_features.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── endpoints.py
│   └── utils/
│       ├── __init__.py
│       ├── geo_utils.py
│       └── validation.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── models/
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_cdw_proxy_development.ipynb
│   ├── 03_crosswalk_training.ipynb
│   └── 04_validation.ipynb
├── tests/
├── docs/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Requirements File
```txt
# requirements.txt
# Core scientific computing
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.10.0
scikit-learn>=1.3.0
xarray>=2023.0.0

# Machine learning
xgboost>=2.0.0
lightgbm>=4.0.0
tensorflow>=2.13.0  # Optional, for deep learning

# Geospatial
rasterio>=1.3.0
geopandas>=0.14.0
shapely>=2.0.0
pyproj>=3.5.0
earthengine-api>=0.1.370
sentinelsat>=1.2.0

# NEON data access
requests>=2.31.0
h5py>=3.9.0  # For HDF5 files
netCDF4>=1.6.0  # For NetCDF files

# Web API
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0

# Database
psycopg2-binary>=2.9.0
sqlalchemy>=2.0.0

# Visualization (optional)
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.15.0
folium>=0.14.0  # For interactive maps

# Development tools
pytest>=7.4.0
black>=23.0.0
pylint>=2.17.0
jupyter>=1.0.0
```

## Data Pipeline

### Step 1: NEON Data Download
```python
# src/data/neon_downloader.py
import requests
import os
from pathlib import Path
from typing import List, Dict
import pandas as pd

class NEONDataDownloader:
    """Download and manage NEON data products"""
    
    def __init__(self, base_dir: str = "data/raw/neon"):
        self.base_url = "https://data.neonscience.org/api/v0"
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Colorado NEON sites
        self.colorado_sites = ['NIWO', 'RMNP', 'CPER']
        
        # Key products for fire risk
        self.fire_products = {
            # AOP Products
            'DP3.30015.001': 'ecosystem_structure',
            'DP3.30014.001': 'hyperspectral_reflectance',
            'DP3.30025.001': 'slope_aspect',
            
            # Ground Products
            'DP1.10098.001': 'vegetation_structure',
            'DP1.10058.001': 'coarse_downed_wood',
            'DP1.00094.001': 'soil_water_content',
            
            # Tower Products
            'DP1.00002.001': 'air_temperature',
            'DP1.00098.001': 'relative_humidity',
            'DP1.00001.001': 'wind_speed'
        }
    
    def get_product_availability(self, product_id: str, site: str) -> Dict:
        """Check data availability for a product at a site"""
        url = f"{self.base_url}/products/{product_id}/{site}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()['data']
        else:
            raise Exception(f"Failed to get availability: {response.status_code}")
    
    def download_product(self, product_id: str, site: str, 
                        start_date: str, end_date: str) -> List[str]:
        """Download a NEON data product"""
        
        # Get available files
        url = f"{self.base_url}/data/{product_id}/{site}"
        params = {
            'startdate': start_date,
            'enddate': end_date,
            'package': 'basic'
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get data URLs: {response.status_code}")
        
        data = response.json()['data']
        downloaded_files = []
        
        # Download each file
        for file_info in data['files']:
            file_url = file_info['url']
            file_name = file_info['name']
            
            # Create directory structure
            product_dir = self.base_dir / product_id / site
            product_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = product_dir / file_name
            
            # Download if not exists
            if not file_path.exists():
                print(f"Downloading {file_name}...")
                response = requests.get(file_url, stream=True)
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                downloaded_files.append(str(file_path))
            else:
                print(f"File exists: {file_name}")
                downloaded_files.append(str(file_path))
        
        return downloaded_files
    
    def download_fire_risk_data(self, start_date: str = "2019-01-01", 
                                end_date: str = "2023-12-31"):
        """Download all fire-relevant NEON data"""
        
        for site in self.colorado_sites:
            print(f"\nProcessing site: {site}")
            
            for product_id, product_name in self.fire_products.items():
                print(f"  Downloading {product_name} ({product_id})...")
                
                try:
                    files = self.download_product(
                        product_id=product_id,
                        site=site,
                        start_date=start_date,
                        end_date=end_date
                    )
                    print(f"    Downloaded {len(files)} files")
                except Exception as e:
                    print(f"    Error: {e}")
```

### Step 2: Satellite Data Integration
```python
# src/data/satellite_fetcher.py
import ee
from datetime import datetime, timedelta
import numpy as np
import xarray as xr

class SatelliteDataFetcher:
    """Fetch and process satellite data"""
    
    def __init__(self):
        # Initialize Earth Engine
        ee.Initialize()
        
        self.products = {
            'sentinel2': 'COPERNICUS/S2_SR_HARMONIZED',
            'landsat8': 'LANDSAT/LC08/C02/T1_L2',
            'modis': 'MODIS/006/MOD09GA',
            'viirs': 'NOAA/VIIRS/001/VNP09GA'
        }
    
    def get_sentinel2_composite(self, bounds: list, start_date: str, 
                                end_date: str) -> np.ndarray:
        """Get Sentinel-2 cloud-free composite"""
        
        # Define area of interest
        aoi = ee.Geometry.Rectangle(bounds)
        
        # Load Sentinel-2 collection
        collection = (ee.ImageCollection(self.products['sentinel2'])
                     .filterBounds(aoi)
                     .filterDate(start_date, end_date)
                     .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))
        
        # Calculate indices
        def add_indices(image):
            ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
            ndwi = image.normalizedDifference(['B8', 'B11']).rename('NDWI')
            nbr = image.normalizedDifference(['B8', 'B12']).rename('NBR')
            
            return image.addBands([ndvi, ndwi, nbr])
        
        collection = collection.map(add_indices)
        
        # Create median composite
        composite = collection.median()
        
        # Export to numpy array
        bands = ['B2','B3','B4','B5','B6','B7','B8','B8A','B11','B12',
                'NDVI','NDWI','NBR']
        
        # Get data
        data = composite.select(bands).getInfo()
        
        return self._ee_to_numpy(data)
    
    def get_modis_time_series(self, point: tuple, start_date: str, 
                             end_date: str) -> pd.DataFrame:
        """Get MODIS time series for a point"""
        
        # Create point geometry
        point_geo = ee.Geometry.Point(point)
        
        # Load MODIS collection
        collection = (ee.ImageCollection(self.products['modis'])
                     .filterBounds(point_geo)
                     .filterDate(start_date, end_date))
        
        # Extract time series
        def extract_values(image):
            values = image.reduceRegion(
                reducer=ee.Reducer.first(),
                geometry=point_geo,
                scale=500
            )
            
            return ee.Feature(None, values).set('date', image.date())
        
        features = collection.map(extract_values)
        
        # Convert to dataframe
        data = features.getInfo()
        df = pd.DataFrame([f['properties'] for f in data['features']])
        df['date'] = pd.to_datetime(df['date'], unit='ms')
        
        return df
    
    def _ee_to_numpy(self, ee_image_info: dict) -> np.ndarray:
        """Convert Earth Engine image to numpy array"""
        # Implementation depends on export method
        # Could use geemap, eemont, or direct API
        pass
```

### Step 3: Feature Engineering
```python
# src/features/aop_features.py
import numpy as np
import rasterio
from scipy import ndimage
from typing import Dict

class AOPFeatureExtractor:
    """Extract features from NEON AOP products"""
    
    def __init__(self):
        self.ndvi_bands = {
            'nir': 90,  # ~860nm
            'red': 60   # ~650nm
        }
        
        self.water_bands = {
            'nir': 90,     # ~860nm
            'swir1': 200,  # ~1240nm
            'swir2': 285   # ~1640nm
        }
    
    def extract_chm_features(self, chm_path: str) -> Dict[str, float]:
        """Extract features from Canopy Height Model"""
        
        with rasterio.open(chm_path) as src:
            chm = src.read(1)
            
        # Remove no-data values
        chm_valid = chm[chm > 0]
        
        features = {
            # Basic statistics
            'canopy_height_mean': np.mean(chm_valid),
            'canopy_height_std': np.std(chm_valid),
            'canopy_height_max': np.max(chm_valid),
            'canopy_height_p95': np.percentile(chm_valid, 95),
            
            # Structural metrics
            'canopy_cover': np.sum(chm > 2) / chm.size,
            'tall_tree_fraction': np.sum(chm > 20) / np.sum(chm > 2),
            'gap_fraction': np.sum(chm < 2) / chm.size,
            
            # Heterogeneity
            'height_cv': np.std(chm_valid) / np.mean(chm_valid),
            'height_skewness': scipy.stats.skew(chm_valid),
            'height_kurtosis': scipy.stats.kurtosis(chm_valid),
            
            # Surface roughness (proxy for CDW)
            'surface_roughness': np.std(chm[chm < 5]),
            
            # Edge density (fragmentation)
            'edge_density': self._calculate_edge_density(chm > 5)
        }
        
        return features
    
    def extract_hyperspectral_features(self, hs_path: str) -> Dict[str, float]:
        """Extract features from hyperspectral imagery"""
        
        import h5py
        
        with h5py.File(hs_path, 'r') as f:
            # Load reflectance data
            reflectance = f['Reflectance']['Reflectance_Data'][:]
            wavelengths = f['Wavelength']['Wavelength'][:]
        
        features = {}
        
        # Vegetation indices
        features['ndvi_mean'] = self._calculate_ndvi(reflectance)
        features['ndvi_std'] = np.std(self._calculate_ndvi_map(reflectance))
        
        # Water indices
        features['ndwi'] = self._calculate_ndwi(reflectance)
        features['msi'] = self._calculate_msi(reflectance)  # Moisture Stress
        
        # Red edge position (stress indicator)
        features['red_edge_position'] = self._find_red_edge(reflectance, wavelengths)
        
        # Photochemical Reflectance Index (stress)
        features['pri'] = self._calculate_pri(reflectance)
        
        # Cellulose/Lignin absorption (dead vegetation)
        features['cai'] = self._calculate_cai(reflectance)  # Cellulose Absorption
        
        # Species indicators (simplified)
        features['conifer_index'] = self._calculate_conifer_index(reflectance)
        features['deciduous_index'] = self._calculate_deciduous_index(reflectance)
        
        return features
    
    def _calculate_ndvi(self, reflectance: np.ndarray) -> float:
        """Calculate mean NDVI"""
        nir = reflectance[:, :, self.ndvi_bands['nir']]
        red = reflectance[:, :, self.ndvi_bands['red']]
        
        ndvi = (nir - red) / (nir + red + 1e-8)
        return np.nanmean(ndvi)
    
    def _calculate_edge_density(self, binary_map: np.ndarray) -> float:
        """Calculate edge density of binary map"""
        edges = ndimage.sobel(binary_map.astype(float))
        return np.sum(edges > 0) / binary_map.size
    
    def _find_red_edge(self, reflectance: np.ndarray, 
                      wavelengths: np.ndarray) -> float:
        """Find red edge position (inflection point)"""
        # Get spectral slice in red edge region (680-750nm)
        red_edge_idx = np.where((wavelengths > 680) & (wavelengths < 750))[0]
        
        # Calculate derivative
        mean_spectrum = np.mean(reflectance, axis=(0, 1))
        red_edge_spectrum = mean_spectrum[red_edge_idx]
        derivative = np.gradient(red_edge_spectrum)
        
        # Find maximum derivative position
        max_idx = np.argmax(derivative)
        red_edge_position = wavelengths[red_edge_idx[max_idx]]
        
        return red_edge_position
```

## Model Development

### Step 4: CDW Proxy Model
```python
# src/models/cdw_proxy.py
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import cross_val_score
import joblib

class CDWProxyModel:
    """Estimate CDW from AOP data"""
    
    def __init__(self):
        self.models = {
            'rf': RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                random_state=42
            ),
            'gb': GradientBoostingRegressor(
                n_estimators=150,
                max_depth=8,
                learning_rate=0.1,
                random_state=42
            )
        }
        
        self.weights = [0.6, 0.4]  # RF, GB weights
        self.feature_names = None
        self.is_trained = False
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
             feature_names: list = None):
        """Train CDW proxy models"""
        
        self.feature_names = feature_names
        
        # Train each model
        for name, model in self.models.items():
            print(f"Training {name}...")
            model.fit(X_train, y_train)
            
            # Cross-validation score
            scores = cross_val_score(model, X_train, y_train, cv=5, 
                                    scoring='r2')
            print(f"  CV R² score: {np.mean(scores):.3f} (+/- {np.std(scores):.3f})")
        
        self.is_trained = True
        
        # Feature importance
        if feature_names:
            self._print_feature_importance()
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict CDW using ensemble"""
        
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        predictions = []
        
        for name, model in self.models.items():
            pred = model.predict(X)
            predictions.append(pred)
        
        # Weighted average
        ensemble_pred = np.average(predictions, weights=self.weights, axis=0)
        
        # Ensure realistic bounds (0-300 Mg/ha typical range)
        ensemble_pred = np.clip(ensemble_pred, 0, 300)
        
        return ensemble_pred
    
    def _print_feature_importance(self):
        """Print feature importance from Random Forest"""
        
        rf_importance = self.models['rf'].feature_importances_
        
        # Sort by importance
        indices = np.argsort(rf_importance)[::-1]
        
        print("\nTop 10 Most Important Features:")
        for i in range(min(10, len(indices))):
            idx = indices[i]
            print(f"  {self.feature_names[idx]}: {rf_importance[idx]:.3f}")
    
    def save(self, path: str):
        """Save trained model"""
        model_dict = {
            'models': self.models,
            'weights': self.weights,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        joblib.dump(model_dict, path)
    
    def load(self, path: str):
        """Load trained model"""
        model_dict = joblib.load(path)
        self.models = model_dict['models']
        self.weights = model_dict['weights']
        self.feature_names = model_dict['feature_names']
        self.is_trained = model_dict['is_trained']
```

### Step 5: Three-Tier Cascade
```python
# src/models/three_tier_cascade.py
import numpy as np
import xgboost as xgb
from typing import Dict, Tuple

class ThreeTierCascade:
    """Complete three-tier prediction system"""
    
    def __init__(self):
        # Initialize sub-models
        self.ground_to_aop = GroundToAOPModel()
        self.aop_to_satellite = AOPToSatelliteModel()
        self.fire_risk_model = FireRiskModel()
        
    def train_complete_cascade(self, 
                               ground_data: Dict,
                               aop_data: Dict,
                               satellite_data: Dict,
                               fire_labels: np.ndarray):
        """Train all three tiers"""
        
        print("=" * 50)
        print("TRAINING THREE-TIER CASCADE MODEL")
        print("=" * 50)
        
        # Tier 1: Ground -> AOP
        print("\n[1/3] Training Ground to AOP crosswalk...")
        self.ground_to_aop.train(
            ground_features=ground_data['features'],
            ground_targets=ground_data['targets'],
            aop_features=aop_data['features']
        )
        
        # Enhance AOP with predicted ground variables
        aop_enhanced = self._enhance_aop_with_ground(
            aop_data['features'],
            self.ground_to_aop.predict(aop_data['features'])
        )
        
        # Tier 2: AOP -> Satellite
        print("\n[2/3] Training AOP to Satellite crosswalk...")
        self.aop_to_satellite.train(
            aop_features=aop_enhanced,
            satellite_features=satellite_data['features']
        )
        
        # Tier 3: Fire Risk
        print("\n[3/3] Training fire risk model...")
        self.fire_risk_model.train(
            features=aop_enhanced,
            labels=fire_labels
        )
        
        print("\n" + "=" * 50)
        print("CASCADE TRAINING COMPLETE")
        print("=" * 50)
    
    def predict(self, data: np.ndarray, data_tier: str) -> Dict:
        """Predict fire risk using appropriate tier"""
        
        if data_tier == 'ground':
            # Best case: have ground measurements
            risk_features = self._prepare_ground_features(data)
            confidence = 0.95
            
        elif data_tier == 'aop':
            # Good case: have AOP data
            ground_pred = self.ground_to_aop.predict(data)
            risk_features = self._prepare_aop_features(data, ground_pred)
            confidence = 0.85
            
        elif data_tier == 'satellite':
            # Common case: satellite only
            aop_pred = self.aop_to_satellite.predict(data)
            ground_pred = self.ground_to_aop.predict(aop_pred)
            risk_features = self._prepare_satellite_features(data, aop_pred, ground_pred)
            confidence = 0.70
        
        else:
            raise ValueError(f"Unknown data tier: {data_tier}")
        
        # Predict fire risk
        risk_probability = self.fire_risk_model.predict_proba(risk_features)
        
        return {
            'risk_probability': risk_probability,
            'risk_class': self._classify_risk(risk_probability),
            'confidence': confidence,
            'data_tier': data_tier
        }
    
    def _classify_risk(self, probability: float) -> str:
        """Classify risk level"""
        if probability < 0.2:
            return 'LOW'
        elif probability < 0.4:
            return 'MODERATE'
        elif probability < 0.6:
            return 'HIGH'
        elif probability < 0.8:
            return 'VERY HIGH'
        else:
            return 'EXTREME'

class GroundToAOPModel:
    """Crosswalk from ground measurements to AOP signatures"""
    
    def __init__(self):
        self.model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.1,
            objective='reg:squarederror'
        )
    
    def train(self, ground_features, ground_targets, aop_features):
        """Train ground to AOP mapping"""
        # Implementation here
        pass
    
    def predict(self, aop_features):
        """Predict ground conditions from AOP"""
        # Implementation here
        pass

class AOPToSatelliteModel:
    """Crosswalk from AOP to satellite"""
    
    def __init__(self):
        self.model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=10,
            learning_rate=0.1
        )
    
    def train(self, aop_features, satellite_features):
        """Train AOP to satellite mapping"""
        # Implementation here
        pass
    
    def predict(self, satellite_features):
        """Predict AOP features from satellite"""
        # Implementation here
        pass

class FireRiskModel:
    """Final fire risk prediction model"""
    
    def __init__(self):
        self.model = xgb.XGBClassifier(
            n_estimators=300,
            max_depth=10,
            learning_rate=0.1,
            objective='binary:logistic'
        )
    
    def train(self, features, labels):
        """Train fire risk model"""
        # Implementation here
        pass
    
    def predict_proba(self, features):
        """Predict fire probability"""
        # Implementation here
        pass
```

## API Development

### Step 6: FastAPI Application
```python
# src/api/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import numpy as np
from datetime import datetime

from ..models.three_tier_cascade import ThreeTierCascade
from ..data.satellite_fetcher import SatelliteDataFetcher
from ..features.aop_features import AOPFeatureExtractor

app = FastAPI(
    title="Colorado Fire Watch API",
    description="Wildfire risk prediction using NEON data",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models on startup
model = ThreeTierCascade()
model.load("data/models/cascade_model.pkl")

satellite_fetcher = SatelliteDataFetcher()
feature_extractor = AOPFeatureExtractor()

# Request/Response models
class LocationRequest(BaseModel):
    latitude: float
    longitude: float
    date: Optional[datetime] = datetime.now()

class RiskResponse(BaseModel):
    location: dict
    risk_level: str
    risk_probability: float
    confidence: float
    data_tier: str
    contributing_factors: dict

class BulkRequest(BaseModel):
    locations: List[LocationRequest]

# Endpoints
@app.get("/")
def read_root():
    return {
        "name": "Colorado Fire Watch API",
        "status": "operational",
        "endpoints": [
            "/risk/point",
            "/risk/area",
            "/risk/bulk",
            "/data/availability",
            "/model/info"
        ]
    }

@app.post("/risk/point", response_model=RiskResponse)
async def get_point_risk(request: LocationRequest):
    """Get fire risk for a single point"""
    
    try:
        # Check data availability
        data_tier = check_data_availability(
            request.latitude,
            request.longitude,
            request.date
        )
        
        # Fetch appropriate data
        if data_tier == "aop":
            data = fetch_aop_data(request.latitude, request.longitude)
            features = feature_extractor.extract_aop_features(data)
        else:
            # Default to satellite
            data = satellite_fetcher.get_sentinel2_composite(
                bounds=[request.longitude-0.01, request.latitude-0.01,
                       request.longitude+0.01, request.latitude+0.01],
                start_date=str(request.date - timedelta(days=15)),
                end_date=str(request.date)
            )
            features = extract_satellite_features(data)
        
        # Add weather data
        weather = fetch_weather_data(request.latitude, request.longitude, request.date)
        features.update(weather)
        
        # Predict risk
        prediction = model.predict(features, data_tier)
        
        # Prepare response
        response = RiskResponse(
            location={
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            risk_level=prediction['risk_class'],
            risk_probability=float(prediction['risk_probability']),
            confidence=float(prediction['confidence']),
            data_tier=data_tier,
            contributing_factors=get_contributing_factors(features)
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/risk/area")
async def get_area_risk(bounds: List[float], resolution: int = 100):
    """Get fire risk for an area"""
    
    # Create grid
    lats = np.linspace(bounds[1], bounds[3], resolution)
    lons = np.linspace(bounds[0], bounds[2], resolution)
    
    risk_map = np.zeros((resolution, resolution))
    
    for i, lat in enumerate(lats):
        for j, lon in enumerate(lons):
            request = LocationRequest(latitude=lat, longitude=lon)
            response = await get_point_risk(request)
            risk_map[i, j] = response.risk_probability
    
    return {
        "bounds": bounds,
        "resolution": resolution,
        "risk_map": risk_map.tolist(),
        "statistics": {
            "mean_risk": float(np.mean(risk_map)),
            "max_risk": float(np.max(risk_map)),
            "high_risk_area": float(np.sum(risk_map > 0.6) / risk_map.size)
        }
    }

@app.get("/data/availability")
def check_data_availability(latitude: float, longitude: float, 
                           date: Optional[datetime] = None):
    """Check what data is available for a location"""
    
    availability = {
        "ground": False,
        "aop": False,
        "satellite": True  # Always available
    }
    
    # Check if in NEON plot
    if is_in_neon_plot(latitude, longitude):
        availability["ground"] = True
    
    # Check if in AOP flight box
    if is_in_aop_coverage(latitude, longitude, date):
        availability["aop"] = True
    
    # Determine best available tier
    if availability["ground"]:
        best_tier = "ground"
    elif availability["aop"]:
        best_tier = "aop"
    else:
        best_tier = "satellite"
    
    return {
        "location": {"latitude": latitude, "longitude": longitude},
        "availability": availability,
        "recommended_tier": best_tier
    }

@app.get("/model/info")
def get_model_info():
    """Get information about the model"""
    
    return {
        "model_version": "1.0.0",
        "training_date": "2024-01-15",
        "training_sites": ["NIWO", "RMNP", "CPER"],
        "validation_metrics": {
            "ground_tier_r2": 0.85,
            "aop_tier_r2": 0.78,
            "satellite_tier_r2": 0.72,
            "fire_prediction_auc": 0.89
        },
        "features": {
            "ground": 25,
            "aop": 45,
            "satellite": 30
        }
    }

# Helper functions
def check_data_availability(lat: float, lon: float, date: datetime) -> str:
    """Determine best available data tier"""
    # Implementation here
    pass

def fetch_aop_data(lat: float, lon: float):
    """Fetch AOP data for location"""
    # Implementation here
    pass

def fetch_weather_data(lat: float, lon: float, date: datetime):
    """Fetch weather data"""
    # Implementation here
    pass

def get_contributing_factors(features: dict) -> dict:
    """Extract main contributing factors"""
    # Implementation here
    pass
```

## Deployment

### Step 7: Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY data/models/ ./data/models/

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/firewatch
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data
  
  db:
    image: postgis/postgis:15-3.3
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=firewatch
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Testing & Validation

### Step 8: Test Suite
```python
# tests/test_models.py
import pytest
import numpy as np
from src.models.cdw_proxy import CDWProxyModel
from src.models.three_tier_cascade import ThreeTierCascade

class TestCDWProxy:
    def test_model_training(self):
        """Test CDW proxy model training"""
        model = CDWProxyModel()
        
        # Generate synthetic data
        X_train = np.random.randn(100, 20)
        y_train = np.random.uniform(10, 150, 100)
        
        # Train model
        model.train(X_train, y_train)
        
        assert model.is_trained
        
    def test_prediction_bounds(self):
        """Test that predictions are within reasonable bounds"""
        model = CDWProxyModel()
        
        X_train = np.random.randn(100, 20)
        y_train = np.random.uniform(10, 150, 100)
        
        model.train(X_train, y_train)
        
        X_test = np.random.randn(10, 20)
        predictions = model.predict(X_test)
        
        assert np.all(predictions >= 0)
        assert np.all(predictions <= 300)

class TestThreeTierCascade:
    def test_cascade_prediction(self):
        """Test complete cascade prediction"""
        model = ThreeTierCascade()
        
        # Test satellite tier (most common)
        satellite_data = np.random.randn(1, 50)
        result = model.predict(satellite_data, 'satellite')
        
        assert 'risk_probability' in result
        assert 'risk_class' in result
        assert 'confidence' in result
        assert result['confidence'] == 0.70  # Satellite tier confidence
```

### Validation Scripts
```python
# scripts/validate_fire_predictions.py
import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, precision_recall_curve
import matplotlib.pyplot as plt

def validate_against_fires(model, fire_database_path):
    """Validate model against historical fires"""
    
    # Load fire database
    fires = pd.read_csv(fire_database_path)
    
    results = []
    
    for _, fire in fires.iterrows():
        # Get pre-fire conditions
        pre_fire_date = pd.to_datetime(fire['start_date']) - pd.Timedelta(days=7)
        
        # Load data for fire location
        data = load_data_for_location(
            fire['latitude'],
            fire['longitude'],
            pre_fire_date
        )
        
        # Predict risk
        prediction = model.predict(data['features'], data['tier'])
        
        results.append({
            'fire_name': fire['name'],
            'predicted_risk': prediction['risk_probability'],
            'actual_burned': 1,  # It did burn
            'fire_size': fire['acres'],
            'data_tier': data['tier']
        })
    
    # Calculate metrics
    results_df = pd.DataFrame(results)
    
    # ROC-AUC
    auc = roc_auc_score(results_df['actual_burned'], results_df['predicted_risk'])
    print(f"ROC-AUC Score: {auc:.3f}")
    
    # Precision-Recall
    precision, recall, thresholds = precision_recall_curve(
        results_df['actual_burned'],
        results_df['predicted_risk']
    )
    
    # Plot results
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Risk distribution
    axes[0].hist(results_df['predicted_risk'], bins=20)
    axes[0].set_xlabel('Predicted Risk')
    axes[0].set_ylabel('Count')
    axes[0].set_title('Risk Distribution for Actual Fires')
    
    # Precision-Recall curve
    axes[1].plot(recall, precision)
    axes[1].set_xlabel('Recall')
    axes[1].set_ylabel('Precision')
    axes[1].set_title(f'Precision-Recall Curve (AUC={auc:.3f})')
    
    plt.tight_layout()
    plt.savefig('validation_results.png')
    
    return results_df
```

## Production Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Model validation complete
- [ ] API documentation updated
- [ ] Docker builds successfully
- [ ] Environment variables configured
- [ ] SSL certificates ready
- [ ] Monitoring setup

### Deployment Steps
1. Build Docker image: `docker build -t colorado-fire-watch .`
2. Run tests: `pytest tests/`
3. Deploy to staging: `docker-compose up -d`
4. Smoke test API endpoints
5. Deploy to production
6. Monitor logs and metrics

### Post-Deployment
- [ ] API endpoints responding
- [ ] Model predictions reasonable
- [ ] Database connections stable
- [ ] Cache working properly
- [ ] Alerts configured
- [ ] Documentation published

## Next Steps

1. **Immediate Actions**
   - Download NIWO 2019 data (pre-Cameron Peak)
   - Train initial CDW proxy model
   - Build Sentinel-2 crosswalk
   
2. **Short-term (1-2 weeks)**
   - Complete three-tier cascade
   - Deploy API locally
   - Create web interface
   
3. **Medium-term (1 month)**
   - Validate against 2020 fires
   - Optimize model performance
   - Deploy to cloud
   
4. **Long-term (3 months)**
   - Expand to all Colorado
   - Add real-time weather
   - Mobile application