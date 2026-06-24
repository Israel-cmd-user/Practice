import os
import shutil
import psycopg2
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")
SOURCE_PATH = os.getenv("SOURCE_PATH")
TARGET_INSPECTION_ROUND = os.getenv("TARGET_INSPECTION_ROUND")
OUTPUT_PATH = os.getenv("OUTPUT_PATH")

def organise_by_db_names():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        # FIXED: Added table alias 'd', corrected CAST syntax, 
        # fixed column alias formatting, and fixed the join condition typo.
        query = """
        SELECT 
            CONCAT(d.defect_id, '_fn_', d.frame_number) AS file_key,
            d.ra_region,
            d.road_no,
            d.video_source,
            COALESCE(c.defect_class_name, CAST(d.defect_class_id AS VARCHAR)) AS folder_name
        FROM wip_current.road_defects d
        LEFT JOIN wip_current.defect_classes c
            ON d.defect_class_id = c.defect_class_id 
        WHERE d.inspection_round = %s;
        """
        
        print(f"Fetching mapping for Round {TARGET_INSPECTION_ROUND}...")
        cur.execute(query, (TARGET_INSPECTION_ROUND,))
        rows = cur.fetchall()
        
        image_map = {}
        for row in rows:
            file_key = row[0]
            region = str(row[1])
            road_ln = str(row[2])
            video_source = str(row[3])
            folder_name = str(row[4])
            
            # Formats as: Region/Road_RN/Video_Source/Defect_Class
            image_map[file_key] = os.path.join(region, road_ln, video_source, folder_name)
        
        cur.close()
        conn.close()
        
        if not image_map:
            print("No records found in the database for this round.")
            return

        print("Scanning directory structure...")
        tasks = []
        abs_output_path = os.path.abspath(OUTPUT_PATH)
        
        for root, _, files in tqdm(os.walk(SOURCE_PATH), desc="Scanning folders", unit="dir"):
            # FIXED: Safe protection against loop processing if OUTPUT_PATH is inside SOURCE_PATH
            if os.path.abspath(root).startswith(abs_output_path):
                continue
            
            for filename in files:
                if filename.lower().endswith(('.jpeg', '.jpg')):
                    tasks.append((root, filename))

        if not tasks:
            print("No images found to process.")
            return

        moved_count = 0

        for root, filename in tqdm(tasks, desc="Sorting Images", unit="img"):
            name_key = os.path.splitext(filename)[0]
            
            if name_key in image_map:
                target_dir = os.path.join(OUTPUT_PATH, image_map[name_key])
                
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                src = os.path.join(root, filename)
                dst = os.path.join(target_dir, filename)
                
                if src != dst:
                    try:
                        shutil.move(src, dst)
                        moved_count += 1
                    except Exception as e:
                        tqdm.write(f"Error moving {filename}: {e}")
        
        print("Cleaning up empty folders...")
        for root, dirs, files in os.walk(SOURCE_PATH, topdown=False):
            if root != SOURCE_PATH and not dirs and not files:
                try:
                    os.rmdir(root)
                except OSError:
                    pass

        print(f"\nProcessed {moved_count} images and cleaned up empty folders.")

    except Exception as e:
        print(f"Database or File Error: {e}")

if __name__ == "__main__":
    organise_by_db_names()