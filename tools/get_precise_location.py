#!/usr/bin/env python3
"""
Get precise GPS location and create monitoring area
"""

import webbrowser
import os
import sys

def get_location_from_browser():
    """Open browser to get precise GPS location"""
    print("🌍 Getting your precise GPS location...")
    print()
    print("This will open your browser to get your exact GPS coordinates.")
    print("Please allow location access when prompted.")
    print()
    
    # Open a location service in browser
    location_url = "https://www.latlong.net/"
    print(f"Opening {location_url} in your browser...")
    
    try:
        webbrowser.open(location_url)
        print("✅ Browser opened successfully!")
        print()
        print("📋 Instructions:")
        print("1. Allow location access when prompted")
        print("2. Copy the latitude and longitude values")
        print("3. Return here and enter them")
        print()
    except Exception as e:
        print(f"❌ Could not open browser: {e}")
        print("Please manually visit: https://www.latlong.net/")
        print()

def get_manual_coordinates():
    """Get coordinates from user input"""
    print("Please enter your precise GPS coordinates:")
    print("You can get these from:")
    print("- Your phone's GPS")
    print("- Google Maps (right-click on your location)")
    print("- https://www.latlong.net/")
    print()
    
    while True:
        try:
            lat_input = input("Enter Latitude (e.g., 13.7146): ").strip()
            lon_input = input("Enter Longitude (e.g., 100.7478): ").strip()
            
            lat = float(lat_input)
            lon = float(lon_input)
            
            # Basic validation
            if not (-90 <= lat <= 90):
                print("❌ Latitude must be between -90 and 90 degrees")
                continue
            if not (-180 <= lon <= 180):
                print("❌ Longitude must be between -180 and 180 degrees")
                continue
            
            print(f"✅ Coordinates accepted: {lat}, {lon}")
            return lat, lon
            
        except ValueError:
            print("❌ Please enter valid numbers")
        except KeyboardInterrupt:
            print("\nSetup cancelled.")
            sys.exit(0)

def create_precise_bounds(lat, lon, radius_km=2):
    """Create a very small monitoring area around the given coordinates"""
    # Convert km to degrees (approximate)
    # 1 degree latitude ≈ 111 km
    # 1 degree longitude ≈ 111 km * cos(latitude)
    
    lat_offset = radius_km / 111.0
    lon_offset = radius_km / (111.0 * abs(lat / 90.0))  # Adjust for latitude
    
    top_lat = lat + lat_offset
    bottom_lat = lat - lat_offset
    left_lon = lon - lon_offset
    right_lon = lon + lon_offset
    
    bounds = f"{top_lat:.6f},{bottom_lat:.6f},{left_lon:.6f},{right_lon:.6f}"
    
    print(f"🎯 Created precise monitoring area:")
    print(f"   Center: {lat:.6f}°, {lon:.6f}°")
    print(f"   Top: {top_lat:.6f}°")
    print(f"   Bottom: {bottom_lat:.6f}°")
    print(f"   Left: {left_lon:.6f}°")
    print(f"   Right: {right_lon:.6f}°")
    print(f"   Radius: ~{radius_km} km")
    
    return bounds

def get_script_directory():
    """Gets the directory of the currently running script"""
    return os.path.dirname(os.path.abspath(__file__))

def update_secrets_file(bounds_box, lat, lon):
    """Update config.py with precise location"""
    secrets_content = f'''# This file is where you keep secret settings, passwords, and tokens!
# If you put them in the code you risk committing that info or sharing it

secrets = {{
    'ssid' : 'wifi network',
    'password' : 'wifi password',
    # area to search for flights: top latitude, bottom latitude, left longitude, right longitude
    # Precise location: {lat:.6f}, {lon:.6f}
    'bounds_box' : '{bounds_box}'
    }}
'''
    
    # Get the project root directory (one level up from the script's 'tools' folder)
    project_root = os.path.dirname(get_script_directory())
    config_path = os.path.join(project_root, 'config.py')

    try:
        with open(config_path, 'w') as f:
            f.write(secrets_content)
        print(f"✅ Updated {config_path} with precise location")
        return True
    except Exception as e:
        print(f"❌ Error updating {config_path}: {e}")
        return False

def main():
    """Main function to get precise GPS location and update configuration"""
    print("Flight Portal - Precise GPS Location Setup")
    print("=" * 45)
    print()
    
    # Offer to open browser for location
    print("How would you like to get your precise location?")
    print("1. Open browser to get GPS coordinates automatically")
    print("2. Enter coordinates manually")
    print()
    
    while True:
        try:
            choice = input("Enter choice (1-2): ").strip()
            if choice == '1':
                get_location_from_browser()
                break
            elif choice == '2':
                break
            else:
                print("Please enter 1 or 2")
        except KeyboardInterrupt:
            print("\nSetup cancelled.")
            return
    
    # Get coordinates
    lat, lon = get_manual_coordinates()
    
    # Ask user for radius
    print()
    print("How precise do you want the monitoring area?")
    print("1. Very precise (1 km radius) - Only flights directly overhead")
    print("2. Precise (2 km radius) - Recommended for most users")
    print("3. Local (5 km radius) - More flights, less precise")
    
    while True:
        try:
            choice = input("Enter choice (1-3): ").strip()
            if choice == '1':
                radius = 1
                break
            elif choice == '2':
                radius = 2
                break
            elif choice == '3':
                radius = 5
                break
            else:
                print("Please enter 1, 2, or 3")
        except KeyboardInterrupt:
            print("\nSetup cancelled.")
            return
    
    # Create bounds
    bounds_box = create_precise_bounds(lat, lon, radius)
    
    # Update secrets file
    if update_secrets_file(bounds_box, lat, lon):
        print()
        print("🎉 Precise location setup complete!")
        print(f"Monitoring area: {radius}km radius around your exact location")
        print(f"Coordinates: {lat:.6f}, {lon:.6f}")
        print()
        print("You can now run the desktop notifier:")
        print("  python desktop_notifier.py")
        print()
        print("To test notifications:")
        print("  python test_notification.py")

if __name__ == "__main__":
    main() 