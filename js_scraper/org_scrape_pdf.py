import os
import shutil
import re
from tqdm import tqdm
from dotenv import load_dotenv

def sort_loose_images_from_env():
    # Load environment variables from the local .env file
    load_dotenv()
    
    # Retrieve the configured image directory path
    target_dir = os.getenv("TARGET_IMG_DIR")
    
    if not target_dir:
        print(" Warning: 'TARGET_IMG_DIR' variable not found in environment or .env file.")
        print(" Defaulting execution to the current working directory instead.")
        target_dir = "."
        
    # Resolve to an absolute path signature
    target_dir = os.path.abspath(target_dir)
    
    if not os.path.exists(target_dir):
        print(f" Error: The configured directory '{target_dir}' does not exist.")
        return

    print(f" Target Environment Directory: {target_dir}")
    
    # Regular expression to match your image style: STRUCTUREID_anything.jpg
    # It captures everything up to the first underscore as the structure ID
    pattern = re.compile(r"^([^_]+)_.+\.(jpg|jpeg|png)$", re.IGNORECASE)

    # Filter out everything except valid image files inside the target directory
    try:
        all_files = os.listdir(target_dir)
    except Exception as e:
        print(f" Error accessing directory: {e}")
        return

    # Sift for images, ignoring case versions of jpg/jpeg/png
    valid_extensions = ('.jpg', '.jpeg', '.png')
    image_files = [f for f in all_files if f.lower().endswith(valid_extensions) and os.path.isfile(os.path.join(target_dir, f))]
    
    if not image_files:
        print(" No image files found to sort inside that directory.")
        return

    moved_count = 0
    skipped_count = 0

    print(f"Organizing {len(image_files)} image files...")
    
    # Run loop through target directory with an animated progress bar
    for filename in tqdm(image_files, desc="Sorting Images", unit="file"):
        file_path = os.path.join(target_dir, filename)

        match = pattern.match(filename)
        if match:
            # Extract the structure number (e.g., 'CL4213' from 'CL4213_S01_27_09_2024.jpg')
            struct_no = match.group(1)
            
            # Map structures dynamically inside our environment path
            target_folder = os.path.join(target_dir, struct_no)
            os.makedirs(target_folder, exist_ok=True)
            
            destination_path = os.path.join(target_folder, filename)
            
            try:
                shutil.move(file_path, destination_path)
                moved_count += 1
            except Exception as e:
                tqdm.write(f" Error moving {filename}: {e}")
        else:
            skipped_count += 1

    print(f"\n Sorting Complete!")
    print(f" Successfully grouped: {moved_count} images inside the environment target folder.")
    if skipped_count > 0:
        print(f" Skipped or mismatched files: {skipped_count}")

if __name__ == "__main__":
    sort_loose_images_from_env()