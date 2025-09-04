"""
Simple STAC-based Sentinel-2 downloader for NDWI calculation.
Uses the Earth Search STAC catalog hosted on AWS.
"""
import os
import numpy as np
import rasterio
import rioxarray
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import requests
from pystac_client import Client
from shapely.geometry import Point, box
import matplotlib.pyplot as plt

class STACDownloader:
    """Download Sentinel-2 data using STAC API and calculate NDWI."""
    
    def __init__(self):
        """Initialize the STAC client."""
        # Earth Search STAC endpoint (AWS-hosted Sentinel-2 data)
        self.api_url = "https://earth-search.aws.element84.com/v1"
        self.client = Client.open(self.api_url)
        
    def search_sentinel2(self,
                        lon: float,
                        lat: float,
                        start_date: str,
                        end_date: str,
                        cloud_cover_max: int = 10,
                        limit: int = 5) -> List:
        """Search for Sentinel-2 data at a specific location and time range."""
        
        print(f"🔍 Searching Sentinel-2 data...")
        print(f"   Location: {lat:.4f}°N, {lon:.4f}°E")
        print(f"   Time: {start_date} to {end_date}")
        print(f"   Max cloud cover: {cloud_cover_max}%")
        
        # Create a small bounding box around the point
        buffer = 0.01  # ~1km buffer
        bbox = box(lon - buffer, lat - buffer, lon + buffer, lat + buffer)
        
        # Search for Sentinel-2 L2A data
        search = self.client.search(
            collections=["sentinel-2-l2a"],
            intersects=bbox,
            datetime=f"{start_date}/{end_date}",
            query={"eo:cloud_cover": {"lt": cloud_cover_max}},
            limit=limit
        )
        
        items = list(search.items())
        print(f"✅ Found {len(items)} Sentinel-2 images")
        
        return items
    
    def get_ndwi_bands(self, item) -> Tuple[str, str]:
        """Get the URLs for Green (B03) and NIR (B08) bands needed for NDWI."""
        assets = item.assets
        
        # Get Green band (B03) and NIR band (B08)
        green_url = assets["green"].href  # B03 - Green band
        nir_url = assets["nir"].href      # B08 - NIR band
        
        return green_url, nir_url
    
    def download_band_subset(self,
                           band_url: str,
                           lon: float,
                           lat: float,
                           buffer_km: float = 1.0,
                           output_path: str = None) -> str:
        """Download a subset of a Sentinel-2 band around a specific location."""
        
        # Calculate bounding box in meters (approximate)
        buffer_deg = buffer_km / 111.0  # Rough conversion: 1 degree ≈ 111 km
        
        minx = lon - buffer_deg
        miny = lat - buffer_deg
        maxx = lon + buffer_deg
        maxy = lat + buffer_deg
        
        print(f"📥 Downloading band subset...")
        print(f"   URL: {band_url}")
        print(f"   Bounds: {minx:.4f}, {miny:.4f} to {maxx:.4f}, {maxy:.4f}")
        
        # Open the remote raster file
        raster = rioxarray.open_rasterio(band_url)
        
        # Clip to the area of interest
        subset = raster.rio.clip_box(minx=minx, miny=miny, maxx=maxx, maxy=maxy)
        
        # Generate output filename if not provided
        if output_path is None:
            band_name = Path(band_url).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"data/{band_name}_{timestamp}.tif"
        
        # Create output directory
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save the subset
        subset.rio.to_raster(output_path)
        
        file_size = Path(output_path).stat().st_size / (1024 * 1024)  # MB
        print(f"✅ Saved: {output_path} ({file_size:.1f} MB)")
        
        return output_path
    
    def calculate_ndwi(self,
                      green_file: str,
                      nir_file: str,
                      output_path: str = None) -> str:
        """Calculate NDWI from Green and NIR band files."""
        
        print(f"🧮 Calculating NDWI...")
        print(f"   Green band: {green_file}")
        print(f"   NIR band: {nir_file}")
        
        # Read the bands
        with rasterio.open(green_file) as green_src:
            green_data = green_src.read(1).astype(np.float32)
            profile = green_src.profile
        
        with rasterio.open(nir_file) as nir_src:
            nir_data = nir_src.read(1).astype(np.float32)
        
        # Calculate NDWI = (Green - NIR) / (Green + NIR)
        # Avoid division by zero
        denominator = green_data + nir_data
        ndwi = np.where(denominator != 0, 
                       (green_data - nir_data) / denominator, 
                       0)
        
        # Generate output filename if not provided
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"data/ndwi_{timestamp}.tif"
        
        # Update profile for NDWI output
        profile.update({
            'dtype': rasterio.float32,
            'count': 1,
            'nodata': -9999
        })
        
        # Save NDWI
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(ndwi, 1)
        
        file_size = Path(output_path).stat().st_size / (1024 * 1024)  # MB
        print(f"✅ NDWI saved: {output_path} ({file_size:.1f} MB)")
        
        return output_path
    
    def download_and_calculate_ndwi(self,
                                   lon: float,
                                   lat: float,
                                   start_date: str,
                                   end_date: str,
                                   buffer_km: float = 1.0,
                                   cloud_cover_max: int = 10) -> Dict[str, str]:
        """Complete workflow: search, download, and calculate NDWI."""
        
        print("🛰️  STAC Sentinel-2 NDWI Analysis")
        print("=" * 50)
        
        # Search for data
        items = self.search_sentinel2(lon, lat, start_date, end_date, cloud_cover_max)
        
        if not items:
            raise ValueError("No Sentinel-2 data found for the specified criteria")
        
        # Use the first (most recent) item
        item = items[0]
        print(f"📅 Using image from: {item.properties['datetime']}")
        print(f"☁️  Cloud cover: {item.properties.get('eo:cloud_cover', 'N/A')}%")
        
        # Get band URLs
        green_url, nir_url = self.get_ndwi_bands(item)
        
        # Download band subsets
        green_file = self.download_band_subset(green_url, lon, lat, buffer_km)
        nir_file = self.download_band_subset(nir_url, lon, lat, buffer_km)
        
        # Calculate NDWI
        ndwi_file = self.calculate_ndwi(green_file, nir_file)
        
        # Also download RGB for visualization
        rgb_url = item.assets["visual"].href
        rgb_file = self.download_band_subset(rgb_url, lon, lat, buffer_km, 
                                           f"data/rgb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tif")
        
        return {
            'ndwi': ndwi_file,
            'green': green_file,
            'nir': nir_file,
            'rgb': rgb_file,
            'item': item
        }
    
    def get_recent_dates(self, days_back: int = 30) -> Tuple[str, str]:
        """Get recent date range for data download."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    
    def analyze_ndwi(self, ndwi_file: str) -> Dict:
        """Analyze NDWI data and return statistics."""
        
        with rasterio.open(ndwi_file) as src:
            ndwi_data = src.read(1)
        
        # Remove invalid values
        valid_data = ndwi_data[np.isfinite(ndwi_data)]
        
        if len(valid_data) == 0:
            return {"error": "No valid data found"}
        
        # Calculate water percentage (NDWI > 0)
        water_pixels = np.sum(valid_data > 0)
        total_pixels = len(valid_data)
        water_percentage = (water_pixels / total_pixels) * 100
        
        stats = {
            "count": len(valid_data),
            "mean": float(np.mean(valid_data)),
            "std": float(np.std(valid_data)),
            "min": float(np.min(valid_data)),
            "max": float(np.max(valid_data)),
            "water_percentage": water_percentage,
            "water_pixels": int(water_pixels),
            "total_pixels": int(total_pixels)
        }
        
        return stats
    
    def plot_results(self, 
                    ndwi_file: str,
                    rgb_file: str = None,
                    save_path: str = None) -> plt.Figure:
        """Create a visualization of NDWI results."""
        
        # Read NDWI data
        with rasterio.open(ndwi_file) as src:
            ndwi_data = src.read(1)
            transform = src.transform
            bounds = src.bounds
        
        # Create figure
        fig, axes = plt.subplots(1, 2 if rgb_file else 1, figsize=(15, 6))
        if rgb_file is None:
            axes = [axes]
        
        # Plot NDWI
        im1 = axes[0].imshow(ndwi_data, cmap='RdYlBu_r', vmin=-1, vmax=1)
        axes[0].set_title('NDWI (Normalized Difference Water Index)', fontsize=14)
        axes[0].set_xlabel('Pixel X')
        axes[0].set_ylabel('Pixel Y')
        
        # Add colorbar
        cbar1 = plt.colorbar(im1, ax=axes[0], shrink=0.8)
        cbar1.set_label('NDWI Value', rotation=270, labelpad=20)
        
        # Plot RGB if available
        if rgb_file and len(axes) > 1:
            with rasterio.open(rgb_file) as src:
                rgb_data = src.read([1, 2, 3])  # Read RGB bands
                rgb_data = np.transpose(rgb_data, (1, 2, 0))  # Reorder for matplotlib
            
            axes[1].imshow(rgb_data)
            axes[1].set_title('RGB Visualization', fontsize=14)
            axes[1].set_xlabel('Pixel X')
            axes[1].set_ylabel('Pixel Y')
        
        # Add statistics
        stats = self.analyze_ndwi(ndwi_file)
        stats_text = f"""NDWI Statistics:
