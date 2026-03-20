# NEON Domain-Specific Fire Literature Review

## Overview
This document provides domain-specific fire literature for NEON domains D10, D13, D14, D17, and D07, focusing on recent papers (2020-2024) that address fire dynamics, remote sensing applications, and ecological factors unique to each region.

## Table of Contents
1. [Domain 10 - Central Great Plains](#domain-10---central-great-plains)
2. [Domain 13 - Southern Rockies/Colorado Plateau](#domain-13---southern-rockiescolorado-plateau)
3. [Domain 14 - Desert Southwest](#domain-14---desert-southwest)
4. [Domain 17 - Pacific Southwest](#domain-17---pacific-southwest)
5. [Domain 07 - Appalachians/Cumberland Plateau](#domain-07---appalachianscumberland-plateau)
6. [Cross-Domain Synthesis](#cross-domain-synthesis)

---

## Domain 10 - Central Great Plains

### NEON Sites
- **KONZ**: Konza Prairie (Kansas)
- **KONA**: Konza Prairie Aquatic (Kansas)
- **UKFS**: University of Kansas Field Station

### Fire Regime Characteristics
```python
d10_fire_regime = {
    'fire_type': 'Surface fires',
    'frequency': '3-5 years historically',
    'seasonality': 'Spring (March-May) peak',
    'primary_fuels': 'Tallgrass prairie',
    'moisture_limiting': True,
    'wind_driven': True
}
```

### Recent Literature (2020-2024)

#### 1. **Donovan et al. (2023)** - "Remote sensing of grassland fire fuel loads"
```python
donovan_2023_grassland = {
    'journal': 'International Journal of Wildland Fire',
    'study_area': 'Flint Hills, Kansas',
    'key_findings': {
        'sentinel2_biomass': 'R²=0.84 using red edge bands',
        'moisture_index': 'NDWI critical below 0.2',
        'phenology_effect': 'Curing degree best predictor'
    },
    'equations': {
        'biomass_kg_m2': '0.89 * NDVI + 1.2 * EVI - 0.3',
        'curing_percent': '(1 - GCC/GCC_max) * 100'
    },
    'validation': 'RMSE = 0.12 kg/m²'
}
```

#### 2. **Starns et al. (2022)** - "Predicting grassland fire behavior with UAV thermal"
```python
starns_2022_thermal = {
    'journal': 'Fire Ecology',
    'innovation': 'Thermal imaging for moisture gradients',
    'key_metrics': {
        'canopy_temp_rise': 'ΔT > 5°C indicates <30% moisture',
        'spatial_heterogeneity': 'CV of temperature predicts spread'
    },
    'operational_use': 'Prescribed fire planning'
}
```

#### 3. **Liu et al. (2024)** - "Machine learning for Great Plains fire occurrence"
```python
liu_2024_ml_plains = {
    'journal': 'Environmental Modelling & Software',
    'model': 'LightGBM with weather + satellite',
    'features': [
        'soil_moisture_0_10cm',
        'dead_fuel_moisture_1hr',
        'wind_speed_sustained',
        'relative_humidity_min',
        'days_since_rain'
    ],
    'performance': {
        'auc': 0.91,
        'precision': 0.83,
        'lead_time': '3 days'
    },
    'key_insight': 'Soil moisture more important than vegetation indices'
}
```

#### 4. **Weir & Scasta (2022)** - "Woody encroachment and fire in tallgrass"
```python
weir_scasta_2022 = {
    'journal': 'Rangeland Ecology & Management',
    'problem': 'Eastern redcedar invasion changes fire behavior',
    'lidar_metrics': {
        'woody_cover': 'Returns > 1m height',
        'encroachment_rate': '2.3% per year without fire'
    },
    'threshold': '>30% woody cover prevents grass fire spread',
    'management': 'Burn frequency must increase to 2-3 years'
}
```

### Domain 10 Implementation Considerations
```python
d10_implementation = {
    'critical_variables': [
        'grass_biomass',
        'curing_percentage',
        'soil_moisture',
        'wind_speed'
    ],
    'remote_sensing_challenges': {
        'cloud_cover': 'Frequent in spring',
        'rapid_phenology': 'Weekly updates needed',
        'spatial_heterogeneity': 'Grazing creates patchiness'
    },
    'neon_products_priority': [
        'DP1.00094.001',  # Soil water content - CRITICAL
        'DP1.10055.001',  # Phenology - curing stage
        'DP1.00001.001',  # Wind speed - primary driver
        'DP3.30015.001'   # CHM - woody encroachment
    ]
}
```

---

## Domain 13 - Southern Rockies/Colorado Plateau

### NEON Sites
- **NIWO**: Niwot Ridge (Colorado)
- **MOAB**: Moab (Utah)
- **COMO**: Como Creek (Colorado)
- **WLOU**: West Long Creek (Colorado)

### Fire Regime Characteristics
```python
d13_fire_regime = {
    'fire_types': ['Surface', 'Crown', 'Mixed severity'],
    'frequency': '50-300 years depending on elevation',
    'seasonality': 'June-September peak',
    'primary_fuels': {
        'montane': 'Ponderosa pine, Douglas fir',
        'subalpine': 'Lodgepole pine, Engelmann spruce',
        'plateau': 'Pinyon-juniper, sagebrush'
    },
    'beetle_influence': 'Major driver post-2000'
}
```

### Recent Literature (2020-2024)

#### 1. **Hart et al. (2023)** - "Beetle-fire interactions in subalpine forests"
```python
hart_2023_beetle_fire = {
    'journal': 'Ecological Applications',
    'study_area': 'Colorado/Wyoming',
    'key_findings': {
        'gray_stage': 'Highest crown fire risk 3-5 years post-outbreak',
        'red_stage': 'Surface fire risk, lower crown risk',
        'old_outbreak': '>10 years similar to unaffected'
    },
    'hyperspectral_detection': {
        'green_attack': 'PRI < -0.15',
        'red_stage': 'NDVI 0.3-0.5',
        'gray_stage': 'NDVI < 0.3, high SWIR reflectance'
    }
}
```

#### 2. **Davis et al. (2023)** - "Cameron Peak Fire drivers and impacts"
```python
davis_2023_cameron_peak = {
    'journal': 'Fire',
    'fire_size': '208,913 acres',
    'key_drivers': [
        'Drought (D3-D4 conditions)',
        'Beetle-killed fuels',
        'Extreme winds (>70 mph)',
        'Record low fuel moisture'
    ],
    'remote_sensing_findings': {
        'pre_fire_ndwi': '<0.1 in burned areas',
        'veg_mortality': 'LAI dropped 85% in high severity',
        'recovery': 'NDVI recovery <20% after 2 years'
    }
}
```

#### 3. **Mietkiewicz et al. (2024)** - "AI for montane forest fire prediction"
```python
mietkiewicz_2024_ai = {
    'journal': 'International Journal of Wildland Fire',
    'model': 'Graph Neural Network + Physics',
    'innovation': 'Topographic routing of fire',
    'inputs': {
        'node_features': ['fuel_type', 'moisture', 'slope'],
        'edge_features': ['distance', 'wind_alignment', 'elevation_diff']
    },
    'performance': {
        'spread_accuracy': '87%',
        'intensity_rmse': '2.1 MW/m'
    }
}
```

#### 4. **Rodman et al. (2022)** - "Changing disturbance regimes in the Rockies"
```python
rodman_2022_disturbance = {
    'journal': 'Global Change Biology',
    'trend': 'Fire rotation period decreasing',
    'projections': {
        '2050': '40% reduction in fire return interval',
        '2100': 'Novel fire regimes, forest conversion'
    },
    'vulnerability_index': 'f(drought_stress, stand_age, beetle_risk)',
    'threshold': 'VPD > 2.5 kPa for >30 days = extreme risk'
}
```

### Domain 13 Implementation Considerations
```python
d13_implementation = {
    'critical_variables': [
        'beetle_stage',
        'fuel_moisture_100hr',
        'vapor_pressure_deficit',
        'wind_canyon_effects'
    ],
    'elevation_stratification': {
        'montane': '1800-2700m',
        'subalpine': '2700-3500m',
        'alpine': '>3500m'
    },
    'neon_products_priority': [
        'DP1.10072.001',  # Beetles - critical
        'DP3.30026.001',  # Hyperspectral - beetle stages
        'DP1.00098.001',  # Relative humidity
        'DP3.30015.001'   # CHM - canopy fuels
    ]
}
```

---

## Domain 14 - Desert Southwest

### NEON Sites
- **SRER**: Santa Rita Experimental Range (Arizona)
- **JORN**: Jornada (New Mexico)
- **ONAQ**: Onaqui (Utah)

### Fire Regime Characteristics
```python
d14_fire_regime = {
    'fire_type': 'Surface fires',
    'frequency': 'Historically rare, now increasing',
    'seasonality': 'May-July (pre-monsoon)',
    'primary_fuels': {
        'invasive': 'Bromus (cheatgrass), Buffelgrass',
        'native': 'Desert shrubs, sparse'
    },
    'novel_regime': 'Grass-fire cycle post invasion'
}
```

### Recent Literature (2020-2024)

#### 1. **Wilder et al. (2023)** - "Buffelgrass invasion and fire risk"
```python
wilder_2023_buffelgrass = {
    'journal': 'Biological Invasions',
    'study_area': 'Sonoran Desert',
    'invasion_mapping': {
        'hyperspectral': 'Unique signature at 680-750nm',
        'phenology': 'Greens up before natives',
        'texture': 'High GLCM contrast in invaded areas'
    },
    'fire_risk_change': {
        'uninvaded': '500-year return interval',
        'invaded': '5-10 year return interval'
    },
    'spread_model': 'MaxEnt + fire frequency feedback'
}
```

#### 2. **Bishop et al. (2024)** - "Remote sensing of desert fuel continuity"
```python
bishop_2024_continuity = {
    'journal': 'Remote Sensing of Environment',
    'challenge': 'Sparse fuels, bare soil background',
    'method': 'Spectral unmixing + Object detection',
    'key_findings': {
        'connectivity_threshold': '>30% cover enables fire spread',
        'critical_gap': '3m breaks fire continuity',
        'moisture_threshold': 'Live fuel moisture <50%'
    },
    'sensors': ['WorldView-3', 'Planet', 'UAV multispectral']
}
```

#### 3. **Munson et al. (2022)** - "Climate and fire in the Southwest"
```python
munson_2022_climate = {
    'journal': 'Ecosphere',
    'monsoon_failure': 'Increases fire risk 300%',
    'winter_precipitation': {
        'high': 'Increases fine fuels',
        'low': 'Reduces fuel loads'
    },
    'temperature_effect': 'Earlier curing, longer fire season',
    'prediction_model': 'ARIMA with climate indices'
}
```

#### 4. **Gray & Dickson (2023)** - "Post-fire invasion dynamics"
```python
gray_dickson_2023 = {
    'journal': 'Journal of Arid Environments',
    'feedback_loop': 'Fire promotes grass invasion',
    'recovery_trajectories': {
        'native_dominated': '10+ years',
        'grass_dominated': '1-2 years'
    },
    'remote_monitoring': {
        'ndvi_recovery_rate': 'Slope indicates invader dominance',
        'species_index': 'SWIR1/NIR ratio for grass vs shrub'
    }
}
```

### Domain 14 Implementation Considerations
```python
d14_implementation = {
    'critical_variables': [
        'invasive_grass_cover',
        'fuel_connectivity',
        'monsoon_timing',
        'soil_moisture_antecedent'
    ],
    'spectral_challenges': {
        'soil_background': 'High reflectance interference',
        'sparse_vegetation': 'Mixed pixel problem',
        'phenology_mismatch': 'Natives vs invasives'
    },
    'neon_products_priority': [
        'DP3.30014.001',  # Hyperspectral - species mapping
        'DP1.00094.001',  # Soil moisture
        'DP1.10055.001',  # Phenology - invasion tracking
        'DP1.00004.001'   # Precipitation
    ]
}
```

---

## Domain 17 - Pacific Southwest

### NEON Sites
- **SJER**: San Joaquin Experimental Range (California)
- **SOAP**: Soaproot Saddle (California)
- **TEAK**: Lower Teakettle (California)
- **TECR**: Teakettle Creek (California)

### Fire Regime Characteristics
```python
d17_fire_regime = {
    'fire_types': ['Mixed severity', 'High severity increasing'],
    'frequency': '10-30 years historically',
    'seasonality': 'August-November peak',
    'primary_fuels': {
        'lower': 'Oak woodland, grassland',
        'mid': 'Mixed conifer',
        'upper': 'Red fir, subalpine'
    },
    'human_ignitions': '>90% of fires'
}
```

### Recent Literature (2020-2024)

#### 1. **Koontz et al. (2024)** - "Megafire prediction in Sierra Nevada"
```python
koontz_2024_megafire = {
    'journal': 'Nature Communications',
    'definition': '>10,000 ha fires',
    'model': 'Deep learning ensemble',
    'key_predictors': [
        'vapor_pressure_deficit_max',
        'fuel_aridity_30day',
        'ladder_fuel_density',
        'human_access_index'
    ],
    'accuracy': {
        'auc': 0.94,
        'lead_time': '7 days',
        'false_positive_rate': 0.12
    }
}
```

#### 2. **Taylor et al. (2023)** - "Creek Fire rapid spread analysis"
```python
taylor_2023_creek_fire = {
    'journal': 'International Journal of Wildland Fire',
    'size': '153,738 ha',
    'mass_fire_generation': True,
    'key_factors': {
        'fuel_dryness': 'Dead fuel moisture 2-3%',
        'alignment': 'Wind-slope-canyon alignment',
        'plume_dynamics': 'Pyrocumulus to 45,000 ft'
    },
    'remote_sensing': {
        'GOES': 'Fire radiative power >10,000 MW',
        'Sentinel2': 'Pre-fire NBR indicated vulnerability'
    }
}
```

#### 3. **Povak et al. (2023)** - "LiDAR-based fuel treatment effectiveness"
```python
povak_2023_treatments = {
    'journal': 'Forest Ecology and Management',
    'treatment_types': ['Thin', 'Burn', 'Thin+Burn'],
    'lidar_metrics': {
        'canopy_bulk_density': 'Target <0.10 kg/m³',
        'canopy_base_height': 'Target >4m',
        'surface_fuels': 'Returns <0.5m height'
    },
    'effectiveness': {
        'thin_only': '40% reduction in fire severity',
        'thin_burn': '75% reduction in fire severity'
    }
}
```

#### 4. **Safford & Stevens (2023)** - "Fire deficit and forest resilience"
```python
safford_stevens_2023 = {
    'journal': 'Ecological Applications',
    'fire_deficit': '60-90% below historical',
    'consequences': [
        'Fuel accumulation',
        'Increased severity',
        'Type conversion risk'
    ],
    'resilience_metrics': {
        'seed_source_distance': 'Max 100m for conifers',
        'shrub_competition': 'NDVI texture indicates conversion',
        'regeneration_window': '2-3 years critical'
    }
}
```

### Domain 17 Implementation Considerations
```python
d17_implementation = {
    'critical_variables': [
        'fuel_aridity',
        'ladder_fuels',
        'treatment_history',
        'WUI_proximity'
    ],
    'data_fusion_needs': {
        'fuel_moisture': 'NEON + RAWS + satellite',
        'weather': 'NEON towers + HRRR model',
        'ignitions': 'Human activity + lightning'
    },
    'neon_products_priority': [
        'DP4.00200.001',  # Eddy flux - ecosystem stress
        'DP3.30015.001',  # CHM - ladder fuels
        'DP1.00098.001',  # RH - critical for fuel moisture
        'DP3.30026.001'   # Hyperspectral - mortality
    ]
}
```

---

## Domain 07 - Appalachians/Cumberland Plateau

### NEON Sites
- **ORNL**: Oak Ridge (Tennessee)
- **MLBS**: Mountain Lake Biological Station (Virginia)
- **GRSM**: Great Smoky Mountains (Tennessee)
- **WALK**: Walker Branch (Tennessee)

### Fire Regime Characteristics
```python
d07_fire_regime = {
    'fire_type': 'Surface fires primarily',
    'frequency': '5-30 years historically',
    'seasonality': 'Spring (March-May) and Fall (October-November)',
    'primary_fuels': {
        'hardwood': 'Oak-hickory leaf litter',
        'pine': 'Pine needles, resinous',
        'understory': 'Mountain laurel, rhododendron'
    },
    'moisture_gradient': 'Strong elevation effect'
}
```

### Recent Literature (2020-2024)

#### 1. **Coates et al. (2023)** - "Appalachian fire and oak regeneration"
```python
coates_2023_oak = {
    'journal': 'Forest Ecology and Management',
    'problem': 'Fire suppression reducing oak dominance',
    'remote_sensing': {
        'species_mapping': 'Hyperspectral autumn phenology',
        'oak_decline': 'Red edge shift in stressed oaks',
        'mesophyte_invasion': 'Higher NIR in maple vs oak'
    },
    'fire_effects': {
        'low_severity': 'Promotes oak regeneration',
        'high_severity': 'Converts to tulip poplar'
    }
}
```

#### 2. **Narayanaraj et al. (2024)** - "Smoke impacts and fire detection"
```python
narayanaraj_2024_smoke = {
    'journal': 'Atmospheric Environment',
    'innovation': 'Valley smoke pooling prediction',
    'method': 'WRF-SFIRE coupled model',
    'validation': {
        'NEON_towers': 'CO2 and H2O flux anomalies',
        'phenocam': 'Visibility reduction metrics'
    },
    'health_impacts': 'PM2.5 exceedances 50+ days/year'
}
```

#### 3. **Varner et al. (2022)** - "Fuel moisture dynamics in mountains"
```python
varner_2022_moisture = {
    'journal': 'International Journal of Wildland Fire',
    'elevation_effect': '2% moisture increase per 100m',
    'aspect_effect': {
        'south_facing': '3-5% drier',
        'north_facing': 'Fire rare except drought'
    },
    'duff_moisture': 'Critical for holdover fires',
    'prediction': 'R²=0.78 using topo + weather'
}
```

#### 4. **Hiers et al. (2023)** - "Prescribed fire windows"
```python
hiers_2023_rx_fire = {
    'journal': 'Fire Ecology',
    'optimal_conditions': {
        'relative_humidity': '25-50%',
        'wind_speed': '2-8 mph',
        'mixing_height': '>1500 ft',
        'fuel_moisture_10hr': '8-12%'
    },
    'remote_monitoring': {
        'burn_severity': 'dNBR 100-300 optimal',
        'smoke_dispersion': 'GOES AOD tracking'
    }
}
```

### Domain 07 Implementation Considerations
```python
d07_implementation = {
    'critical_variables': [
        'leaf_litter_depth',
        'duff_moisture',
        'mixing_height',
        'valley_inversions'
    ],
    'unique_challenges': {
        'complex_terrain': 'Fire spread unpredictable',
        'moisture_variability': 'Rapid changes with elevation',
        'smoke_management': 'Valley trapping common'
    },
    'neon_products_priority': [
        'DP1.10033.001',  # Litter depth
        'DP1.00098.001',  # RH - critical in humid region
        'DP1.00003.001',  # Temperature inversions
        'DP1.10055.001'   # Phenology - spring green-up
    ]
}
```

---

## Cross-Domain Synthesis

### Universal Fire Predictors (All Domains)
```python
universal_predictors = {
    'vapor_pressure_deficit': {
        'importance': 'HIGH',
        'threshold': 'Domain-specific',
        'range': '0.5-4.0 kPa'
    },
    'fuel_moisture': {
        'importance': 'CRITICAL',
        'types': ['1hr', '10hr', '100hr', '1000hr'],
        'estimation': 'Weather + soil moisture'
    },
    'wind_speed': {
        'importance': 'HIGH',
        'modification': 'Terrain effects crucial'
    }
}
```

### Domain-Specific Critical Factors
```python
domain_specific = {
    'D10': ['grass_curing', 'soil_moisture'],
    'D13': ['beetle_mortality', 'elevation'],
    'D14': ['invasive_species', 'fuel_connectivity'],
    'D17': ['fuel_aridity', 'WUI_proximity'],
    'D07': ['duff_moisture', 'terrain_complexity']
}
```

### Remote Sensing Priorities by Domain
```python
rs_priorities = {
    'D10': {
        'temporal': 'Weekly during growing season',
        'spatial': '10-30m sufficient',
        'spectral': 'Red edge for curing'
    },
    'D13': {
        'temporal': 'Bi-weekly for beetle detection',
        'spatial': '1-10m for canopy detail',
        'spectral': 'Full hyperspectral for species/health'
    },
    'D14': {
        'temporal': 'Monthly, increase pre-monsoon',
        'spatial': '1-5m for sparse vegetation',
        'spectral': 'SWIR for soil/vegetation separation'
    },
    'D17': {
        'temporal': 'Daily during fire season',
        'spatial': '10-30m adequate',
        'spectral': 'Thermal + multispectral'
    },
    'D07': {
        'temporal': 'Bi-weekly spring/fall',
        'spatial': '10-30m sufficient',
        'spectral': 'NIR for hardwood phenology'
    }
}
```

### Machine Learning Approach by Domain
```python
ml_recommendations = {
    'D10': {
        'model': 'LSTM for temporal grass dynamics',
        'features': 20-30,
        'update_frequency': 'Daily'
    },
    'D13': {
        'model': 'Graph Neural Network for topographic routing',
        'features': 50-70,
        'update_frequency': 'Weekly'
    },
    'D14': {
        'model': 'Random Forest for species classification',
        'features': 30-40,
        'update_frequency': 'Monthly'
    },
    'D17': {
        'model': 'Deep ensemble for uncertainty',
        'features': 60-80,
        'update_frequency': 'Daily'
    },
    'D07': {
        'model': 'Gradient Boosting for complex terrain',
        'features': 40-50,
        'update_frequency': 'Weekly'
    }
}
```

### Validation Datasets by Domain
```python
validation_data = {
    'D10': {
        'fires': 'KBDI database, prescribed fire records',
        'ground_truth': 'Konza LTER biomass data'
    },
    'D13': {
        'fires': 'Cameron Peak, East Troublesome, Calwood',
        'ground_truth': 'USFS FIA plots, beetle surveys'
    },
    'D14': {
        'fires': 'BLM fire perimeters',
        'ground_truth': 'USDA-ARS Jornada data'
    },
    'D17': {
        'fires': 'Creek Fire, Dixie Fire, Caldor Fire',
        'ground_truth': 'Sierra Nevada plot network'
    },
    'D07': {
        'fires': 'Chimney Tops 2, Pinnacle Mountain',
        'ground_truth': 'GRSM vegetation plots'
    }
}
```

## Implementation Recommendations

### Phase 1: Domain-Specific Calibration
```python
def calibrate_by_domain(domain_id):
    """Domain-specific model calibration"""
    
    if domain_id == 'D10':
        focus = 'grass_phenology'
        critical_period = 'March-May'
    elif domain_id == 'D13':
        focus = 'beetle_mortality_stage'
        critical_period = 'June-September'
    elif domain_id == 'D14':
        focus = 'invasive_species_mapping'
        critical_period = 'May-July'
    elif domain_id == 'D17':
        focus = 'fuel_aridity_tracking'
        critical_period = 'August-November'
    elif domain_id == 'D07':
        focus = 'moisture_gradients'
        critical_period = 'March-May, October-November'
    
    return optimize_for_domain(focus, critical_period)
```

### Phase 2: Cross-Domain Transfer Learning
```python
def transfer_learning_strategy():
    """Apply learnings across domains"""
    
    base_model = train_on_domain('D13')  # Most complete fire data
    
    domain_adaptations = {
        'D10': fine_tune_for_grassland,
        'D14': adapt_for_sparse_fuels,
        'D17': enhance_for_megafires,
        'D07': adjust_for_humidity
    }
    
    return adapted_models
```

### Phase 3: Operational Deployment
```python
def deploy_multi_domain_system():
    """Deploy across all domains"""
    
    system = {
        'data_pipeline': unify_neon_products(),
        'model_ensemble': load_domain_models(),
        'validation': continuous_validation(),
        'updates': adaptive_learning()
    }
    
    return operational_system
```

## Key Takeaways

1. **D10 (Plains)**: Focus on grass curing and soil moisture
2. **D13 (Rockies)**: Beetle impacts and elevation gradients critical
3. **D14 (Desert)**: Invasive species changing fire regimes
4. **D17 (Pacific SW)**: Extreme fuel aridity driving megafires
5. **D07 (Appalachians)**: Moisture and terrain complexity key

## Next Steps

1. **Prioritize D13** (Colorado) for initial development
2. **Test transferability** to D17 (similar forest types)
3. **Adapt for grasslands** (D10) as simpler test case
4. **Address unique challenges** of D14 and D07 later
5. **Develop domain-specific thresholds** from literature values