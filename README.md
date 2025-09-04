# Simple Sentinel-2 NDWI Analysis

Download and analyze Sentinel-2 satellite data to calculate the Normalized Difference Water Index (NDWI) using Python and the STAC API. **No authentication required!**

## 🌟 What Makes This Special

- ✅ **No accounts or credentials needed** - uses public STAC API
- ✅ **Simple setup** - just coordinates and run
- ✅ **Fast downloads** - only downloads what you need
- ✅ **Interactive notebooks** - step-by-step analysis
- ✅ **Multiple locations** - predefined locations or custom coordinates

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/Sentinel_NDWI.git
cd Sentinel_NDWI

# Install UV package manager (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Set up environment
uv venv --python python3
source .venv/bin/activate
uv sync
```

### 2. Run Analysis

#### Option A: Interactive Script (Easiest)
```bash
python simple_main.py
```

#### Option B: Jupyter Notebook (Most Interactive)
```bash
jupyter lab
# Open notebooks/Simple_NDWI_Analysis.ipynb
```

#### Option C: Direct Python
```python
from stac_downloader import STACDownloader

downloader = STACDownloader()
results = downloader.download_and_calculate_ndwi(
    lon=-73.97,  # Longitude
    lat=40.78,   # Latitude
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

## 📍 Available Locations

The project includes predefined locations you can analyze:

- **New York City**: Central Park area
- **San Francisco Bay**: San Francisco Bay area  
- **London**: Central London
- **Netherlands**: Central Netherlands
- **Custom**: Enter your own coordinates

## 🧮 What is NDWI?

**NDWI (Normalized Difference Water Index)** detects water bodies using satellite imagery:

```
NDWI = (Green - NIR) / (Green + NIR)
```

- **Green** = Green band (Band 3 in Sentinel-2)
- **NIR** = Near-Infrared band (Band 8 in Sentinel-2)

**NDWI Values:**
- **Positive values** (0 to 1): Water bodies
- **Negative values** (-1 to 0): Land, vegetation, urban areas

## 📊 What You Get

### Files Created
- `ndwi_*.tif` - NDWI calculated data
- `rgb_*.tif` - RGB visualization data  
- `green_*.tif` - Green band data
- `nir_*.tif` - NIR band data
- `water_classification.tif` - Binary water classification

### Analysis Results
- Water percentage in your area
- NDWI statistics (mean, min, max, std)
- Visual comparisons (NDWI vs RGB)
- Water classification maps

## 🛠️ Project Structure

```
Sentinel_NDWI/
├── notebooks/
│   └── Simple_NDWI_Analysis.ipynb  # Interactive analysis
├── stac_downloader.py              # Main downloader class
├── simple_config.py                # Configuration and locations
├── simple_main.py                  # Interactive command-line tool
├── pyproject.toml                  # UV project configuration
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🔧 Dependencies

- **numpy** - Numerical computations
- **rasterio** - Geospatial raster I/O
- **rioxarray** - Advanced raster operations
- **pystac-client** - STAC API access
- **shapely** - Geometric operations
- **matplotlib** - Plotting and visualization
- **jupyter** - Interactive notebooks

## 📖 Usage Examples

### Example 1: Analyze New York City
```python
from stac_downloader import STACDownloader

downloader = STACDownloader()
results = downloader.download_and_calculate_ndwi(
    lon=-73.97, lat=40.78,  # NYC coordinates
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

### Example 2: Custom Location
```python
# Analyze a lake in your area
results = downloader.download_and_calculate_ndwi(
    lon=-122.42, lat=37.77,  # San Francisco Bay
    start_date="2024-01-01",
    end_date="2024-01-31",
    buffer_km=5.0  # 5km radius
)
```

### Example 3: Analyze Results
```python
# Get statistics
stats = downloader.analyze_ndwi(results['ndwi'])
print(f"Water percentage: {stats['water_percentage']:.1f}%")

# Create visualization
fig = downloader.plot_results(results['ndwi'], results['rgb'])
```

## 🎯 Use Cases

- **Water body detection** - Find lakes, rivers, ponds
- **Flood monitoring** - Track water extent changes
- **Wetland mapping** - Identify wetland areas
- **Urban water features** - Analyze water in cities
- **Environmental monitoring** - Track water resources

## 🔍 How It Works

1. **Search**: Uses STAC API to find Sentinel-2 data
2. **Download**: Downloads only the bands needed (Green, NIR)
3. **Calculate**: Computes NDWI using the formula
4. **Analyze**: Provides statistics and visualizations
5. **Save**: Exports results as GeoTIFF files

## 🚨 Troubleshooting

### "No data found"
- Try a larger time range (more days)
- Check if your area has recent cloud-free imagery
- Try a different location

### "Download failed"
- Check your internet connection
- Try a smaller area or different time period
- The area might not have recent imagery

### "Import errors"
- Make sure you activated the virtual environment: `source .venv/bin/activate`
- Reinstall dependencies: `uv sync`

## 📚 Learn More

- [STAC Specification](https://stacspec.org/)
- [Sentinel-2 Mission](https://sentinel.esa.int/web/sentinel/missions/sentinel-2)
- [NDWI Research Paper](https://www.researchgate.net/publication/228344275_A_Modified_Normalized_Difference_Water_Index_MNDWI)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [STAC Community](https://stacspec.org/) for the open standard
- [AWS Open Data](https://registry.opendata.aws/sentinel-2-l2a-cogs/) for hosting Sentinel-2 data
- [UV](https://github.com/astral-sh/uv) for fast Python package management
- [Carpentries](https://carpentries-incubator.github.io/geospatial-python/) for the STAC tutorial inspiration

---

**Ready to analyze water from space? Start with `python simple_main.py`!** 🛰️💧