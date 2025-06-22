<<<<<<< HEAD
import os
import zipfile
import shutil

# Get the absolute path of the project's root directory
# This is one level up from the current script's location (tools/organize_logos.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Configuration ---
# Path to your downloaded ZIP file
# Note: This path must be absolute or correct relative to where you run the script.
zip_path = r'C:\Users\colac\Downloads\airline-logos-main.zip'

# Name of the folder inside the ZIP file that contains the logos
source_folder_in_zip = 'airline-logos-main/flightaware_logos/'

# Name of the folder where you want to store the final .ico files
output_logos_folder = os.path.join(BASE_DIR, 'logos')
# --- End Configuration ---

def organize_logos():
    """
    Extracts logo files from a ZIP archive, renames them if necessary,
    and moves them to the project's logos folder.
    """
    if not os.path.exists(zip_path):
        print(f"Error: The file was not found at '{zip_path}'")
        print("Please make sure the path is correct and try again.")
        return

    # Create the output logos directory if it doesn't exist
    os.makedirs(output_logos_folder, exist_ok=True)
    print(f"Created or found the '{output_logos_folder}' directory.")

    extracted_count = 0
    with zipfile.ZipFile(zip_path, 'r') as archive:
        # Get a list of all files in the zip archive
        for file_info in archive.infolist():
            # Check if the file is inside the source folder we want
            if file_info.filename.startswith(source_folder_in_zip) and not file_info.is_dir():
                # Get just the filename (e.g., 'AAL.png')
                original_filename = os.path.basename(file_info.filename)
                
                # The files are already named with the ICAO code, which is what we need.
                # We just need to extract them to our output folder.
                target_path = os.path.join(output_logos_folder, original_filename)
                
                # Extract the file
                with archive.open(file_info) as source_file:
                    with open(target_path, 'wb') as target_file:
                        shutil.copyfileobj(source_file, target_file)
                
                extracted_count += 1

    if extracted_count > 0:
        print(f"Success! Extracted {extracted_count} logos to the '{output_logos_folder}' folder.")
        print("You can now delete the .zip file if you wish.")
    else:
        print(f"Warning: No logos were found in the '{source_folder_in_zip}' folder inside the zip file.")
        print("Please check the folder name inside the ZIP and update the 'source_folder_in_zip' variable.")

if __name__ == "__main__":
=======
import os
import zipfile
import shutil

# Get the absolute path of the project's root directory
# This is one level up from the current script's location (tools/organize_logos.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Configuration ---
# Path to your downloaded ZIP file
# Note: This path must be absolute or correct relative to where you run the script.
zip_path = r'C:\Users\colac\Downloads\airline-logos-main.zip'

# Name of the folder inside the ZIP file that contains the logos
source_folder_in_zip = 'airline-logos-main/flightaware_logos/'

# Name of the folder where you want to store the final .ico files
output_logos_folder = os.path.join(BASE_DIR, 'logos')
# --- End Configuration ---

def organize_logos():
    """
    Extracts logo files from a ZIP archive, renames them if necessary,
    and moves them to the project's logos folder.
    """
    if not os.path.exists(zip_path):
        print(f"Error: The file was not found at '{zip_path}'")
        print("Please make sure the path is correct and try again.")
        return

    # Create the output logos directory if it doesn't exist
    os.makedirs(output_logos_folder, exist_ok=True)
    print(f"Created or found the '{output_logos_folder}' directory.")

    extracted_count = 0
    with zipfile.ZipFile(zip_path, 'r') as archive:
        # Get a list of all files in the zip archive
        for file_info in archive.infolist():
            # Check if the file is inside the source folder we want
            if file_info.filename.startswith(source_folder_in_zip) and not file_info.is_dir():
                # Get just the filename (e.g., 'AAL.png')
                original_filename = os.path.basename(file_info.filename)
                
                # The files are already named with the ICAO code, which is what we need.
                # We just need to extract them to our output folder.
                target_path = os.path.join(output_logos_folder, original_filename)
                
                # Extract the file
                with archive.open(file_info) as source_file:
                    with open(target_path, 'wb') as target_file:
                        shutil.copyfileobj(source_file, target_file)
                
                extracted_count += 1

    if extracted_count > 0:
        print(f"Success! Extracted {extracted_count} logos to the '{output_logos_folder}' folder.")
        print("You can now delete the .zip file if you wish.")
    else:
        print(f"Warning: No logos were found in the '{source_folder_in_zip}' folder inside the zip file.")
        print("Please check the folder name inside the ZIP and update the 'source_folder_in_zip' variable.")

if __name__ == "__main__":
>>>>>>> eb3ab8304665a2eaf899ac0988e15ce17239d09e
    organize_logos() 