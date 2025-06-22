<<<<<<< HEAD
#!/usr/bin/env python3
"""
Setup script for Flight Portal Desktop Notifier
Helps users configure their monitoring area
"""

import os
import sys

def get_user_input():
    """Get monitoring area from user"""
    print("Flight Portal Desktop Notifier Setup")
    print("=" * 40)
    print()
    print("This will help you configure your monitoring area.")
    print("You'll need the coordinates for the area you want to monitor.")
    print()
    print("Format: top_latitude, bottom_latitude, left_longitude, right_longitude")
    print("Example for London: 51.6,51.4,-0.3,-0.1")
    print()
    
    while True:
        try:
            bounds = input("Enter your bounds box coordinates: ").strip()
            if not bounds:
                print("Using default London area: 51.6,51.4,-0.3,-0.1")
                return "51.6,51.4,-0.3,-0.1"
            
            # Validate format
            parts = bounds.split(',')
            if len(parts) != 4:
                print("❌ Error: Please enter exactly 4 coordinates separated by commas")
                continue
                
            # Try to convert to float to validate
            coords = [float(x.strip()) for x in parts]
            
            # Basic validation
            if coords[0] <= coords[1]:  # top should be > bottom
                print("❌ Error: Top latitude should be greater than bottom latitude")
                continue
                
            print(f"✅ Valid coordinates: {bounds}")
            return bounds
            
        except ValueError:
            print("❌ Error: Please enter valid numbers separated by commas")
        except KeyboardInterrupt:
            print("\nSetup cancelled.")
            sys.exit(0)

def create_secrets_file(bounds_box):
    """Create or update secrets.py file"""
    secrets_content = f'''# This file is where you keep secret settings, passwords, and tokens!
# If you put them in the code you risk committing that info or sharing it

secrets = {{
    'ssid' : 'wifi network',
    'password' : 'wifi password',
    # area to search for flights: top latitude, bottom latitude, left longitude, right longitude
    'bounds_box' : '{bounds_box}'
    }}
'''
    
    try:
        with open('secrets.py', 'w') as f:
            f.write(secrets_content)
        print(f"✅ Created secrets.py with bounds: {bounds_box}")
    except Exception as e:
        print(f"❌ Error creating secrets.py: {e}")

def main():
    """Main setup function"""
    print("Welcome to Flight Portal Desktop Notifier Setup!")
    print()
    
    # Check if secrets.py already exists
    if os.path.exists('secrets.py'):
        print("⚠️  secrets.py already exists.")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled. Using existing secrets.py")
            return
    
    bounds_box = get_user_input()
    create_secrets_file(bounds_box)
    
    print()
    print("Setup complete! You can now run the desktop notifier:")
    print("  python desktop_notifier.py")
    print("  or double-click run_notifier.bat")
    print()
    print("To test notifications, run:")
    print("  python test_notification.py")

if __name__ == "__main__":
=======
#!/usr/bin/env python3
"""
Setup script for Flight Portal Desktop Notifier
Helps users configure their monitoring area
"""

import os
import sys

def get_user_input():
    """Get monitoring area from user"""
    print("Flight Portal Desktop Notifier Setup")
    print("=" * 40)
    print()
    print("This will help you configure your monitoring area.")
    print("You'll need the coordinates for the area you want to monitor.")
    print()
    print("Format: top_latitude, bottom_latitude, left_longitude, right_longitude")
    print("Example for London: 51.6,51.4,-0.3,-0.1")
    print()
    
    while True:
        try:
            bounds = input("Enter your bounds box coordinates: ").strip()
            if not bounds:
                print("Using default London area: 51.6,51.4,-0.3,-0.1")
                return "51.6,51.4,-0.3,-0.1"
            
            # Validate format
            parts = bounds.split(',')
            if len(parts) != 4:
                print("❌ Error: Please enter exactly 4 coordinates separated by commas")
                continue
                
            # Try to convert to float to validate
            coords = [float(x.strip()) for x in parts]
            
            # Basic validation
            if coords[0] <= coords[1]:  # top should be > bottom
                print("❌ Error: Top latitude should be greater than bottom latitude")
                continue
                
            print(f"✅ Valid coordinates: {bounds}")
            return bounds
            
        except ValueError:
            print("❌ Error: Please enter valid numbers separated by commas")
        except KeyboardInterrupt:
            print("\nSetup cancelled.")
            sys.exit(0)

def create_secrets_file(bounds_box):
    """Create or update secrets.py file"""
    secrets_content = f'''# This file is where you keep secret settings, passwords, and tokens!
# If you put them in the code you risk committing that info or sharing it

secrets = {{
    'ssid' : 'wifi network',
    'password' : 'wifi password',
    # area to search for flights: top latitude, bottom latitude, left longitude, right longitude
    'bounds_box' : '{bounds_box}'
    }}
'''
    
    try:
        with open('secrets.py', 'w') as f:
            f.write(secrets_content)
        print(f"✅ Created secrets.py with bounds: {bounds_box}")
    except Exception as e:
        print(f"❌ Error creating secrets.py: {e}")

def main():
    """Main setup function"""
    print("Welcome to Flight Portal Desktop Notifier Setup!")
    print()
    
    # Check if secrets.py already exists
    if os.path.exists('secrets.py'):
        print("⚠️  secrets.py already exists.")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled. Using existing secrets.py")
            return
    
    bounds_box = get_user_input()
    create_secrets_file(bounds_box)
    
    print()
    print("Setup complete! You can now run the desktop notifier:")
    print("  python desktop_notifier.py")
    print("  or double-click run_notifier.bat")
    print()
    print("To test notifications, run:")
    print("  python test_notification.py")

if __name__ == "__main__":
>>>>>>> eb3ab8304665a2eaf899ac0988e15ce17239d09e
    main() 