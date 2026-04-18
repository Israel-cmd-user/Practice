import os
from collections import defaultdict

# The directory you want to check for internal duplicates
main_directory = r'E:\Ond Assets\main'

def check_for_duplicates(directory):
    # A dictionary to store: {filename: [list_of_paths_where_it_exists]}
    file_map = defaultdict(list)
    
    print(f"--- Scanning {directory} for duplicate filenames ---")
    
    # 1. Walk the directory and catalog every file
    for root, dirs, files in os.walk(directory):
        for file in files:
            # We use the filename as the key
            full_path = os.path.join(root, file)
            file_map[file].append(full_path)
            
    # 2. Filter and display results
    duplicates_found = False
    for filename, paths in file_map.items():
        if len(paths) > 1:
            duplicates_found = True
            print(f"\n[!] DUPLICATE FOUND: '{filename}'")
            for p in paths:
                print(f"    - {p}")
                
    if not duplicates_found:
        print("\n Success! No duplicate filenames found in the directory.")

if __name__ == "__main__":
    if os.path.exists(main_directory):
        check_for_duplicates(main_directory)
    else:
        print(f"Error: The directory '{main_directory}' does not exist.")