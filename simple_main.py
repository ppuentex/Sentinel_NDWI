#!/usr/bin/env python3
"""
Simple main script for STAC-based Sentinel-2 NDWI analysis.
No authentication required - just specify coordinates and run!
"""
import sys
from pathlib import Path
from stac_downloader import STACDownloader
from simple_config import get_location, get_date_range, print_available_locations, print_config

def main():
    """Main function with simple menu."""
    print("🛰️  Simple Sentinel-2 NDWI Analysis")
    print("=" * 50)
    print("No authentication required - uses public STAC API!")
    print()
    
    # Show available locations
    print_available_locations()
    print()
    
    # Get user input
    while True:
        try:
            print("Choose an option:")
            print("1. Use predefined location")
            print("2. Enter custom coordinates")
            print("3. Show configuration")
            print("4. Exit")
            print()
            
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == "1":
                use_predefined_location()
                break
            elif choice == "2":
                use_custom_coordinates()
                break
            elif choice == "3":
                print_config()
                print()
            elif choice == "4":
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                print("❌ Invalid choice. Please enter 1-4.")
                print()
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again.")

def use_predefined_location():
    """Use a predefined location."""
    print("\n📍 Predefined Locations:")
    print_available_locations()
    print()
    
    while True:
        location_key = input("Enter location key (or 'list' to see options): ").strip().lower()
        
        if location_key == 'list':
            print_available_locations()
            print()
            continue
        
        try:
            location = get_location(location_key)
            break
        except ValueError as e:
            print(f"❌ {e}")
            print()
    
    print(f"\n✅ Selected: {location['name']}")
    print(f"   Coordinates: {location['lat']:.4f}°N, {location['lon']:.4f}°E")
    print(f"   Description: {location['description']}")
    
    # Run analysis
    run_analysis(location['lon'], location['lat'], location['name'])

def use_custom_coordinates():
    """Use custom coordinates."""
    print("\n📍 Custom Coordinates:")
    print("Enter latitude and longitude coordinates.")
    print("Example: 40.78, -73.97 (New York City)")
    print()
    
    while True:
        try:
            coords_input = input("Enter coordinates (lat, lon): ").strip()
            lat_str, lon_str = coords_input.split(',')
            
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
            
            # Basic validation
            if not (-90 <= lat <= 90):
                print("❌ Latitude must be between -90 and 90 degrees")
                continue
            if not (-180 <= lon <= 180):
                print("❌ Longitude must be between -180 and 180 degrees")
                continue
            
            break
            
        except ValueError:
            print("❌ Invalid format. Please use: latitude, longitude")
            print("Example: 40.78, -73.97")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    location_name = f"Custom Location ({lat:.4f}°N, {lon:.4f}°E)"
    print(f"\n✅ Coordinates: {lat:.4f}°N, {lon:.4f}°E")
    
    # Run analysis
    run_analysis(lon, lat, location_name)

def run_analysis(lon: float, lat: float, location_name: str):
    """Run the NDWI analysis."""
    print(f"\n🚀 Starting NDWI analysis for {location_name}")
    print("=" * 50)
    
    try:
        # Initialize downloader
        downloader = STACDownloader()
        
        # Get date range
        start_date, end_date = get_date_range()
        
        print(f"📍 Location: {lat:.4f}°N, {lon:.4f}°E")
        print(f"📅 Date Range: {start_date} to {end_date}")
        print(f"🔍 Search radius: 2.0 km")
        print(f"☁️  Max cloud cover: 20%")
        print()
        
        # Download and calculate NDWI
        results = downloader.download_and_calculate_ndwi(
            lon=lon,
            lat=lat,
            start_date=start_date,
            end_date=end_date,
            buffer_km=2.0,
            cloud_cover_max=20
        )
        
        print("\n🎉 Analysis completed successfully!")
        print(f"📁 Files created:")
        for key, filepath in results.items():
            if key != 'item':
                print(f"   {key}: {filepath}")
        
        # Analyze results
        print("\n📊 NDWI Analysis Results:")
        stats = downloader.analyze_ndwi(results['ndwi'])
        print(f"   Mean NDWI: {stats['mean']:.3f}")
        print(f"   Min NDWI: {stats['min']:.3f}")
        print(f"   Max NDWI: {stats['max']:.3f}")
        print(f"   Water percentage: {stats['water_percentage']:.1f}%")
        print(f"   Water pixels: {stats['water_pixels']:,}")
        print(f"   Total pixels: {stats['total_pixels']:,}")
        
        # Create visualization
        print("\n📊 Creating visualization...")
        plot_path = f"data/ndwi_analysis_{location_name.replace(' ', '_')}.png"
        downloader.plot_results(results['ndwi'], results['rgb'], plot_path)
        
        print(f"\n✅ Complete! Check the 'data' directory for results.")
        print(f"📊 Visualization: {plot_path}")
        
        # Show interpretation
        print("\n💡 Interpretation:")
        if stats['water_percentage'] > 50:
            print("   🌊 High water content detected - likely a water body")
        elif stats['water_percentage'] > 20:
            print("   💧 Moderate water content - mixed water/land area")
        elif stats['water_percentage'] > 5:
            print("   🌿 Low water content - mostly land with some water features")
        else:
            print("   🏔️  Very low water content - mostly land/urban area")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("\nTroubleshooting tips:")
        print("- Check your internet connection")
        print("- Verify the coordinates are valid")
        print("- Try a different location or time range")
        print("- The area might not have recent cloud-free imagery")

if __name__ == "__main__":
    main()
