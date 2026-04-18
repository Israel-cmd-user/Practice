import os
from sqlalchemy import (create_engine, Column, String, update,
                        Boolean, Integer, func, or_, case)
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import insert
from dotenv  import load_dotenv

load_dotenv()

TABLE_NAME = os.getenv("TABLE_NAME")
SCHEMA_NAME = os.getenv("SCHEMA_NAME")
DB_URL = os.getenv("DB_URL")
ROOT_PATH = os.getenv("ROOT_PATH")
INSPECTION_ROUND = os.getenv("INSPECTION_ROUND")

Base = declarative_base()

class ImageRecord(Base):
    __tablename__ = TABLE_NAME
    __table_args__ = {"schema": SCHEMA_NAME}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    defect_id = Column(String(50), unique=True)
    inspection_round = Column(String(20))
    frame_number = Column(Integer, unique=True)
    is_sealed = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

counts = session.query(
    func.count(case((ImageRecord.verified == True, 1))),
    func.count(case((or_(ImageRecord.verified == False, ImageRecord.verified == None), 1)))
).filter(ImageRecord.inspection_round == INSPECTION_ROUND).first()

verified_count = counts[0]
unverified_count = counts[1]

print(f"Pre verified true's: {verified_count}")
print(f"Pre verified false's: {unverified_count}")

session.query(ImageRecord)\
    .filter(ImageRecord.inspection_round == INSPECTION_ROUND)\
    .update({
        ImageRecord.verified: False,
        ImageRecord.is_deleted: False,
        ImageRecord.is_sealed: False
    }, synchronize_session='fetch') 

session.commit()

def get_image_data(base_path):
    # os.walk allows us to see the root, the directories, and the files
    for root, _, files in os.walk(base_path):
        current_folder = os.path.basename(root)
        
        is_sealed = (current_folder.lower() == "sealed")
        is_deleted = (current_folder.lower() == "deleted")
        verified = True 

        for filename in files:
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue
                
            parts = filename.split('_')
            if len(parts) >= 2:
                img_id = f"{parts[0]}_{parts[1]}" 

            clean_name = filename.split('.')[0] 
            parts_fn = clean_name.split('_')

            if len(parts_fn) >= 2:
                img_fn = parts_fn[-1] 
                img_fn_numeric = ''.join(filter(str.isdigit, img_fn))
                
                yield {
                    "id":id,
                    "defect_id": img_id,
                    "frame_number": img_fn_numeric,
                    "is_sealed": is_sealed,
                    "is_deleted": is_deleted,
                    "verified": verified,
                    "inspection_round": INSPECTION_ROUND
                }

def upsert_images(base_path):
    data_generator = get_image_data(base_path)

    batch = []
    for item in data_generator:
        batch.append(item)
        if len(batch) >= 2000:
            execute_upsert(batch)
            batch = []
            
    if batch:  # Clean up remaining items
        execute_upsert(batch)

def execute_upsert(data_list):
    for data in data_list:
        stmt =(
            update(ImageRecord)
            .where(ImageRecord.defect_id == data ['defect_id'])
            .where(ImageRecord.frame_number == data ['frame_number'])
            .where(ImageRecord.inspection_round == INSPECTION_ROUND)
            .values(
                is_sealed = data ['is_sealed'],
                is_deleted = data['is_deleted'],
                verified = data ['verified']
            )
        )
    
    session.execute(stmt, data_list)
    session.commit()
    print(f"Batch processed: {len(data_list)} records updated.")

if __name__ == "__main__":
    upsert_images(ROOT_PATH)
    final_verified = session.query(func.count(ImageRecord.id)).filter(
    ImageRecord.verified == True,
    ImageRecord.inspection_round == INSPECTION_ROUND
    ).scalar()
    print(f"Total verified true values for {INSPECTION_ROUND}: {final_verified}")
