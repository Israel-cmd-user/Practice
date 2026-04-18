import os
import shutil
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

SOURCE_PATH = os.getenv("SOURCE_PATH")

def organise_preserving_subfolders(base_dir):
    print(f"Starting structure preserving organisation in: {base_dir}")

    status_keywords = ['deleted', 'missed', 'missing', 'sealed', 'concrete_surface']

    print("Scanning for files...")
    all_tasks = []
    for root, _, files in os.walk(base_dir, topdown=False):
        for file in files:
            if not file.startswith('.') and file.lower().endswith(('.png', '.jpg', '.jpeg')):
                all_tasks.append((root, file))

    if not all_tasks:
        print("No files found to organise.")
        return

    for root, file in tqdm(all_tasks, desc="Organising", unit="file"):
        path_parts = root.split(os.sep)
        path_parts_lower = [p.lower() for p in path_parts]
        
        # Find if a status keyword exists in the current path
        status_index = -1
        current_status = None
        for status in status_keywords:
            if status in path_parts_lower:
                status_index = path_parts_lower.index(status)
                current_status = status
                break

        prefix = file.split('_')[0]

        # Calculate Target Path
        if current_status:
            if current_status in ['missed', 'missing']:
                sub_structure = path_parts[status_index:]
                target_path = os.path.join(base_dir, prefix, *sub_structure)
            else:
                status_folder = path_parts[status_index]
                target_path = os.path.join(base_dir, prefix, status_folder)
        else:
            target_path = os.path.join(base_dir, prefix)

        # if current_status:
        #     # Only take the specific keyword found, ignore folders after it
        #     status_folder = path_parts[status_index] 
        #     target_path = os.path.join(base_dir, prefix, status_folder)
        # else:
        #     # Fallback for images not in a status folder
        #     target_path = os.path.join(base_dir, prefix)

        # Execute Move
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        source = os.path.join(root, file)
        destination = os.path.join(target_path, file)

        if source == destination:
            continue

        try:
            shutil.move(source, destination)
        except Exception as e:
            # tqdm.write to avoid breaking the progress bar layout
            tqdm.write(f"Error moving {file}: {e}")

    print("\nCleaning up empty folders...")
    for root, _, files in os.walk(base_dir, topdown=False):
        if root == base_dir: continue
        if not os.listdir(root):
            try:
                os.rmdir(root)
            except OSError: 
                pass

    print("\nOrganisation complete. Subfolders preserved!")

if __name__ == "__main__":
    if os.path.exists(SOURCE_PATH):
        organise_preserving_subfolders(SOURCE_PATH)
    else:
        print(f"Error: Path {SOURCE_PATH} does not exist.")