"""
Simple configuration for STAC-based Sentinel-2 NDWI analysis.
No authentication required - uses public STAC API.
"""
from typing import Dict, Tuple
from datetime import datetime, timedelta

# Example locations (modify these for your area of interest)
LOCATIONS = {
    "new_york": {
        "name": "New York City",
        "lon": -73.97,
        "lat": 40.78,
        "description": "Central Park area"
    },
    "san_francisco": {
        "name": "San Francisco Bay",
        "lon": -122.42,
        "lat": 37.77,
        "description": "San Francisco Bay area"
    },
    "london": {
        "name": "London",
        "lon": -0.13,
        "lat": 51.51,
        "description": "Central London"
    },
    "netherlands": {
        "name": "Netherlands",
        "lon": 4.9,
        "lat": 52.4,
        "description": "Central Netherlands"
    },
    "custom": {
        "name": "Custom Location",
        "lon": 0.0,  # Modify these
        "lat": 0.0,  # Modify these
        "description": "Your custom location"
    }
}

# Analysis parameters
ANALYSIS_CONFIG = {
    "buffer_km": 2.0,           # Radius around the point to analyze (km)
    "cloud_cover_max": 20,      # Maximum cloud cover percentage
    "days_back": 30,            # How many days back to search
    "limit": 5                  # Maximum number of images to consider
}

def get_location(location_key: str = "new_york") -> Dict:
    """Get location configuration by key."""
    if location_key not in LOCATIONS:
        raise ValueError(f"Location '{location_key}' not found. Available: {list(LOCATIONS.keys())}")
    
    return LOCATIONS[location_key]

def get_date_range(days_back: int = None) -> Tuple[str, str]:
    """Get date range for analysis."""
    if days_back is None:
        days_back = ANALYSIS_CONFIG["days_back"]
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

def print_available_locations():
    """Print all available locations."""
    print("📍 Available locations:")
    for key, loc in LOCATIONS.items():
        print(f"   {key}: {loc['name']} ({loc['description']})")
        print(f"      Coordinates: {loc['lat']:.4f}°N, {loc['lon']:.4f}°E")

def print_config():
    """Print current configuration."""
    print("⚙️  Current Configuration:")
    for key, value in ANALYSIS_CONFIG.items():
        print(f"   {key}: {value}")
