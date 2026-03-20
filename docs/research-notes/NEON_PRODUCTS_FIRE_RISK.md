# NEON Products for Wildfire Risk Assessment

## Overview
This document outlines all NEON (National Ecological Observatory Network) data products relevant to wildfire risk prediction, organized by data type and fire risk component.

## Table of Contents
1. [Core AOP Products](#core-aop-products)
2. [Ground-Based Products](#ground-based-products)
3. [Tower Atmospheric Products](#tower-atmospheric-products)
4. [Soil Products](#soil-products)
5. [Phenology Products](#phenology-products)
6. [Biogeochemistry Products](#biogeochemistry-products)
7. [Organism Products](#organism-products)
8. [Eddy Covariance Products](#eddy-covariance-products)
9. [Aquatic Products](#aquatic-products)

## Core AOP Products

### Discrete LiDAR Products (Manageable File Sizes)
- **DP3.30015.001**: Ecosystem structure (CHM) - 1m raster, ~100MB per tile
- **DP3.30025.001**: Slope and aspect - 1m raster, small files
- **DP3.30024.001**: Discrete return LiDAR (avoid point clouds)

### Hyperspectral Products
- **DP3.30014.001**: Apparent reflectance - 426 bands, ~1GB per tile
- **DP3.30026.001**: Vegetation indices suite
- **DP3.30010.001**: High-resolution orthorectified camera imagery

### Fire Risk Applications
```python
# Key features extractable from AOP
aop_fire_features = {
    'canopy_height': 'Crown fire potential',
    'canopy_gaps': 'Fuel discontinuity',
    'surface_roughness': 'Surface fuel complexity',
    'ndvi_variants': 'Vegetation health/stress',
    'moisture_indices': 'Live fuel moisture',
    'species_classification': 'Fuel type mapping'
}
```

## Ground-Based Products

### Vegetation Structure (VST)
- **DP1.10098.001**: Woody vegetation structure
  - Tree heights, DBH, crown dimensions
  - Health status assessments
  - Species identification

### Coarse Downed Wood (CDW)
- **DP1.10058.001**: Coarse downed wood survey
  - Volume per hectare
  - Decay class distribution
  - Diameter distributions

### Litter and Fine Woody Debris
- **DP1.10033.001**: Litterfall and fine woody debris
  - Fuel accumulation rates
  - Seasonal patterns
  - Chemical composition

## Tower Atmospheric Products

### Temperature and Humidity
- **DP1.00002.001**: Single aspirated air temperature
- **DP1.00003.001**: Triple aspirated air temperature (more accurate)
- **DP1.00098.001**: Relative humidity

### Wind
- **DP1.00001.001**: 2D wind speed and direction
- **DP1.00007.001**: 3D wind speed and direction

### Precipitation
- **DP1.00004.001**: Precipitation (tipping bucket)
- **DP1.00006.001**: Precipitation (weighing gauge)

### Radiation
- **DP1.00023.001**: Shortwave and longwave radiation
- **DP1.00024.001**: Photosynthetically active radiation

### Fire Weather Index Calculation
```python
def calculate_fwi_components(tower_data):
    """Calculate Canadian FWI from tower data"""
    return {
        'ffmc': fine_fuel_moisture_code(tower_data),
        'dmc': duff_moisture_code(tower_data),
        'dc': drought_code(tower_data),
        'isi': initial_spread_index(tower_data),
        'bui': buildup_index(tower_data),
        'fwi': fire_weather_index(tower_data)
    }
```

## Soil Products

### Physical Properties
- **DP1.10086.001**: Soil physical properties
  - Texture (sand, silt, clay percentages)
  - Bulk density
  - Water holding capacity

### Moisture Monitoring
- **DP1.00094.001**: Soil water content (continuous)
- **DP1.00095.001**: Soil CO2 concentration
- **DP1.10047.001**: Soil temperature

### Chemical Properties
- **DP1.10100.001**: Soil chemical properties
  - Organic carbon content
  - Nitrogen content
  - pH

### Fire Applications
```python
def fuel_moisture_from_soil(soil_data):
    """Estimate fine fuel moisture from soil conditions"""
    # Clay retains moisture longer
    clay_effect = soil_data['clay_percent'] * 0.01
    
    # Current deficit
    deficit = (soil_data['field_capacity'] - soil_data['current_moisture'])
    
    # Time since rain effect
    days_dry = soil_data['days_since_rain']
    
    return estimate_1hr_10hr_fuel_moisture(clay_effect, deficit, days_dry)
```

## Phenology Products

### Observational Data
- **DP1.10055.001**: Plant phenology observations
  - Green-up dates
  - Peak greenness
  - Senescence timing

### Phenocam Imagery
- **DP1.00033.001**: Phenocam imagery
  - Daily vegetation photos
  - GCC (Green Chromatic Coordinate) time series
  - Early stress detection

### Summary Products
- **DP4.00001.001**: Summary phenometrics
  - Annual phenophase transitions
  - Growing season length

### Phenological Fire Risk
```python
def phenological_fire_risk(pheno_data, current_date):
    """Assess fire risk based on phenological stage"""
    if current_date > pheno_data['senescence_start']:
        return 2.0  # Curing vegetation, highest risk
    elif current_date < pheno_data['greenup_start'] + 14:
        return 1.5  # Early growth, flashy fuels
    elif near_peak_greenness(current_date, pheno_data):
        return 0.5  # Maximum moisture, lowest risk
    return 1.0  # Normal risk
```

## Biogeochemistry Products

### Litter Chemistry
- **DP1.10026.001**: Litter chemical properties
  - Carbon:Nitrogen ratio
  - Lignin content
  - Decomposition rates

### Foliar Chemistry
- **DP1.10058.001**: Plant foliar chemistry
  - Nitrogen content (stress indicator)
  - Water content
  - Secondary compounds

### Decomposition
- **DP1.20097.001**: Soil microbe biomass
  - Decomposition potential
  - Fuel accumulation rates

### Flammability Assessment
```python
def assess_fuel_flammability(litter_chem):
    """Chemical composition affects burning characteristics"""
    # High C:N = slower decomposition, more accumulation
    accumulation = min(litter_chem['c_n_ratio'] / 25, 2.0)
    
    # Lignin resists burning
    lignin_effect = 1 - (litter_chem['lignin_percent'] / 100)
    
    # Volatiles increase flammability
    volatile_content = estimate_volatiles(litter_chem['species'])
    
    return accumulation * lignin_effect * volatile_content
```

## Organism Products

### Beetle Monitoring
- **DP1.10072.001**: Ground beetles
- **DP1.10020.001**: Bark beetle impacts (when available)
  - Outbreak detection
  - Tree mortality predictions

### Birds as Indicators
- **DP1.10022.001**: Breeding bird point counts
  - Woodpecker abundance (snag indicator)
  - Cavity nester populations

### Mammal Grazing
- **DP1.10003.001**: Small mammal abundance
  - Grazing pressure on fine fuels
  - Seed predation effects

### Biological Risk Indicators
```python
def biological_fire_indicators(organism_data):
    """Use organisms to assess forest health"""
    indicators = {}
    
    # Bark beetles = future dead fuel
    if organism_data['beetle_density'] > threshold:
        indicators['beetle_kill_risk'] = 3.0
    
    # Woodpeckers indicate snags
    indicators['snag_index'] = (
        organism_data['woodpecker_count'] / 
        organism_data['total_birds']
    )
    
    return indicators
```

## Eddy Covariance Products

### Bundled Flux Data
- **DP4.00200.001**: Bundled eddy covariance
  - CO2 flux (GPP, Reco, NEE)
  - Water vapor flux (ET)
  - Energy balance components

### Isotope Measurements
- **DP1.00034.001**: CO2 isotopes
- **DP1.00035.001**: H2O isotopes
  - Water use efficiency
  - Evaporation vs transpiration partitioning

### Early Stress Detection
```python
def detect_ecosystem_stress(flux_data):
    """Flux towers detect stress before visible symptoms"""
    # Reduced carbon uptake
    gpp_anomaly = (flux_data['gpp'] - flux_data['gpp_baseline']) / flux_data['gpp_baseline']
    
    # Reduced evapotranspiration (stomatal closure)
    et_reduction = 1 - (flux_data['et'] / flux_data['et_normal'])
    
    # Bowen ratio increases with stress
    bowen = flux_data['sensible_heat'] / flux_data['latent_heat']
    
    stress_index = combine_stress_indicators(gpp_anomaly, et_reduction, bowen)
    return stress_index
```

## Aquatic Products

### Stream Monitoring
- **DP1.20288.001**: Water quality
- **DP1.20016.001**: Stream discharge
- **DP4.00130.001**: Stream temperature model

### Riparian Assessment
- **DP1.20190.001**: Riparian vegetation composition
  - Buffer effectiveness
  - Fuel moisture gradient

### Post-Fire Risk
```python
def assess_watershed_vulnerability(aquatic_data, fire_risk):
    """Predict post-fire debris flows and water impacts"""
    # Flashy streams = steep watersheds
    flow_variability = np.std(aquatic_data['discharge']) / np.mean(aquatic_data['discharge'])
    
    # Riparian buffer protection
    buffer_width = aquatic_data['riparian_cover']
    
    debris_flow_risk = fire_risk * flow_variability * (1 / buffer_width)
    return debris_flow_risk
```

## Data Access Examples

### Using neonUtilities (R)
```r
library(neonUtilities)

# Download CDW data
cdw_data <- loadByProduct(
  dpID = "DP1.10058.001",
  site = c("NIWO", "RMNP"),
  startdate = "2019-01",
  enddate = "2023-12"
)

# Download AOP data
aop_data <- byFileAOP(
  dpID = "DP3.30015.001",  # CHM
  site = "NIWO",
  year = 2019
)
```

### Using Python
```python
import requests

def download_neon_data(product_id, site, start_date, end_date):
    """Download NEON data via API"""
    base_url = "https://data.neonscience.org/api/v0"
    
    # Get available files
    url = f"{base_url}/data/{product_id}/{site}"
    params = {
        'startdate': start_date,
        'enddate': end_date
    }
    
    response = requests.get(url, params=params)
    data_urls = response.json()['data']['files']
    
    # Download files
    for file_url in data_urls:
        download_file(file_url)
```

## Integration Priority

### Tier 1 - Essential Products
1. AOP hyperspectral and CHM
2. Tower weather data
3. Soil moisture
4. CDW/VST where available

### Tier 2 - Enhanced Accuracy
1. Phenology products
2. Eddy flux data
3. Litter chemistry
4. Beetle monitoring

### Tier 3 - Comprehensive System
1. All organism data
2. Aquatic products
3. Isotope measurements
4. Full biogeochemistry suite

## Colorado NEON Sites

### NIWO - Niwot Ridge
- Subalpine forest
- Cameron Peak Fire proximity
- Excellent long-term data

### RMNP - Rocky Mountain National Park
- Multiple vegetation zones
- East Troublesome Fire area
- High visitor impact considerations

### CPER - Central Plains Experimental Range
- Grassland/shrubland
- Different fire regime
- Lower elevation dynamics

## Next Steps

1. Start with NIWO site (best fire validation data)
2. Focus on AOP + tower weather initially
3. Add soil moisture and phenology
4. Expand to other products based on performance gains
5. Validate against Cameron Peak and East Troublesome fires