# Three-Tier Data Integration Strategy

## Overview
This document describes the three-tier cascade approach for wildfire risk prediction: **Ground Data → AOP → Satellite**. Each tier provides different spatial and temporal coverage, with models trained to transfer information from high-detail to broad-scale observations.

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Tier 1: Ground Data](#tier-1-ground-data)
3. [Tier 2: AOP Data](#tier-2-aop-data)
4. [Tier 3: Satellite Data](#tier-3-satellite-data)
5. [Crosswalk Models](#crosswalk-models)
6. [Integration Pipeline](#integration-pipeline)
7. [Validation Strategy](#validation-strategy)
8. [Implementation Examples](#implementation-examples)

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TIER 1: GROUND DATA                       │
│  Spatial: Plot-level (20m plots)                            │
│  Temporal: Annual to multi-year                             │
│  Products: CDW, VST, Soil, Litter, Phenology               │
│  Coverage: ~100 plots per NEON site                         │
└────────────────────────┬────────────────────────────────────┘
                         │ Train Model A
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                     TIER 2: AOP DATA                         │
│  Spatial: 1m resolution, 10×10km boxes                      │
│  Temporal: Annual flights                                    │
│  Products: Hyperspectral (426 bands), LiDAR, Camera        │
│  Coverage: NEON sites + campaign areas                      │
└────────────────────────┬────────────────────────────────────┘
                         │ Train Model B
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   TIER 3: SATELLITE DATA                     │
│  Spatial: 10-30m (Sentinel), 250-1000m (MODIS)             │
│  Temporal: 5-day (Sentinel), Daily (MODIS)                 │
│  Products: Multispectral, Thermal, Active Fire             │
│  Coverage: Global                                           │
└─────────────────────────────────────────────────────────────┘
                         │
                         ↓
              🔥 FIRE RISK PREDICTION 🔥
```

## Tier 1: Ground Data

### Available Products
```python
ground_products = {
    # Vegetation Structure
    'DP1.10098.001': 'Woody plant vegetation structure',
    'DP1.10058.001': 'Coarse downed wood',
    'DP1.10033.001': 'Litter and fine woody debris',
    
    # Soil Properties
    'DP1.10086.001': 'Soil physical properties',
    'DP1.10100.001': 'Soil chemical properties',
    'DP1.00094.001': 'Soil water content',
    
    # Plant Chemistry
    'DP1.10026.001': 'Litter chemical properties',
    'DP1.10058.001': 'Plant foliar chemistry',
    
    # Phenology
    'DP1.10055.001': 'Plant phenology observations',
    
    # Organisms
    'DP1.10072.001': 'Ground beetles',
    'DP1.10022.001': 'Breeding landbird point counts'
}
```

### Feature Extraction
```python
def extract_ground_features(plot_data):
    """Extract fire-relevant features from ground measurements"""
    
    features = {}
    
    # Fuel loads
    features['cdw_mg_ha'] = plot_data['cdw']['volume_m3'] * 0.45 * 1000
    features['litter_kg_m2'] = plot_data['litter']['dry_mass']
    features['fwd_1hr'] = plot_data['fwd']['diameter_0_0.6cm']
    features['fwd_10hr'] = plot_data['fwd']['diameter_0.6_2.5cm']
    features['fwd_100hr'] = plot_data['fwd']['diameter_2.5_7.6cm']
    
    # Vegetation structure
    features['canopy_cover'] = plot_data['vst']['canopy_cover_percent']
    features['tree_height_mean'] = np.mean(plot_data['vst']['tree_heights'])
    features['tree_height_max'] = np.max(plot_data['vst']['tree_heights'])
    features['basal_area'] = plot_data['vst']['basal_area_m2_ha']
    features['stem_density'] = plot_data['vst']['stems_per_ha']
    
    # Health indicators
    features['mortality_rate'] = plot_data['vst']['dead_trees'] / plot_data['vst']['total_trees']
    features['beetle_damage'] = plot_data['organisms']['beetle_affected_trees']
    
    # Soil moisture potential
    features['soil_clay'] = plot_data['soil']['clay_percent']
    features['soil_organic'] = plot_data['soil']['organic_carbon_percent']
    features['soil_moisture'] = plot_data['soil']['volumetric_water_content']
    
    # Chemical properties (flammability)
    features['litter_cn_ratio'] = plot_data['litter']['carbon'] / plot_data['litter']['nitrogen']
    features['foliar_moisture'] = plot_data['foliar']['water_content_percent']
    
    return features
```

## Tier 2: AOP Data

### Available Products
```python
aop_products = {
    # LiDAR Products (Discrete, manageable sizes)
    'DP3.30015.001': 'Ecosystem structure (CHM)',
    'DP3.30025.001': 'Slope and aspect',
    
    # Hyperspectral Products
    'DP3.30014.001': 'Apparent reflectance (426 bands)',
    'DP3.30026.001': 'Vegetation indices',
    
    # Camera Products
    'DP3.30010.001': 'High-resolution orthorectified camera'
}
```

### Feature Extraction
```python
def extract_aop_features(aop_data):
    """Extract features from AOP products"""
    
    features = {}
    
    # Structure from LiDAR
    chm = aop_data['chm']
    features['canopy_height_mean'] = np.mean(chm[chm > 2])
    features['canopy_height_std'] = np.std(chm[chm > 2])
    features['canopy_height_max'] = np.max(chm)
    features['gap_fraction'] = np.sum(chm < 2) / chm.size
    features['canopy_roughness'] = calculate_roughness(chm)
    
    # Slope and aspect effects
    features['slope_mean'] = np.mean(aop_data['slope'])
    features['slope_max'] = np.max(aop_data['slope'])
    features['aspect_majority'] = mode(aop_data['aspect'])
    
    # Hyperspectral indices
    hs = aop_data['hyperspectral']
    
    # Multiple NDVI formulations
    features['ndvi_broadband'] = calculate_ndvi(hs, 860, 650)
    features['ndvi_red_edge'] = calculate_ndvi(hs, 750, 705)
    features['ndvi_narrow'] = calculate_ndvi(hs, 850, 680)
    
    # Water indices
    features['ndwi'] = (hs[:,:,860] - hs[:,:,1240]) / (hs[:,:,860] + hs[:,:,1240])
    features['msi'] = hs[:,:,1600] / hs[:,:,820]  # Moisture Stress Index
    
    # Stress indicators
    features['pri'] = (hs[:,:,531] - hs[:,:,570]) / (hs[:,:,531] + hs[:,:,570])
    features['red_edge_position'] = calculate_red_edge_position(hs)
    
    # Dead vegetation
    features['cellulose_absorption'] = hs[:,:,2100] / hs[:,:,2200]
    features['lignin_absorption'] = hs[:,:,2300] / hs[:,:,2200]
    
    # Species classification
    features['species_composition'] = classify_species(hs)
    
    return features
```

## Tier 3: Satellite Data

### Available Sources
```python
satellite_sources = {
    'sentinel2': {
        'bands': 13,
        'resolution': '10-60m',
        'revisit': '5 days',
        'key_products': ['surface_reflectance', 'scene_classification']
    },
    'landsat8': {
        'bands': 11,
        'resolution': '30m',
        'revisit': '16 days',
        'key_products': ['surface_reflectance', 'surface_temperature']
    },
    'modis': {
        'bands': 36,
        'resolution': '250-1000m',
        'revisit': 'daily',
        'key_products': ['vegetation_indices', 'land_surface_temp', 'active_fire']
    },
    'viirs': {
        'resolution': '375-750m',
        'revisit': 'daily',
        'key_products': ['active_fire', 'surface_reflectance']
    }
}
```

### Feature Extraction
```python
def extract_satellite_features(sat_data):
    """Extract features from satellite imagery"""
    
    features = {}
    
    # Sentinel-2 bands
    if 'sentinel2' in sat_data:
        s2 = sat_data['sentinel2']
        
        # Basic indices
        features['s2_ndvi'] = (s2['B8'] - s2['B4']) / (s2['B8'] + s2['B4'])
        features['s2_ndwi'] = (s2['B8'] - s2['B11']) / (s2['B8'] + s2['B11'])
        features['s2_nbr'] = (s2['B8'] - s2['B12']) / (s2['B8'] + s2['B12'])
        
        # Red edge indices
        features['s2_re_ndvi'] = (s2['B8'] - s2['B5']) / (s2['B8'] + s2['B5'])
        features['s2_re_position'] = (s2['B5'] + s2['B7']) / 2
        
        # All band ratios (rich feature set)
        for b1 in ['B2','B3','B4','B5','B6','B7','B8','B8A','B11','B12']:
            for b2 in ['B2','B3','B4','B5','B6','B7','B8','B8A','B11','B12']:
                if b1 != b2:
                    features[f's2_ratio_{b1}_{b2}'] = s2[b1] / s2[b2]
    
    # MODIS products
    if 'modis' in sat_data:
        mod = sat_data['modis']
        features['mod_lst_day'] = mod['LST_Day']
        features['mod_lst_night'] = mod['LST_Night']
        features['mod_lst_diff'] = mod['LST_Day'] - mod['LST_Night']
        features['mod_ndvi'] = mod['NDVI']
        features['mod_evi'] = mod['EVI']
        
    # Landsat thermal
    if 'landsat' in sat_data:
        ls = sat_data['landsat']
        features['ls_surface_temp'] = ls['ST_B10']
        features['ls_ndvi'] = (ls['B5'] - ls['B4']) / (ls['B5'] + ls['B4'])
        
    return features
```

## Crosswalk Models

### Model A: Ground to AOP
```python
class GroundToAOPModel:
    """Learn relationships between ground measurements and AOP signatures"""
    
    def __init__(self):
        self.models = {}
        self.feature_importance = {}
        
    def train(self, ground_features, aop_features):
        """Train models to predict ground conditions from AOP"""
        
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
        from sklearn.neural_network import MLPRegressor
        
        # CDW prediction model
        self.models['cdw'] = {
            'rf': RandomForestRegressor(n_estimators=200, max_depth=10),
            'gb': GradientBoostingRegressor(n_estimators=150),
            'nn': MLPRegressor(hidden_layer_sizes=(100, 50)),
            'weights': [0.5, 0.3, 0.2]
        }
        
        # Train each model
        for model in ['rf', 'gb', 'nn']:
            self.models['cdw'][model].fit(
                aop_features,
                ground_features['cdw_mg_ha']
            )
        
        # Feature importance from RF
        self.feature_importance['cdw'] = self.models['cdw']['rf'].feature_importances_
        
        # Similarly train for other ground variables
        ground_targets = ['litter_kg_m2', 'soil_moisture', 'foliar_moisture']
        for target in ground_targets:
            self.train_target_model(target, aop_features, ground_features[target])
    
    def predict(self, aop_features):
        """Predict ground conditions from AOP"""
        
        predictions = {}
        
        for target, model_dict in self.models.items():
            preds = []
            for model_name in ['rf', 'gb', 'nn']:
                pred = model_dict[model_name].predict(aop_features)
                preds.append(pred)
            
            # Weighted ensemble
            weights = model_dict['weights']
            predictions[target] = np.average(preds, weights=weights, axis=0)
        
        return predictions
```

### Model B: AOP to Satellite
```python
class AOPToSatelliteModel:
    """Learn to predict AOP-derived features from satellite"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        
    def train(self, aop_features, satellite_features):
        """Train crosswalk from satellite to AOP"""
        
        from sklearn.preprocessing import StandardScaler
        from sklearn.ensemble import RandomForestRegressor
        import xgboost as xgb
        
        # Scale features
        self.scalers['satellite'] = StandardScaler()
        sat_scaled = self.scalers['satellite'].fit_transform(satellite_features)
        
        # Key AOP features to predict
        aop_targets = [
            'canopy_height_mean',
            'gap_fraction', 
            'ndvi_red_edge',
            'moisture_stress_index',
            'species_lodgepole_fraction',
            'dead_vegetation_fraction'
        ]
        
        for target in aop_targets:
            # Use XGBoost for complex relationships
            self.models[target] = xgb.XGBRegressor(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8
            )
            
            self.models[target].fit(sat_scaled, aop_features[target])
    
    def predict(self, satellite_features):
        """Predict AOP features from satellite"""
        
        # Scale inputs
        sat_scaled = self.scalers['satellite'].transform(satellite_features)
        
        predictions = {}
        for target, model in self.models.items():
            predictions[target] = model.predict(sat_scaled)
        
        return predictions
```

### Combined Three-Tier Model
```python
class ThreeTierCascadeModel:
    """Complete three-tier prediction system"""
    
    def __init__(self):
        self.ground_to_aop = GroundToAOPModel()
        self.aop_to_satellite = AOPToSatelliteModel()
        self.fire_risk_model = None
        
    def train_cascade(self, ground_data, aop_data, satellite_data, fire_labels):
        """Train the complete cascade"""
        
        # Step 1: Train Ground → AOP
        print("Training Tier 1: Ground to AOP...")
        self.ground_to_aop.train(
            ground_features=ground_data,
            aop_features=aop_data
        )
        
        # Step 2: Enhance AOP with predicted ground variables
        aop_enhanced = aop_data.copy()
        ground_predictions = self.ground_to_aop.predict(aop_data)
        for key, values in ground_predictions.items():
            aop_enhanced[f'predicted_{key}'] = values
        
        # Step 3: Train AOP → Satellite
        print("Training Tier 2: AOP to Satellite...")
        self.aop_to_satellite.train(
            aop_features=aop_enhanced,
            satellite_features=satellite_data
        )
        
        # Step 4: Train fire risk model using all tiers
        print("Training fire risk model...")
        self.train_fire_risk_model(aop_enhanced, fire_labels)
    
    def predict_fire_risk(self, data, data_tier):
        """Predict fire risk using best available data"""
        
        if data_tier == 'ground':
            # Best case: have ground truth
            risk_features = self.prepare_risk_features_from_ground(data)
            
        elif data_tier == 'aop':
            # Good case: have AOP data
            # First predict ground variables
            ground_pred = self.ground_to_aop.predict(data)
            risk_features = self.prepare_risk_features_from_aop(data, ground_pred)
            
        elif data_tier == 'satellite':
            # Common case: only satellite
            # First predict AOP features
            aop_pred = self.aop_to_satellite.predict(data)
            # Then predict ground variables
            ground_pred = self.ground_to_aop.predict(aop_pred)
            risk_features = self.prepare_risk_features_from_satellite(data, aop_pred, ground_pred)
        
        # Calculate fire risk
        risk = self.fire_risk_model.predict_proba(risk_features)[:, 1]
        
        return risk
```

## Integration Pipeline

### Data Flow Architecture
```python
class FireRiskPipeline:
    """Complete pipeline for operational fire risk prediction"""
    
    def __init__(self):
        self.cascade_model = ThreeTierCascadeModel()
        self.weather_model = WeatherIntegration()
        self.validation_system = ValidationSystem()
        
    def process_location(self, lat, lon, date):
        """Process a location through the cascade"""
        
        # Check data availability
        data_tier = self.check_data_availability(lat, lon, date)
        
        if data_tier == 'ground':
            # NEON plot location
            data = self.load_ground_data(lat, lon, date)
            features = self.extract_ground_features(data)
            
        elif data_tier == 'aop':
            # Within AOP flight box
            data = self.load_aop_data(lat, lon, date)
            features = self.extract_aop_features(data)
            
        else:
            # Satellite only (most common)
            data = self.load_satellite_data(lat, lon, date)
            features = self.extract_satellite_features(data)
        
        # Add weather data (always available)
        weather = self.weather_model.get_conditions(lat, lon, date)
        features.update(weather)
        
        # Predict through cascade
        risk = self.cascade_model.predict_fire_risk(features, data_tier)
        
        # Add uncertainty based on data tier
        uncertainty = self.calculate_uncertainty(data_tier)
        
        return {
            'location': (lat, lon),
            'date': date,
            'fire_risk': risk,
            'uncertainty': uncertainty,
            'data_tier': data_tier,
            'features': features
        }
```

### Temporal Integration
```python
def integrate_temporal_data(location, date_range):
    """Combine different temporal resolutions"""
    
    # Static/slow-changing from annual data
    static_features = {
        'cdw_load': get_annual_cdw(location),  # Annual from AOP
        'species_composition': get_species(location),  # Rarely changes
        'topography': get_topography(location)  # Static
    }
    
    # Seasonal from periodic satellites
    seasonal_features = {
        'phenology_stage': get_phenology(location, date_range),  # Weekly
        'vegetation_indices': get_sentinel_ndvi(location, date_range),  # 5-day
        'soil_moisture': get_smap_moisture(location, date_range)  # 3-day
    }
    
    # Daily from MODIS/VIIRS
    daily_features = {
        'lst': get_modis_lst(location, date_range),
        'active_fire': get_viirs_fire(location, date_range)
    }
    
    # Sub-daily from weather
    hourly_features = {
        'temperature': get_hourly_temp(location, date_range),
        'humidity': get_hourly_rh(location, date_range),
        'wind': get_hourly_wind(location, date_range)
    }
    
    # Combine with appropriate temporal weights
    integrated = combine_temporal_features(
        static_features,
        seasonal_features,
        daily_features,
        hourly_features
    )
    
    return integrated
```

## Validation Strategy

### Cross-Validation Across Tiers
```python
def validate_cascade_model(model, validation_data):
    """Validate model performance across data tiers"""
    
    results = {
        'ground': {'mae': [], 'r2': [], 'auc': []},
        'aop': {'mae': [], 'r2': [], 'auc': []},
        'satellite': {'mae': [], 'r2': [], 'auc': []}
    }
    
    # Test Ground → AOP predictions
    for plot in validation_data['ground_plots']:
        # Get AOP data at plot location
        aop_at_plot = extract_aop_window(plot['location'])
        
        # Predict ground variables from AOP
        predicted = model.ground_to_aop.predict(aop_at_plot)
        actual = plot['measurements']
        
        results['ground']['mae'].append(mean_absolute_error(actual, predicted))
        results['ground']['r2'].append(r2_score(actual, predicted))
    
    # Test AOP → Satellite predictions
    for aop_tile in validation_data['aop_tiles']:
        # Get satellite data for tile
        sat_at_tile = extract_satellite_window(aop_tile['bounds'])
        
        # Predict AOP features from satellite
        predicted = model.aop_to_satellite.predict(sat_at_tile)
        actual = aop_tile['features']
        
        results['aop']['mae'].append(mean_absolute_error(actual, predicted))
        results['aop']['r2'].append(r2_score(actual, predicted))
    
    # Test fire predictions at each tier
    for fire_event in validation_data['fire_events']:
        for data_tier in ['ground', 'aop', 'satellite']:
            if data_tier in fire_event:
                predicted_risk = model.predict_fire_risk(
                    fire_event[data_tier],
                    data_tier
                )
                actual_burned = fire_event['burned_area']
                
                results[data_tier]['auc'].append(
                    roc_auc_score(actual_burned, predicted_risk)
                )
    
    return results
```

### Fire Event Validation
```python
def validate_against_fires(model, fire_database):
    """Validate using actual fire events"""
    
    validations = []
    
    for fire in fire_database:
        # Get pre-fire data at multiple tiers
        pre_fire_date = fire['start_date'] - timedelta(days=7)
        
        # Predict at each tier where data exists
        predictions = {}
        
        if fire['has_ground_data']:
            ground_risk = model.predict_fire_risk(
                fire['ground_data'],
                'ground'
            )
            predictions['ground'] = ground_risk
        
        if fire['has_aop_data']:
            aop_risk = model.predict_fire_risk(
                fire['aop_data'],
                'aop'
            )
            predictions['aop'] = aop_risk
        
        # Satellite always available
        sat_risk = model.predict_fire_risk(
            fire['satellite_data'],
            'satellite'
        )
        predictions['satellite'] = sat_risk
        
        # Compare to actual fire extent
        validation = {
            'fire_name': fire['name'],
            'predictions': predictions,
            'actual_area': fire['final_area'],
            'severity': fire['severity']
        }
        
        validations.append(validation)
    
    return validations
```

## Implementation Examples

### Example 1: Colorado Statewide Risk Map
```python
def generate_colorado_risk_map(date):
    """Generate fire risk map for entire state"""
    
    # Initialize model
    model = ThreeTierCascadeModel()
    model.load_pretrained('colorado_model.pkl')
    
    # Create grid
    grid = create_grid(
        bounds=COLORADO_BOUNDS,
        resolution=30  # meters
    )
    
    risk_map = np.zeros(grid.shape)
    data_tier_map = np.zeros(grid.shape, dtype=str)
    
    for i, j in grid.indices:
        lat, lon = grid.get_coords(i, j)
        
        # Check data availability
        if is_in_neon_plot(lat, lon):
            tier = 'ground'
        elif is_in_aop_flightbox(lat, lon):
            tier = 'aop'
        else:
            tier = 'satellite'
        
        # Get appropriate data
        data = load_data_for_tier(lat, lon, date, tier)
        
        # Predict risk
        risk = model.predict_fire_risk(data, tier)
        
        risk_map[i, j] = risk
        data_tier_map[i, j] = tier
    
    return risk_map, data_tier_map
```

### Example 2: Near Real-Time Monitoring
```python
def monitor_fire_risk_realtime():
    """Real-time fire risk monitoring system"""
    
    model = ThreeTierCascadeModel()
    
    while True:
        # Get latest satellite pass
        latest_satellite = get_latest_satellite_data()
        
        # Process high-risk areas first
        high_risk_areas = identify_high_risk_areas(latest_satellite)
        
        for area in high_risk_areas:
            # Check if we have better data
            if has_recent_aop(area):
                data = get_aop_data(area)
                tier = 'aop'
            else:
                data = latest_satellite[area]
                tier = 'satellite'
            
            # Add current weather
            weather = get_current_weather(area)
            data.update(weather)
            
            # Predict risk
            risk = model.predict_fire_risk(data, tier)
            
            # Alert if threshold exceeded
            if risk > ALERT_THRESHOLD:
                send_alert(area, risk)
        
        # Wait for next update
        time.sleep(3600)  # Check hourly
```

### Example 3: Model Training Script
```python
def train_three_tier_model():
    """Complete training pipeline"""
    
    # Load all data
    print("Loading NEON ground data...")
    ground_data = load_neon_ground_data(['NIWO', 'RMNP', 'CPER'])
    
    print("Loading AOP data...")
    aop_data = load_neon_aop_data(['NIWO', 'RMNP', 'CPER'], years=range(2018, 2024))
    
    print("Loading satellite data...")
    satellite_data = load_satellite_data(
        sources=['sentinel2', 'landsat8', 'modis'],
        bounds=COLORADO_BOUNDS,
        dates=('2018-01-01', '2023-12-31')
    )
    
    print("Loading fire labels...")
    fire_labels = load_fire_database()
    
    # Initialize model
    model = ThreeTierCascadeModel()
    
    # Train cascade
    model.train_cascade(
        ground_data=ground_data,
        aop_data=aop_data,
        satellite_data=satellite_data,
        fire_labels=fire_labels
    )
    
    # Validate
    validation_results = validate_cascade_model(model, validation_data)
    
    print(f"Ground tier R²: {np.mean(validation_results['ground']['r2']):.3f}")
    print(f"AOP tier R²: {np.mean(validation_results['aop']['r2']):.3f}")
    print(f"Satellite tier R²: {np.mean(validation_results['satellite']['r2']):.3f}")
    
    print(f"Fire prediction AUC: {np.mean(validation_results['satellite']['auc']):.3f}")
    
    # Save model
    model.save('colorado_three_tier_model.pkl')
    
    return model

if __name__ == "__main__":
    model = train_three_tier_model()
```

## Key Advantages

1. **Maximizes data value**: Limited ground data trains broader coverage
2. **Uncertainty quantification**: Know confidence based on data tier
3. **Operational flexibility**: Works with whatever data is available
4. **Temporal integration**: Combines different update frequencies
5. **Validation at each tier**: Can validate crosswalks independently

## Next Steps

1. Implement Model A: Ground to AOP crosswalk
2. Validate with NEON plots at NIWO
3. Implement Model B: AOP to Satellite crosswalk
4. Test on Cameron Peak Fire area
5. Deploy operational system for Colorado
6. Expand to other western states with NEON sites