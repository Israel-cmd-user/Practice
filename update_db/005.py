import os
from sqlalchemy import (create_engine, Column, String, update,
                        Boolean, Integer, func, or_, case, tuple_)
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import insert
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

TABLE_NAME = os.getenv("TABLE_NAME")
SCHEMA_NAME = os.getenv("SCHEMA_NAME")
DB_URL = os.getenv("DB_URL")
ROOT_PATH = os.getenv("ROOT_PATH")
TARGET_ROUND = os.getenv("TARGET_ROUND")
# TARGET_ROUND_2 = os.getenv("TARGET_ROUND_2")
# TARGET_ROUND_3 = os.getenv("TARGET_ROUND_3")
# TARGET_ROUND_4 = os.getenv("TARGET_ROUND_4")

INSPECTION_ROUNDS = [TARGET_ROUND]

Base = declarative_base()

class ImageRecord(Base):
    __tablename__ = TABLE_NAME
    __table_args__ = {"schema": SCHEMA_NAME}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    defect_id = Column(String(50), unique=True)
    inspection_round = Column(String(20))
    frame_number = Column(Integer, unique=True)
    is_sealed = Column(Boolean)
    is_deleted = Column(Boolean)
    verified = Column(Boolean)

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

counts = session.query(
    func.count(case((ImageRecord.verified == True, 1))),
    func.count(case((or_(ImageRecord.verified == False, ImageRecord.verified == None), 1)))
).filter(ImageRecord.inspection_round.in_(INSPECTION_ROUNDS)).first()

verified_count = counts[0]
unverified_count = counts[1]

print(f"Pre verified true's: {verified_count}")
print(f"Pre verified false's: {unverified_count}")

# Reset flags before processing
BATCH_SIZE = 10000 

print("Calculating ID boundaries...")
# Fetch the min and max ID for the rows matching your criteria
boundaries = session.query(
    func.min(ImageRecord.id),
    func.max(ImageRecord.id)
).filter(ImageRecord.inspection_round.in_(INSPECTION_ROUNDS),
         or_(
             ImageRecord.verified == None,
             ImageRecord.is_deleted == None,
             ImageRecord.is_sealed == None
         )       
        ).first()

min_id, max_id = boundaries[0], boundaries[1]

if min_id is not None and max_id is not None:
    # Calculate total steps for tqdm progress bar
    total_chunks = ((max_id - min_id) // BATCH_SIZE) + 1
    
    print(f"Resetting records in batches of {BATCH_SIZE}...")
    with tqdm(total=total_chunks, desc="Resetting flags") as pbar:
        current_id = min_id
        while current_id <= max_id:
            next_id = current_id + BATCH_SIZE
            
            # Perform the update strictly within the current ID chunk
            session.query(ImageRecord)\
                .filter(
                    ImageRecord.inspection_round.in_(INSPECTION_ROUNDS),
                    ImageRecord.id >= current_id,
                    ImageRecord.id < next_id,

                    or_(
                        ImageRecord.verified == None,
                        ImageRecord.is_deleted == None,
                        ImageRecord.is_sealed == None
                    )
                )\
                .update(
                    {
                        ImageRecord.verified: func.coalesce(ImageRecord.verified, False),
                        ImageRecord.is_deleted: func.coalesce(ImageRecord.is_deleted, False),
                        ImageRecord.is_sealed: func.coalesce(ImageRecord.is_sealed, False)
                    },
                    synchronize_session=False  # <-- CRITICAL FOR PERFORMANCE
                )
            
            # Commit each batch immediately to free up DB locks and logs
            session.commit()
            
            current_id = next_id
            pbar.update(1)
            
    print("Reset complete successfully!")
else:
    print("All records are already initialised. No reset required.\n")

def build_local_file_map(base_path):
    seen_rounds = set()
    local_data_map = {}
    print(" Scanning local files...")
    
    for root, _, files in os.walk(base_path):
        path_parts = root.split(os.sep)
        current_project = next((p for p in path_parts if p.startswith("GX")), None)
        inspection_round = next((i for i in path_parts if i.startswith("202")), None)

        if not current_project or not inspection_round:
            continue

        if inspection_round not in seen_rounds:
            print(f" Success: Detected Round '{inspection_round}' in Project '{current_project}'")
            # print(f"   Sample Path: {root}")
            seen_rounds.add(inspection_round)

        folder_name = os.path.basename(root).lower()

        if folder_name == "missing" or folder_name == "missed" or folder_name == "concrete_surface":
            print(f" Skipping missing folder in {current_project}")
            continue

        project_key = f"{inspection_round}_{current_project}"

        if project_key not in local_data_map:
            local_data_map[project_key] = {}
        
        # Determine Status based on Folder Name
        is_sealed = (folder_name.lower() == "sealed")
        is_deleted = (folder_name.lower() == "deleted")
        verified = True

        for filename in files:
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue
            
            # Parse ID
            parts = filename.split('_')
            if len(parts) >= 2:
                img_id = f"{parts[0]}_{parts[1]}"
            else:
                continue

            # Parse Frame Number
            clean_name = filename.split('.')[0]
            parts_fn = clean_name.split('_')
            
            if len(parts_fn) >= 2:
                img_fn = parts_fn[-1]
                digit_string = ''.join(filter(str.isdigit, img_fn))
                
                if digit_string:
                    try:
                        frame_int = int(digit_string)
                        
                        # Save to Map (De-duplicates automatically)
                        # Key = (ID, Frame) | Value = Status info
                        local_data_map[project_key][(img_id, frame_int, inspection_round)] = {
                            "is_sealed": is_sealed,
                            "is_deleted": is_deleted,
                            "verified": verified
                        }
                    except ValueError:
                        continue

    total_frames = sum(len(frames) for frames in local_data_map.values())
    print(f" Found {(total_frames)} unique frames locally accross all videos.")
    return local_data_map

def execute_upsert(data_list):
    stmt = insert(ImageRecord).values(data_list)
    
    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=['defect_id', 'frame_number', 'inspection_round'],
        set_={
            "is_sealed": stmt.excluded.is_sealed,
            "is_deleted": stmt.excluded.is_deleted,
            "verified": stmt.excluded.verified
        },
        where=(ImageRecord.inspection_round.in_(INSPECTION_ROUNDS))
    )
    
    session.execute(upsert_stmt)
    
    # Force sync across rounds
    for data in data_list:
        sync_stmt = (
            update(ImageRecord)
            .where(ImageRecord.defect_id == data['defect_id'])
            .where(ImageRecord.inspection_round.in_(INSPECTION_ROUNDS))
            .values({
                "is_sealed": data['is_sealed'],
                "is_deleted": data['is_deleted'],
                "verified": data['verified']
            })
        )
        session.execute(sync_stmt)
        
    session.commit()

