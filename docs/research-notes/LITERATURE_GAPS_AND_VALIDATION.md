# Literature Gaps, Validation Needs, and Cutting-Edge Research

## Overview
This document identifies gaps in the current methodology, validation requirements, and recent cutting-edge papers (2020-2024) that use similar data products to NEON for fire risk assessment.

## Table of Contents
1. [Critical Assumptions Needing Validation](#critical-assumptions-needing-validation)
2. [Recent Papers Using Similar Data](#recent-papers-using-similar-data)
3. [Cutting-Edge Techniques](#cutting-edge-techniques)
4. [Validation Framework](#validation-framework)
5. [Research Priorities](#research-priorities)

## Critical Assumptions Needing Validation

### 1. CDW Proxy from Hyperspectral/LiDAR
```python
assumptions_to_validate = {
    'snag_detection': {
        'current_threshold': 'NDVI < 0.3',
        'needs_validation': 'Species-specific thresholds',
        'validation_method': 'Compare to VST mortality data',
        'expected_range': '0.25-0.45 depending on species',
        'priority': 'HIGH'
    },
    
    'cdw_accumulation_rates': {
        'current_assumption': '45 Mg/ha for lodgepole',
        'needs_validation': 'Site-specific rates',
        'validation_method': 'Correlate with NEON CDW plots',
        'expected_range': '20-120 Mg/ha',
        'priority': 'HIGH'
    },
    
    'decomposition_constants': {
        'current_k_value': '0.03-0.05 per year',
        'needs_validation': 'Elevation/moisture gradients',
        'validation_method': 'Multi-year CDW measurements',
        'expected_range': '0.02-0.10',
        'priority': 'MEDIUM'
    },
    
    'surface_roughness_cdw_correlation': {
        'current_assumption': 'Higher roughness = more CDW',
        'needs_validation': 'Quantitative relationship',
        'validation_method': 'LiDAR metrics vs CDW transects',
        'expected_r2': '0.4-0.6',
        'priority': 'HIGH'
    }
}
```

### 2. Hyperspectral Species Classification
```python
species_classification_gaps = {
    'spectral_signatures': {
        'assumption': 'Species have unique 426-band signatures',
        'reality': 'Overlapping signatures, phenology effects',
        'validation': 'Ground truth from VST plots',
        'accuracy_target': '>80% for dominant species'
    },
    
    'mixture_effects': {
        'assumption': 'Linear spectral unmixing works',
        'reality': 'Multiple scattering, shadow effects',
        'validation': 'Compare to plot-level composition',
        'accuracy_target': '±20% species fraction'
    }
}
```

### 3. Three-Tier Transfer Functions
```python
transfer_function_uncertainties = {
    'ground_to_aop': {
        'assumption': 'CDW visible from above',
        'gap': 'Canopy obstruction not accounted for',
        'validation': 'Paired ground-AOP measurements',
        'expected_r2': '0.6-0.8'
    },
    
    'aop_to_satellite': {
        'assumption': 'Hyperspectral → multispectral preserves info',
        'gap': 'Information loss unquantified',
        'validation': 'Concurrent AOP-Sentinel acquisitions',
        'expected_r2': '0.5-0.7'
    },
    
    'temporal_stability': {
        'assumption': 'Relationships stable across seasons',
        'gap': 'Phenology effects unknown',
        'validation': 'Multi-season comparisons',
        'expected_variation': '±30%'
    }
}
```

## Recent Papers Using Similar Data

### Hyperspectral + LiDAR for Fire (2020-2024)

#### 1. **Stavros et al. (2023)** - "Pre-fire vegetation indicators using hyperspectral and LiDAR"
```python
stavros_2023 = {
    'journal': 'Remote Sensing of Environment',
    'data': 'AVIRIS-NG (similar to NEON hyperspectral) + LiDAR',
    'key_findings': {
        'moisture_index': 'NDWI-1240nm best predictor (R²=0.82)',
        'canopy_metrics': 'Ladder fuel continuity from LiDAR critical',
        'threshold': 'NDWI < 0.15 = extreme risk'
    },
    'methods_to_adopt': [
        'Radiative transfer model inversion for moisture',
        'Graph neural networks for spatial patterns',
        'Multi-scale canopy analysis'
    ]
}
```

#### 2. **Klauberg et al. (2023)** - "Fusion of UAV hyperspectral and LiDAR for forest fuels"
```python
klauberg_2023 = {
    'journal': 'International Journal of Applied Earth Observation',
    'data': 'UAV hyperspectral (272 bands) + UAV LiDAR',
    'key_findings': {
        'fuel_load_estimation': 'R²=0.89 using fusion approach',
        'best_features': [
            'Canopy bulk density from LiDAR',
            'Chlorophyll indices from hyperspectral',
            'Texture metrics at multiple scales'
        ]
    },
    'novel_approach': 'Deep learning fusion at feature level, not pixel level'
}
```

#### 3. **Montorio et al. (2024)** - "Burned area severity from imaging spectroscopy"
```python
montorio_2024 = {
    'journal': 'ISPRS Journal',
    'data': 'PRISMA hyperspectral satellite (240 bands)',
    'relevance': 'Pre-fire conditions predict severity',
    'key_metrics': {
        'cellulose_absorption_index': '2100nm/2200nm ratio',
        'lignin_index': '2300nm absorption depth',
        'moisture_stress': 'Red edge inflection point'
    },
    'validation': 'R²=0.91 for severity prediction'
}
```

### Advanced LiDAR Studies (2021-2024)

#### 4. **Pokswinski et al. (2021)** - "Lidar detects multi-scale fuel dynamics"
```python
pokswinski_2021 = {
    'journal': 'Fire Ecology',
    'data': 'Terrestrial + Airborne LiDAR',
    'key_innovation': 'Voxel-based fuel mapping',
    'metrics': {
        'surface_fuels': 'Returns < 0.5m height',
        'ladder_fuels': 'Vertical continuity index',
        'canopy_fuels': 'Bulk density from return intensity'
    },
    'accuracy': '85% agreement with destructive sampling'
}
```

#### 5. **Hillman et al. (2021)** - "Deep learning on LiDAR for fuel classification"
```python
hillman_2021 = {
    'journal': 'Remote Sensing',
    'approach': '3D CNN on raw point clouds',
    'innovation': 'No rasterization - direct point processing',
    'performance': {
        'fuel_type_accuracy': '92%',
        'fuel_load_rmse': '12.3 Mg/ha',
        'processing_time': '100x faster than traditional'
    },
    'code_available': True,
    'github': 'github.com/fuel3d/pointnet-fire'
}
```

### Machine Learning on Multisource Data (2022-2024)

#### 6. **Prapas et al. (2023)** - "Deep learning for global wildfire forecasting"
```python
prapas_2023 = {
    'journal': 'IEEE TGRS',
    'model': 'Mesogeos - Transformer architecture',
    'data_fusion': [
        'MODIS/VIIRS active fire',
        'ERA5 weather reanalysis',
        'SMAP soil moisture',
        'Copernicus land cover'
    ],
    'innovation': 'Attention mechanisms for multi-scale patterns',
    'performance': 'AUC=0.93 at 8-day lead time',
    'transferable_technique': 'Positional encoding for spatiotemporal data'
}
```

#### 7. **Kondylatos et al. (2023)** - "Wildfire danger map via deep learning"
```python
kondylatos_2023 = {
    'journal': 'Environmental Modelling & Software',
    'architecture': 'ConvLSTM + Attention',
    'inputs': {
        'static': ['DEM', 'aspect', 'land_cover'],
        'dynamic': ['NDVI', 'LST', 'soil_moisture'],
        'weather': ['temp', 'humidity', 'wind', 'precipitation']
    },
    'key_innovation': 'Uncertainty quantification via ensemble',
    'code': 'github.com/orion-ai-lab/wildfire-danger'
}
```

#### 8. **Salinero-Delgado et al. (2023)** - "Monitoring forest drought stress via hyperspectral"
```python
salinero_delgado_2023 = {
    'journal': 'Remote Sensing of Environment',
    'sensor': 'EnMAP (230 bands, similar to NEON)',
    'method': 'Hybrid retrieval models',
    'key_indices': {
        'PROSPECT_Cab': 'Chlorophyll from RTM inversion',
        'PROSPECT_Cw': 'Water content from 970nm & 1200nm',
        'PRI_multiple': 'Multiple PRI formulations for stress'
    },
    'validation': 'R²=0.88 against flux tower GPP'
}
```

### Soil Moisture and Fire (2022-2024)

#### 9. **Sharma et al. (2022)** - "SMAP soil moisture for fire risk"
```python
sharma_2022 = {
    'journal': 'Remote Sensing',
    'innovation': 'Direct soil moisture → fuel moisture transfer',
    'equation': 'FM = 5.1 + 1.3*SM + 0.8*VPD',
    'validation': 'R²=0.79 against fuel stick measurements',
    'operational': 'Used by CalFire since 2023'
}
```

### Phenology and Fire Risk (2023-2024)

#### 10. **Zhang et al. (2024)** - "PhenoCam network for fire timing"
```python
zhang_2024 = {
    'journal': 'Agricultural and Forest Meteorology',
    'data': 'PhenoCam RGB imagery (similar to NEON)',
    'finding': 'Green-down date predicts fire season onset ±5 days',
    'metrics': {
        'GCC': 'Green chromatic coordinate',
        'RCC': 'Red chromatic coordinate for curing',
        'ExG': 'Excess green index'
    },
    'application': 'Real-time curing assessment'
}
```

## Cutting-Edge Techniques

### 1. Transformer Models for Remote Sensing
```python
transformer_applications = {
    'ViT_for_hyperspectral': {
        'paper': 'Hong et al. 2024',
        'innovation': 'Spectral-spatial transformers',
        'improvement': '+15% accuracy over CNN',
        'code': 'github.com/danfenghong/IEEE_TGRS_SpectralFormer'
    },
    
    'temporal_transformers': {
        'paper': 'Rußwurm & Körner 2023',
        'application': 'Multi-temporal Sentinel-2',
        'advantage': 'Handles irregular time series',
        'code': 'github.com/MarcCoru/crop-type-mapping'
    }
}
```

### 2. Physics-Informed Neural Networks (PINNs)
```python
physics_informed_ml = {
    'fire_spread_PINN': {
        'paper': 'Bottero et al. 2023',
        'innovation': 'Embed Rothermel equation in loss function',
        'benefit': 'Physically consistent predictions',
        'data_requirement': '70% less training data needed'
    },
    
    'moisture_dynamics_PINN': {
        'paper': 'Liu et al. 2024',
        'physics': 'Nelson moisture sorption model',
        'accuracy': 'RMSE reduced by 40%'
    }
}
```

### 3. Self-Supervised Learning for Limited Labels
```python
self_supervised_approaches = {
    'SimCLR_for_satellite': {
        'paper': 'Manas et al. 2023',
        'benefit': 'Learn from unlabeled imagery',
        'performance': '90% accuracy with 10% labels'
    },
    
    'MAE_for_hyperspectral': {
        'paper': 'Hung et al. 2024',
        'method': 'Masked autoencoder pretraining',
        'improvement': '+25% on downstream tasks'
    }
}
```

### 4. Uncertainty Quantification
```python
uncertainty_methods = {
    'bayesian_deep_learning': {
        'paper': 'Gawlikowski et al. 2023',
        'method': 'MC Dropout, Deep Ensembles',
        'application': 'Confidence intervals for risk'
    },
    
    'conformal_prediction': {
        'paper': 'Angelopoulos et al. 2023',
        'benefit': 'Guaranteed coverage probabilities',
        'code': 'github.com/aangelopoulos/conformal-prediction'
    }
}
```

### 5. Graph Neural Networks for Spatial Dependencies
```python
graph_neural_networks = {
    'fire_spread_GNN': {
        'paper': 'Zhao et al. 2024',
        'innovation': 'Terrain-vegetation interaction graphs',
        'performance': 'Captures non-local effects'
    },
    
    'infrastructure_risk_GNN': {
        'paper': 'Miller et al. 2023',
        'application': 'WUI fire risk propagation',
        'advantage': 'Models community-level risk'
    }
}
```

## Validation Framework

### Phase 1: Component Validation
```python
def validate_cdw_proxy():
    """Validate CDW proxy against NEON ground data"""
    
    validation_sites = ['NIWO', 'RMNP', 'CPER']
    
    for site in validation_sites:
        # Load paired data
        cdw_ground = load_neon_cdw(site)
        aop_data = load_neon_aop(site)
        
        # Extract features at plot locations
        for plot in cdw_ground.plots:
            aop_window = extract_aop_at_plot(aop_data, plot.coords)
            predicted_cdw = calculate_cdw_proxy(aop_window)
            
            metrics = {
                'mae': abs(predicted_cdw - plot.cdw_mg_ha),
                'mape': abs(predicted_cdw - plot.cdw_mg_ha) / plot.cdw_mg_ha,
                'r2': calculate_r2(predicted_cdw, plot.cdw_mg_ha)
            }
    
    # Acceptance criteria
    assert metrics['r2'] > 0.6, "CDW proxy R² must exceed 0.6"
    assert metrics['mape'] < 0.3, "Mean absolute percentage error < 30%"
```

### Phase 2: Crosswalk Validation
```python
def validate_crosswalks():
    """Validate tier transitions"""
    
    # Ground to AOP validation
    ground_aop_pairs = get_coincident_measurements()
    
    for pair in ground_aop_pairs:
        predicted = ground_to_aop_model.predict(pair.aop)
        actual = pair.ground
        
        validate_predictions(predicted, actual)
    
    # AOP to Satellite validation
    aop_satellite_pairs = get_coincident_imagery()
    
    for pair in aop_satellite_pairs:
        predicted = aop_to_satellite_model.predict(pair.satellite)
        actual = pair.aop
        
        validate_predictions(predicted, actual)
```

### Phase 3: Fire Event Validation
```python
def validate_against_fires():
    """Ultimate validation against actual fires"""
    
    fires = {
        'cameron_peak': {
            'date': '2020-08-13',
            'area': 'NIWO_vicinity',
            'size': 208913,  # acres
            'has_pre_fire_aop': True
        },
        'east_troublesome': {
            'date': '2020-10-14', 
            'area': 'RMNP_vicinity',
            'size': 193812,
            'has_pre_fire_aop': False  # Satellite only
        },
        'calwood': {
            'date': '2020-10-17',
            'area': 'Boulder_County',
            'size': 10106,
            'has_pre_fire_aop': False
        }
    }
    
    for fire_name, fire_info in fires.items():
        # Get pre-fire predictions
        pre_fire_risk = predict_risk(
            location=fire_info['area'],
            date=fire_info['date'] - timedelta(days=7)
        )
        
        # Get actual burned area
        burned_area = get_fire_perimeter(fire_name)
        
        # Calculate metrics
        metrics = {
            'threat_score': calculate_threat_score(pre_fire_risk, burned_area),
            'auc': calculate_auc(pre_fire_risk, burned_area),
            'false_alarm_rate': calculate_far(pre_fire_risk, burned_area)
        }
        
        print(f"{fire_name}: AUC={metrics['auc']:.3f}")
```

### Phase 4: Operational Testing
```python
def operational_validation():
    """Test system performance in operational setting"""
    
    tests = {
        'latency': {
            'requirement': '< 1 second per prediction',
            'method': 'Time 1000 random locations'
        },
        'coverage': {
            'requirement': '100% of Colorado',
            'method': 'Test grid at 1km resolution'
        },
        'temporal_consistency': {
            'requirement': 'Smooth daily transitions',
            'method': 'Check day-to-day variance'
        },
        'uncertainty_calibration': {
            'requirement': '90% CI contains truth 90% of time',
            'method': 'Calibration plots'
        }
    }
    
    return run_tests(tests)
```

## Research Priorities

### Immediate Priorities (Before Implementation)
1. **Validate NDVI thresholds for dead trees**
   - Use NEON VST mortality data
   - Test range: 0.2-0.5
   - Create species-specific thresholds

2. **Calibrate CDW proxy model**
   - Correlate LiDAR metrics with CDW plots
   - Test multiple algorithms (RF, XGBoost, Neural Nets)
   - Establish confidence intervals

3. **Test hyperspectral species classification**
   - Use NEON's species identification data
   - Build spectral library for Colorado species
   - Validate unmixing approaches

### Short-term Research (During Development)
1. **Optimize three-tier cascade**
   - Test different fusion strategies
   - Quantify information loss at each tier
   - Develop uncertainty propagation methods

2. **Incorporate recent techniques**
   - Implement transformer models for hyperspectral
   - Test physics-informed approaches
   - Add self-supervised pretraining

3. **Validate against 2020 fires**
   - Cameron Peak, East Troublesome, Calwood
   - Compare predictions to actual spread
   - Identify failure modes

### Long-term Research (Post-MVP)
1. **Multi-temporal dynamics**
   - Phenology effects on predictions
   - Seasonal model adjustments
   - Long-term fuel accumulation

2. **Climate change impacts**
   - Shifting baselines
   - Novel fire regimes
   - Adaptation strategies

3. **Operational improvements**
   - Real-time data assimilation
   - Ensemble predictions
   - Automated quality control

## Key Papers to Read First

### Essential Reading (Start Here)
1. **Stavros et al. 2023** - Most similar to your approach
2. **Prapas et al. 2023** - State-of-the-art ML for fire
3. **Klauberg et al. 2023** - Hyperspectral-LiDAR fusion
4. **Hillman et al. 2021** - Deep learning on LiDAR

### Colorado-Specific
1. **West et al. 2016** - Beetle-fire interactions
2. **Davis et al. 2022** - Cameron Peak analysis
3. **Sherriff & Veblen 2007** - Fire regimes

### Methods Papers
1. **Hong et al. 2024** - Transformers for hyperspectral
2. **Gawlikowski et al. 2023** - Uncertainty quantification
3. **Bottero et al. 2023** - Physics-informed neural networks

## Implementation Recommendations

### Based on Recent Literature
```python
recommended_approach = {
    'architecture': 'Transformer + ConvLSTM hybrid',
    'pretraining': 'Self-supervised on all NEON imagery',
    'fusion': 'Feature-level, not pixel-level',
    'uncertainty': 'Deep ensemble with 5 models',
    'validation': 'Leave-one-site-out cross-validation',
    'thresholds': 'Learn from data, don't hardcode',
    'physics': 'Include moisture dynamics equations'
}
```

### Critical Success Factors
1. **Don't trust literature thresholds** - Calibrate locally
2. **Use ensemble methods** - Single models will fail
3. **Quantify uncertainty** - Know when you don't know
4. **Validate extensively** - Every assumption needs testing
5. **Stay current** - New papers weekly in this field

## Next Steps

1. **Literature Deep Dive**
   - Read the 10 papers listed above
   - Extract specific thresholds and methods
   - Contact authors for clarification

2. **Data Exploration**
   - Download NEON data for all products mentioned
   - Explore correlations between products
   - Identify data quality issues

3. **Prototype Development**
   - Start with simple models, add complexity
   - Implement validation from day 1
   - Document all assumptions

4. **Community Engagement**
   - Share early results for feedback
   - Collaborate with fire agencies
   - Open source the code