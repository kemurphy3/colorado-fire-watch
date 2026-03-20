# CDW Proxy Methodology: Estimating Coarse Downed Wood from Remote Sensing

## Executive Summary
This document outlines the methodology for estimating Coarse Downed Wood (CDW) fuel loads using NEON AOP data when ground measurements are unavailable. The approach uses forest structure, species composition, and mortality indicators to predict CDW accumulation.

## Table of Contents
1. [Scientific Basis](#scientific-basis)
2. [CDW Accumulation Drivers](#cdw-accumulation-drivers)
3. [Species-Specific Models](#species-specific-models)
4. [AOP Feature Extraction](#aop-feature-extraction)
5. [Proxy Calculation Methods](#proxy-calculation-methods)
6. [Validation Approach](#validation-approach)
7. [Implementation Code](#implementation-code)

## Scientific Basis

### What is CDW?
Coarse Downed Wood consists of dead woody material >7.5cm diameter lying on the forest floor. It represents a significant fuel load for wildfire and affects:
- Fire intensity and duration
- Soil heating and mortality
- Ember production and spotting
- Resistance to control

### Why CDW Matters for Fire
- **Fuel Load**: 10-200 Mg/ha in western forests
- **Burn Duration**: CDW burns for hours vs minutes for fine fuels
- **Heat Release**: Higher energy content than live fuels
- **Moisture Retention**: Affects ignition probability

## CDW Accumulation Drivers

### Primary Factors
```python
cdw_drivers = {
    'mortality_sources': {
        'background': 0.01-0.02,  # Annual mortality rate
        'beetles': 0.10-0.80,      # Outbreak mortality
        'drought': 0.05-0.15,      # Drought-induced
        'windthrow': 0.02-0.10,    # Storm damage
        'fire': 0.20-0.95          # Fire-killed snags fall
    },
    'decomposition_rates': {
        'lodgepole_pine': 0.03-0.05,  # k per year
        'douglas_fir': 0.02-0.04,
        'aspen': 0.06-0.10,
        'spruce_fir': 0.02-0.03
    },
    'environmental_modifiers': {
        'temperature': 'Higher temp = faster decay',
        'moisture': 'Optimal at 40-60% moisture',
        'elevation': 'Slower decay at high elevation'
    }
}
```

### Conceptual Model
```
CDW_load = Σ(Input_rate × (1 - Decomposition_rate)^time)

Where:
- Input_rate = Tree_mortality × Biomass × Fall_rate
- Decomposition_rate = f(species, climate, moisture)
- Time = Years since disturbance
```

## Species-Specific Models

### Lodgepole Pine (Pinus contorta)
```python
class LodgepoleCDW:
    """CDW dynamics in lodgepole pine forests"""
    
    def __init__(self):
        self.base_mortality = 0.015  # Annual
        self.beetle_threshold_dbh = 20  # cm
        self.snag_fall_rate = {
            'year_1-3': 0.05,
            'year_4-10': 0.15,
            'year_11-20': 0.10,
            'year_20+': 0.02
        }
        self.decomposition_k = 0.04
        
    def estimate_cdw(self, stand_age, basal_area, beetle_pressure):
        # Base CDW from normal mortality
        base_cdw = basal_area * self.base_mortality * stand_age * 0.6
        
        # Beetle kill addition
        if beetle_pressure > 0:
            beetle_cdw = basal_area * beetle_pressure * 0.8
            base_cdw += beetle_cdw
            
        # Apply decomposition
        remaining = base_cdw * np.exp(-self.decomposition_k * 10)
        
        return remaining
```

### Douglas Fir (Pseudotsuga menziesii)
```python
class DouglasFirCDW:
    """CDW dynamics in Douglas fir forests"""
    
    def __init__(self):
        self.base_mortality = 0.012
        self.windthrow_susceptible = True
        self.fire_resistant = True  # Thick bark
        self.decomposition_k = 0.03  # Slower decay
        
    def estimate_cdw(self, stand_metrics):
        # Larger trees = more CDW when they fall
        size_factor = stand_metrics['qmd'] / 30  # Quadratic mean diameter
        
        # Old growth accumulates more
        age_factor = min(stand_metrics['age'] / 200, 2.0)
        
        cdw = 45 * size_factor * age_factor  # Base ~45 Mg/ha
        
        # Windthrow adds large pieces
        if stand_metrics['exposed_ridge']:
            cdw *= 1.5
            
        return cdw
```

### Aspen (Populus tremuloides)
```python
class AspenCDW:
    """CDW dynamics in aspen forests"""
    
    def __init__(self):
        self.base_mortality = 0.020
        self.disease_susceptible = True
        self.fast_decomposition = 0.08  # Rapid decay
        self.low_cdw_typical = 15  # Mg/ha
        
    def estimate_cdw(self, health_indicators):
        # Aspen produces less CDW
        base = self.low_cdw_typical
        
        # Disease increases mortality
        if health_indicators['canker_present']:
            base *= 2.0
            
        # But fast decomposition reduces accumulation
        remaining = base * np.exp(-self.fast_decomposition * 5)
        
        return remaining
```

### Spruce-Fir (Picea-Abies)
```python
class SpruceFirCDW:
    """CDW dynamics in spruce-fir forests"""
    
    def __init__(self):
        self.high_elevation = True
        self.slow_decomposition = 0.025  # Cold = slow decay
        self.high_biomass = True
        self.typical_cdw = 75  # Mg/ha - highest loads
        
    def estimate_cdw(self, elevation, stand_density):
        # Elevation slows decomposition
        elev_factor = 1 + (elevation - 2500) / 1000 * 0.2
        
        # Dense stands = more CDW
        density_factor = stand_density / 500  # stems/ha
        
        cdw = self.typical_cdw * elev_factor * density_factor
        
        return cdw
```

## AOP Feature Extraction

### Structural Metrics from LiDAR
```python
def extract_structural_cdw_indicators(chm, las_discrete):
    """Extract CDW-relevant structure from AOP LiDAR"""
    
    metrics = {}
    
    # Forest density (more trees = more potential CDW)
    metrics['stem_density'] = count_trees(chm, min_height=5)
    metrics['basal_area'] = estimate_basal_area(chm)
    
    # Size distribution (large trees = more CDW)
    heights = chm[chm > 5]
    metrics['mean_height'] = np.mean(heights)
    metrics['max_height'] = np.max(heights)
    metrics['height_cv'] = np.std(heights) / np.mean(heights)
    
    # Gaps indicating fallen trees
    metrics['gap_fraction'] = np.sum(chm < 2) / chm.size
    metrics['large_gaps'] = count_gaps(chm, min_size=100)  # m²
    
    # Surface complexity (CDW creates roughness)
    surface = chm[chm < 5]
    metrics['surface_roughness'] = np.std(surface)
    metrics['surface_skewness'] = scipy.stats.skew(surface.flatten())
    
    return metrics
```

### Mortality Indicators from Hyperspectral
```python
def extract_mortality_indicators(hyperspectral):
    """Detect dead and dying trees from spectral signatures"""
    
    indicators = {}
    
    # Standing dead (future CDW)
    ndvi = (hyperspectral[:,:,90] - hyperspectral[:,:,60]) / \
           (hyperspectral[:,:,90] + hyperspectral[:,:,60])
    indicators['snag_fraction'] = np.sum(ndvi < 0.3) / ndvi.size
    
    # Stressed trees (increased mortality)
    red_edge = calculate_red_edge_position(hyperspectral)
    indicators['stressed_fraction'] = np.sum(red_edge < 710) / red_edge.size
    
    # Beetle damage signature
    beetle_index = (hyperspectral[:,:,120] - hyperspectral[:,:,200]) / \
                   (hyperspectral[:,:,120] + hyperspectral[:,:,200])
    indicators['beetle_damage'] = np.mean(beetle_index > 0.3)
    
    # Disease indicators
    pri = photochemical_reflectance_index(hyperspectral)
    indicators['disease_stress'] = np.mean(pri < -0.1)
    
    return indicators
```

### Species Identification
```python
def identify_forest_composition(hyperspectral, chm):
    """Determine species mix from spectral signatures"""
    
    # Spectral unmixing approach
    endmembers = load_species_signatures()
    
    # Reshape for unmixing
    pixels = hyperspectral.reshape(-1, 426)
    
    # Non-negative matrix factorization
    from sklearn.decomposition import NMF
    nmf = NMF(n_components=len(endmembers))
    abundances = nmf.fit_transform(pixels)
    
    # Match components to species
    species_map = match_to_species(nmf.components_, endmembers)
    
    # Calculate composition
    composition = {}
    for species, abundance in zip(species_map, abundances.T):
        composition[species] = np.mean(abundance[chm.flatten() > 5])
    
    return composition
```

## Proxy Calculation Methods

### Method 1: Statistical Model
```python
def calculate_cdw_statistical(aop_features, site_characteristics):
    """Statistical model based on NEON plot correlations"""
    
    # Trained coefficients from plots with CDW measurements
    coefficients = {
        'intercept': 15.3,
        'basal_area': 0.85,
        'snag_fraction': 125.0,
        'surface_roughness': 8.2,
        'gap_fraction': -45.0,
        'elevation': 0.008,
        'slope': -0.3
    }
    
    cdw_proxy = coefficients['intercept']
    
    for feature, value in aop_features.items():
        if feature in coefficients:
            cdw_proxy += coefficients[feature] * value
    
    # Apply bounds
    cdw_proxy = np.clip(cdw_proxy, 5, 200)  # Mg/ha
    
    return cdw_proxy
```

### Method 2: Process-Based Model
```python
def calculate_cdw_process_based(forest_state, time_since_disturbance):
    """Process model of CDW accumulation and decay"""
    
    # Initialize pools
    standing_dead = forest_state['snag_biomass']
    fallen_dead = forest_state['existing_cdw']
    
    # Annual mortality input
    annual_input = forest_state['live_biomass'] * forest_state['mortality_rate']
    
    # Snag fall dynamics
    for year in range(time_since_disturbance):
        # Snags fall over time
        fall_rate = get_snag_fall_rate(year, forest_state['species'])
        new_cdw = standing_dead * fall_rate
        standing_dead *= (1 - fall_rate)
        
        # Add fallen snags to CDW pool
        fallen_dead += new_cdw
        
        # Add background mortality
        fallen_dead += annual_input
        
        # Apply decomposition
        decay_rate = get_decay_rate(forest_state['species'], forest_state['climate'])
        fallen_dead *= (1 - decay_rate)
    
    return fallen_dead
```

### Method 3: Machine Learning Ensemble
```python
def calculate_cdw_ml_ensemble(aop_data, models_dict):
    """Ensemble of ML models trained on CDW plots"""
    
    features = extract_all_features(aop_data)
    
    predictions = []
    weights = []
    
    # Random Forest
    rf_pred = models_dict['random_forest'].predict(features)
    predictions.append(rf_pred)
    weights.append(0.4)
    
    # Gradient Boosting
    gb_pred = models_dict['gradient_boost'].predict(features)
    predictions.append(gb_pred)
    weights.append(0.3)
    
    # Neural Network
    nn_pred = models_dict['neural_net'].predict(features)
    predictions.append(nn_pred)
    weights.append(0.2)
    
    # Ridge Regression (baseline)
    ridge_pred = models_dict['ridge'].predict(features)
    predictions.append(ridge_pred)
    weights.append(0.1)
    
    # Weighted average
    cdw_proxy = np.average(predictions, weights=weights)
    
    # Calculate uncertainty
    uncertainty = np.std(predictions)
    
    return cdw_proxy, uncertainty
```

## Validation Approach

### Cross-Validation with NEON Plots
```python
def validate_cdw_proxy(ground_truth_plots, aop_data):
    """Validate proxy against measured CDW"""
    
    results = {
        'mae': [],
        'rmse': [],
        'r2': [],
        'bias': []
    }
    
    for plot in ground_truth_plots:
        # Extract AOP at plot location
        plot_aop = extract_aop_window(aop_data, plot['coords'], buffer=20)
        
        # Calculate proxy
        proxy = calculate_cdw_proxy(plot_aop)
        
        # Compare to ground truth
        measured = plot['cdw_mg_ha']
        
        results['mae'].append(abs(proxy - measured))
        results['rmse'].append((proxy - measured) ** 2)
        results['bias'].append(proxy - measured)
    
    # Summary statistics
    summary = {
        'mae': np.mean(results['mae']),
        'rmse': np.sqrt(np.mean(results['rmse'])),
        'r2': calculate_r2(proxy_values, measured_values),
        'bias': np.mean(results['bias'])
    }
    
    return summary
```

### Temporal Validation
```python
def validate_temporal_dynamics(multi_year_data):
    """Validate CDW changes over time"""
    
    for year in range(2015, 2024):
        cdw_proxy = calculate_cdw_proxy(aop_data[year])
        
        # Check against expected dynamics
        if year > fire_year:
            # Expect increase from snag fall
            expected_trend = 'increasing'
        else:
            # Normal accumulation/decay balance
            expected_trend = 'stable'
        
        validate_trend(cdw_proxy, expected_trend)
```

## Implementation Code

### Complete CDW Proxy Pipeline
```python
class CDWProxySystem:
    """Complete system for CDW estimation from AOP"""
    
    def __init__(self):
        self.models = self.load_trained_models()
        self.species_library = self.load_species_signatures()
        
    def estimate_cdw(self, aop_data, method='ensemble'):
        """Main entry point for CDW estimation"""
        
        # Extract features
        structure = self.extract_structure(aop_data['chm'])
        mortality = self.extract_mortality(aop_data['hyperspectral'])
        species = self.identify_species(aop_data['hyperspectral'])
        
        # Combine features
        features = {**structure, **mortality, **species}
        
        # Apply selected method
        if method == 'statistical':
            cdw = self.statistical_model(features)
        elif method == 'process':
            cdw = self.process_model(features)
        elif method == 'ensemble':
            cdw = self.ensemble_model(features)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Add metadata
        result = {
            'cdw_mg_ha': cdw,
            'method': method,
            'confidence': self.calculate_confidence(features),
            'dominant_species': max(species, key=species.get),
            'mortality_level': mortality['snag_fraction']
        }
        
        return result
    
    def extract_structure(self, chm):
        """Extract structural metrics"""
        metrics = {}
        
        # Basic statistics
        trees = chm[chm > 5]
        metrics['mean_height'] = np.mean(trees)
        metrics['max_height'] = np.max(trees)
        metrics['stem_density'] = self.count_trees(chm)
        metrics['basal_area'] = self.estimate_basal_area(chm)
        
        # Complexity metrics
        metrics['gap_fraction'] = np.sum(chm < 2) / chm.size
        metrics['height_diversity'] = self.shannon_index(trees)
        
        # Surface characteristics
        surface = chm[chm < 5]
        metrics['surface_roughness'] = np.std(surface)
        
        return metrics
    
    def extract_mortality(self, hyperspectral):
        """Extract mortality indicators"""
        indicators = {}
        
        # NDVI for dead trees
        ndvi = self.calculate_ndvi(hyperspectral)
        indicators['snag_fraction'] = np.sum(ndvi < 0.3) / ndvi.size
        
        # Stress indicators
        indicators['red_edge_shift'] = self.red_edge_position(hyperspectral)
        indicators['water_stress'] = self.water_band_index(hyperspectral)
        
        # Disturbance signatures
        indicators['beetle_index'] = self.beetle_damage_index(hyperspectral)
        
        return indicators
    
    def identify_species(self, hyperspectral):
        """Identify species composition"""
        
        # Spectral unmixing
        abundances = self.spectral_unmixing(hyperspectral, self.species_library)
        
        # Convert to percentages
        total = np.sum(abundances)
        composition = {
            species: abundance / total 
            for species, abundance in abundances.items()
        }
        
        return composition
    
    def statistical_model(self, features):
        """Apply statistical model"""
        # Trained regression coefficients
        model = self.models['statistical']
        cdw = model.predict(features)
        return cdw
    
    def process_model(self, features):
        """Apply process-based model"""
        # Initialize state from features
        state = self.features_to_state(features)
        
        # Run accumulation/decomposition model
        cdw = self.run_process_model(state)
        
        return cdw
    
    def ensemble_model(self, features):
        """Apply ensemble of models"""
        predictions = []
        
        for name, model in self.models.items():
            pred = model.predict(features)
            predictions.append(pred)
        
        # Weighted average
        cdw = np.average(predictions, weights=self.model_weights)
        
        return cdw
    
    def calculate_confidence(self, features):
        """Estimate prediction confidence"""
        
        # High confidence if:
        # - Clear species identification
        # - Typical forest structure
        # - Low cloud cover in imagery
        
        confidence = 1.0
        
        # Reduce for unusual conditions
        if features['mean_height'] > 40 or features['mean_height'] < 5:
            confidence *= 0.8
            
        if features['snag_fraction'] > 0.5:
            confidence *= 0.7  # Extreme mortality harder to predict
            
        return confidence

# Usage example
if __name__ == "__main__":
    # Initialize system
    cdw_system = CDWProxySystem()
    
    # Load AOP data
    aop_data = {
        'chm': load_chm('NIWO_2019.tif'),
        'hyperspectral': load_hyperspectral('NIWO_2019.h5')
    }
    
    # Estimate CDW
    result = cdw_system.estimate_cdw(aop_data, method='ensemble')
    
    print(f"CDW Estimate: {result['cdw_mg_ha']:.1f} Mg/ha")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Dominant Species: {result['dominant_species']}")
    print(f"Mortality Level: {result['mortality_level']:.1%}")
```

## Key Assumptions and Limitations

### Assumptions
1. Species signatures are consistent across sites
2. Mortality indicators are detectable spectrally
3. Decomposition rates follow known patterns
4. Topography affects accumulation predictably

### Limitations
1. Cannot detect buried CDW under canopy
2. Difficulty distinguishing CDW from live understory
3. Species mixing complicates signatures
4. Temporal lag between mortality and CDW accumulation

### Uncertainty Sources
1. Species misidentification: ±20% CDW estimate
2. Mortality timing unknown: ±5 years accumulation
3. Decomposition variability: ±30% remaining mass
4. Spatial heterogeneity: ±15 Mg/ha local variation

## Next Steps

1. **Validate with NEON CDW plots**: Compare proxy to measurements
2. **Test across sites**: NIWO, RMNP, CPER differences
3. **Incorporate disturbance history**: Fire, beetle, wind records
4. **Add temporal dynamics**: Multi-year CDW trajectories
5. **Integrate with fire models**: CDW as fuel load input