def process_updates_in_batches(session, local_data_map, batch_size=1000):
    all_keys = list(local_data_map.keys())
    total_updated = 0
    
    print(f" Processing {len(all_keys)} records against the Database...")

    # Loop through keys in chunks
    for i in range(0, len(all_keys), batch_size):
        batch_keys = all_keys[i : i + batch_size]

        # Query DB for matches
        db_hits = (
            session.query(
                ImageRecord.defect_id, 
                ImageRecord.frame_number, 
                ImageRecord.inspection_round
            )
            .filter(
                tuple_(ImageRecord.defect_id, 
                       ImageRecord.frame_number,
                       ImageRecord.inspection_round).in_(batch_keys)
            )
            # .filter(ImageRecord.inspection_round == "2025-09V4")
            .all()
        )
        
        if not db_hits:
            continue

        # Prepare Update List
        update_payload = []
        for row in db_hits:
            local_status = local_data_map.get((row.defect_id, row.frame_number, row.inspection_round))
            
            if local_status:
                update_payload.append({
                    "defect_id": row.defect_id,
                    "frame_number": row.frame_number,
                    "inspection_round": row.inspection_round,
                    "is_sealed": local_status['is_sealed'],
                    "is_deleted": local_status['is_deleted'],
                    "verified": local_status['verified']
                })

        # Execute Upsert
        if update_payload:
            execute_upsert(update_payload)
            total_updated += len(update_payload)
            print(f"   Updated batch {i // batch_size + 1}: {len(update_payload)} rows.")

    print(f" Done. Total rows updated in DB: {total_updated}")

if __name__ == "__main__":
    master_map = build_local_file_map(ROOT_PATH)
    for project_id, project_local_map in master_map.items():
        print(f"\n--- Starting database update for: {project_id} ---")
        
        # This function handles one videos worth of data at a time
        process_updates_in_batches(session, project_local_map)

    # Final count across all relevant rounds in the DB
    final_verified = session.query(func.count(ImageRecord.id)).filter(
        ImageRecord.verified == True,
        ImageRecord.inspection_round.in_(INSPECTION_ROUNDS)
    ).scalar()
    
    print(f"\n All videos Synced.")
    print(f"Total verified true values in DB for {INSPECTION_ROUNDS}: {final_verified}")