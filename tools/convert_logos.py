from PIL import Image
import os

# Get the absolute path of the project's root directory
# This is one level up from the current script's location (tools/convert_logos.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Configuration ---
# Folder where your .png logos are located
logos_folder = os.path.join(BASE_DIR, 'logos')
# --- End Configuration ---

def convert_png_to_ico():
    """
    Finds all .png files in the specified folder and converts them to .ico format.
    """
    if not os.path.isdir(logos_folder):
        print(f"Error: The folder '{logos_folder}' was not found.")
        print("Please make sure you have run the 'organize_logos.py' script first.")
        return

    print(f"Scanning for PNG files in '{logos_folder}'...")
    converted_count = 0
    failed_count = 0

    for filename in os.listdir(logos_folder):
        if filename.lower().endswith(".png"):
            png_path = os.path.join(logos_folder, filename)
            ico_filename = os.path.splitext(filename)[0] + ".ico"
            ico_path = os.path.join(logos_folder, ico_filename)

            try:
                # Open the PNG image
                img = Image.open(png_path)

                # Save as ICO with multiple sizes for compatibility
                img.save(ico_path, format='ICO', sizes=[(16,16), (32, 32), (48, 48), (64, 64)])
                
                print(f"  - Converted '{filename}' to '{ico_filename}'")
                converted_count += 1
            except Exception as e:
                print(f"  - FAILED to convert '{filename}'. Reason: {e}")
                failed_count += 1
    
    print("\n--- Conversion Complete ---")
    print(f"Successfully converted: {converted_count} files")
    if failed_count > 0:
        print(f"Failed to convert: {failed_count} files")
    print("--------------------------")

if __name__ == "__main__":
    convert_png_to_ico() 

def convert_png_to_ico():
    """
    Finds all .png files in the specified folder and converts them to .ico format.
    """
    if not os.path.isdir(logos_folder):
        print(f"Error: The folder '{logos_folder}' was not found.")
        print("Please make sure you have run the 'organize_logos.py' script first.")
        return

    print(f"Scanning for PNG files in '{logos_folder}'...")
    converted_count = 0
    failed_count = 0

    for filename in os.listdir(logos_folder):
        if filename.lower().endswith(".png"):
            png_path = os.path.join(logos_folder, filename)
            ico_filename = os.path.splitext(filename)[0] + ".ico"
            ico_path = os.path.join(logos_folder, ico_filename)

            try:
                # Open the PNG image
                img = Image.open(png_path)

                # Save as ICO with multiple sizes for compatibility
                img.save(ico_path, format='ICO', sizes=[(16,16), (32, 32), (48, 48), (64, 64)])
                
                print(f"  - Converted '{filename}' to '{ico_filename}'")
                converted_count += 1
            except Exception as e:
                print(f"  - FAILED to convert '{filename}'. Reason: {e}")
                failed_count += 1
    
    print("\n--- Conversion Complete ---")
    print(f"Successfully converted: {converted_count} files")
    if failed_count > 0:
        print(f"Failed to convert: {failed_count} files")
    print("--------------------------")

if __name__ == "__main__":
    convert_png_to_ico() 