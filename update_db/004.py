import os
from sqlalchemy import (create_engine, Column, String, update,
                        Boolean, Integer, func, or_, case, tuple_)
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import insert
from dotenv import load_dotenv

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
session.query(ImageRecord)\
    .filter(ImageRecord.inspection_round.in_(INSPECTION_ROUNDS))\
    .update({
        ImageRecord.verified: False,
        ImageRecord.is_deleted: False,
        ImageRecord.is_sealed: False
    })
session.commit()

def build_local_file_map(base_path):
    local_data_map = {}
    print(" Scanning local files...")
    
    for root, _, files in os.walk(base_path):
        current_folder = os.path.basename(root)
        
        # Determine Status based on Folder Name
        is_sealed = (current_folder.lower() == "sealed")
        is_deleted = (current_folder.lower() == "deleted")
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
                        local_data_map[(img_id, frame_int)] = {
                            "is_sealed": is_sealed,
                            "is_deleted": is_deleted,
                            "verified": verified
                        }
                    except ValueError:
                        continue

    print(f" Found {len(local_data_map)} unique frames locally.")
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
                tuple_(ImageRecord.defect_id, ImageRecord.frame_number).in_(batch_keys)
            )
            # .filter(ImageRecord.inspection_round == "2025-09V4")
            .all()
        )
        
        if not db_hits:
            continue

        # Prepare Update List
        update_payload = []
        for row in db_hits:
            local_status = local_data_map.get((row.defect_id, row.frame_number))
            
            if local_status:
                update_payload.append({
                    "defect_id": row.defect_id,
                    "frame_number": row.frame_number,
                    "inspection_round": row.inspection_round, # Use DB Round
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
    local_map = build_local_file_map(ROOT_PATH)
    process_updates_in_batches(session, local_map)
    final_verified = session.query(func.count(ImageRecord.id)).filter(
        ImageRecord.verified == True,
        ImageRecord.inspection_round.in_(INSPECTION_ROUNDS)
    ).scalar()
    print(f"Total verified true values for {INSPECTION_ROUNDS}: {final_verified}")