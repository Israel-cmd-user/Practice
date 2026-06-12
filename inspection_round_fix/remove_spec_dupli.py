import os
import shutil
from tqdm import tqdm

BASE_PATH = r"E:\Organised-files"
# The prefix you want to consolidate (e.g., "GX010617")
TARGET_PREFIX = "GX010617" 
MASTER_OUT = os.path.join(BASE_PATH, f"{TARGET_PREFIX}_CONSOLIDATED")

def consolidate_large_batch():
    if not os.path.exists(MASTER_OUT):
        os.makedirs(MASTER_OUT)

    # Identify all folders starting with your prefix
    all_dirs = [d for d in os.listdir(BASE_PATH) 
                if os.path.isdir(os.path.join(BASE_PATH, d)) 
                and d.startswith(TARGET_PREFIX)
                and d != f"{TARGET_PREFIX}_CONSOLIDATED"]

    print(f"Found {len(all_dirs)} folders to consolidate into {MASTER_OUT}")

    for sub_dir in tqdm(all_dirs, desc="Processing Folders"):
        sub_dir_path = os.path.join(BASE_PATH, sub_dir)
        
        # Walk through every sub-folder (Region/Location) inside GX010617_X
        for root, dirs, files in os.walk(sub_dir_path):
            for filename in files:
                if filename.lower().endswith(('.jpg', '.jpeg')):
                    src = os.path.join(root, filename)
                    
                    # To prevent collisions in the MASTER folder, 
                    # we keep the filename unique by keeping its original name
                    # (which usually contains the frame number).
                    dst = os.path.join(MASTER_OUT, filename)
                    
                    # Handle duplicate filenames just in case
                    if os.path.exists(dst):
                        name, ext = os.path.splitext(filename)
                        dst = os.path.join(MASTER_OUT, f"{name}_{sub_dir}{ext}")

                    try:
                        shutil.move(src, dst)
                    except Exception as e:
                        tqdm.write(f"Error moving {filename}: {e}")

    # Cleanup: Delete the 2,100 empty folders
    print("Cleaning up empty folders...")
    for sub_dir in all_dirs:
        path = os.path.join(BASE_PATH, sub_dir)
        try:
            shutil.rmtree(path) # Use rmtree to remove the folder and any empty sub-dirs
        except:
            pass

if __name__ == "__main__":
    consolidate_large_batch()