Mean: {stats['mean']:.3f}
Std: {stats['std']:.3f}
Min: {stats['min']:.3f}
Max: {stats['max']:.3f}
Water %: {stats['water_percentage']:.1f}%"""
        
        fig.text(0.02, 0.02, stats_text, fontsize=10, 
                verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='wheat'))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 Plot saved to: {save_path}")
        
        return fig

def main():
    """Example usage of the STAC downloader."""
    print("🛰️  STAC Sentinel-2 NDWI Downloader")
    print("=" * 50)
    
    # Initialize downloader
    downloader = STACDownloader()
    
    # Example coordinates (you can modify these)
    # New York City area
    lon, lat = -73.97, 40.78
    
    # Get recent date range
    start_date, end_date = downloader.get_recent_dates(days_back=30)
    
    print(f"📍 Location: {lat:.4f}°N, {lon:.4f}°E")
    print(f"📅 Date Range: {start_date} to {end_date}")
    print()
    
    try:
        # Download and calculate NDWI
        results = downloader.download_and_calculate_ndwi(
            lon=lon,
            lat=lat,
            start_date=start_date,
            end_date=end_date,
            buffer_km=2.0,  # 2km radius around the point
            cloud_cover_max=20
        )
        
        print("\n🎉 Analysis completed successfully!")
        print(f"📁 Files created:")
        for key, filepath in results.items():
            if key != 'item':
                print(f"   {key}: {filepath}")
        
        # Analyze results
        print("\n📊 NDWI Analysis:")
        stats = downloader.analyze_ndwi(results['ndwi'])
        for key, value in stats.items():
            if key != 'count':
                print(f"   {key}: {value}")
        
        # Create visualization
        print("\n📊 Creating visualization...")
        plot_path = f"data/ndwi_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        downloader.plot_results(results['ndwi'], results['rgb'], plot_path)
        
        print(f"\n✅ Complete! Check the 'data' directory for results.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have internet connection and the coordinates are valid.")

if __name__ == "__main__":
    main()
