import os
import shutil
import psycopg2
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()


DB_URL = os.getenv("DB_URL")
SOURCE_ROOT = os.getenvs("SOURCE_PATH")
TARGET_INSPECTION_ROUND = os.get("TARGET_INSPECTION_ROUND")

def organise_by_db_names():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        query = """
        SELECT 
            CONCAT(d.defect_id, '_fn_', d.frame_number) AS file_key,
            COALESCE(c.defect_class_name, CAST(d.defect_class_id AS TEXT)) AS folder_name
        FROM wip_current.road_defects d
        LEFT JOIN wip_current.defect_classes c 
            ON d.defect_class_id = c.defect_class_id
        WHERE d.inspection_round = %s;
        """
        
        print(f"Fetching mapping for Round {TARGET_INSPECTION_ROUND}...")
        cur.execute(query, (TARGET_INSPECTION_ROUND,))
        image_map = {row[0]: row[1] for row in cur.fetchall()}
        
        cur.close()
        conn.close()
        
        if not image_map:
            print("No records found in the database for this round.")
            return

        valid_folder_names = set(image_map.values())

        print("Scanning directory structure...")
        tasks = []
        for root, _, files in os.walk(SOURCE_ROOT):
            if os.path.basename(root) in valid_folder_names:
                continue
            
            for filename in files:
                if filename.lower().endswith(('.jpeg', '.jpg')):
                    tasks.append((root, filename))

        if not tasks:
            print("No images found to process.")
            print(f"{tasks}")
            return

        moved_count = 0

        for root, filename in tqdm(tasks, desc="Sorting Images", unit="img"):
            name_key = os.path.splitext(filename)[0]
            
            if name_key in image_map:
                folder_name = image_map[name_key]
                target_dir = os.path.join(root, folder_name)
                
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                src = os.path.join(root, filename)
                dst = os.path.join(target_dir, filename)
                
                # Double-check we aren't moving a file onto itself
                if src != dst:
                    try:
                        shutil.move(src, dst)
                        moved_count += 1
                    except Exception as e:
                        tqdm.write(f"Error moving {filename}: {e}")

        print(f"\nSuccess! Processed {moved_count} images into descriptive folders.")

    except Exception as e:
        print(f"Database or File Error: {e}")

if __name__ == "__main__":
    organise_by_db_names()