#!/usr/bin/env python3
"""
Convert ICO files to PNG for macOS compatibility
"""

import os
from PIL import Image
import sys

def convert_ico_to_png(ico_path, png_path):
    """Convert ICO file to PNG"""
    try:
        with Image.open(ico_path) as img:
            # Convert to RGBA if needed
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            img.save(png_path, 'PNG')
        print(f"✅ Converted {ico_path} to {png_path}")
        return True
    except Exception as e:
        print(f"❌ Error converting {ico_path}: {e}")
        return False

def main():
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    assets_dir = os.path.join(project_root, 'assets')
    
    # Convert the main flight icon
    ico_file = os.path.join(assets_dir, 'flight_icon.ico')
    png_file = os.path.join(assets_dir, 'flight_icon.png')
    
    if os.path.exists(ico_file):
        convert_ico_to_png(ico_file, png_file)
    else:
        print(f"❌ ICO file not found: {ico_file}")
    
    # Convert the fo.ico file as well
    fo_ico_file = os.path.join(assets_dir, 'fo.ico')
    fo_png_file = os.path.join(assets_dir, 'fo.png')
    
    if os.path.exists(fo_ico_file):
        convert_ico_to_png(fo_ico_file, fo_png_file)
    else:
        print(f"❌ ICO file not found: {fo_ico_file}")

if __name__ == "__main__":
    main() 