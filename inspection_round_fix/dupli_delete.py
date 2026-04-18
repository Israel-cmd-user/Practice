import os

# 1. Define your paths
# The folders you want to "walk" to find files to remove
source_folders = [r'C:\Users\is2648257\OneDrive - Surbana Jurong Private Limited\Documents\Verified Images\2025-11V4\GX010609',
                  r'C:\Users\is2648257\OneDrive - Surbana Jurong Private Limited\Documents\Verified Images\2025-11V4\GX010611',
                  r'C:\Users\is2648257\OneDrive - Surbana Jurong Private Limited\Documents\Verified Images\2025-11V4\GX010614']

# The main directory where you want to delete files from
main_directory = r'E:\Ond Assets\main'

def cleanup_main():
    files_to_remove = set()

    # 2. Walk the checked folders to identify files
    for folder in source_folders:
        if os.path.exists(folder):
            for root, dirs, files in os.walk(folder):
                for file in files:
                    # We store just the filename
                    files_to_remove.add(file)
        else:
            print(f"Warning: Folder {folder} not found.")

    if not files_to_remove:
        print("No files found in source folders to delete.")
        return

    # 3. Walk the main directory and delete matches
    for root, dirs, files in os.walk(main_directory):
        for file in files:
            if file in files_to_remove:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except OSError as e:
                    print(f"Error deleting {file_path}: {e}")

if __name__ == "__main__":
    # Safety Check: Always a good idea to back up 'main' before running
    confirm = input("This will delete files in 'main' that match source folders. Proceed? (y/n): ")
    if confirm.lower() == 'y':
        cleanup_main()