import os
from sqlalchemy import create_engine, Column, String, Boolean, Integer
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import insert
from dotenv import load_dotenv

load_dotenv()

TABLE_NAME = os.getenv("TABLE_NAME")
SCHEMA_NAME = os.getenv("SCHEMA_NAME")
DB_URL = os.getenv("DB_URL")
ROOT_PATH = os.getenv("ROOT_PATH")
INSPECTION_ROUND = os.getenv("INSPECTION_ROUND")

Base = declarative_base()

class ImageRecord(Base):
    __tablename__ = "road_defects_test"
    __table_args__ = {"schema": os.getenv("SCHEMA_NAME")}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_sealed = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    frame_number = Column(Integer, default = False)
    defect_id = Column(String(50), unique = True)

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

def parse_id(filename):
    clean_name = os.path.splitext(filename)[0]
    parts = clean_name.split('_')
    return f"{parts[0]}_{parts[1]}" if len(parts) >= 2 else None

def parse_fn(filename):
    new_name = os.path.splitext(filename)[0]
    parts_fn = new_name.split('_')
    if len(parts_fn) >= 2:
        raw_val = parts_fn[-1] 
        numeric_val = ''.join(filter(str.isdigit, raw_val))
        return int(numeric_val) if numeric_val else 0
    return 0

def bulk_insert_images(source_folder):
    if not os.path.exists(source_folder):
        print(f"Error: Folder {source_folder} not found.")
        return

    all_files = os.listdir(source_folder)
    print(f"Found {len(all_files)} files. Starting insertion...")

    batch = []
    count = 0

    for filename in all_files:
        img_id = parse_id(filename)
        img_fn = parse_fn(filename)
        
        if img_id:
            batch.append({
                "defect_id": img_id,
                "frame_number": img_fn  
            })
            
        if len(batch) >= 5000:
            execute_upsert(batch)
            count += len(batch)
            print(f"Processed {count} records...")
            batch = []

    if batch:
        execute_upsert(batch)
        count += len(batch)
    
    print(f"Finished! Total IDs synced: {count}")

def execute_upsert(data_list):
    stmt = insert(ImageRecord).values(data_list)
    
    # ON CONFLICT DO NOTHING ensures we don't overwrite 
    # existing 'sealed' or 'deleted' statuses during this initial load.
    upsert_stmt = stmt.on_conflict_do_nothing(index_elements=['defect_id', 'frame_number'])
    
    session.execute(upsert_stmt)
    session.commit()

if __name__ == "__main__":
    IMAGE_DIR = r"C:\Users\is2648257\Documents\Ond-assets\2025-09-verified\Deleted" 
    bulk_insert_images(IMAGE_DIR)