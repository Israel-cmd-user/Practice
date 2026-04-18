import os
import sqlalchemy as db
from sqlalchemy import (Boolean, create_engine, Column, String,Integer,Float, ForeignKey, 
                        func, desc, select)
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

TABLE_NAME = os.getenv("TABLE_NAME")
TABLE_TWO = os.getenv("TABLE_TWO")
SCHEMA_NAME = os.getenv("SCHEMA_NAME")
DB_URL = os.getenv("DB_URL")
ROOT_PATH =os.getenv("ROOT_PATH")

Base = declarative_base()

class RetrieveImageData(Base):
    __tablename__ = TABLE_NAME
    __table_args__ = {"schema": SCHEMA_NAME}

    id = Column(Integer, primary_key = True, autoincrement= True)
    defect_id = Column(String (20))
    road_no = Column(Integer)
    degree_classification = Column (String(20))
    frame_number = Column(Integer)
    confidence_detect = Column (Float)
    inspection_round = Column (String(20))
    verified = Column (Boolean)
    defect_class_id = Column(Integer, ForeignKey(f"{TABLE_TWO}.defect_class_id"))
    is_deleted = Column(Boolean)

class ImageClassification(Base):
    __tablename__ = TABLE_TWO
    __table_args__ = {"schema": SCHEMA_NAME}

    defect_class_id = Column(Integer, primary_key= True )
    defect_class_name = Column(String(30), unique=True)

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
Session = Session()

subq = (
    select(
        RetrieveImageData,
        func.row_number().over(
            partition_by=RetrieveImageData.defect_id,
            order_by=desc(RetrieveImageData.confidence_detect)
        ).label("rn")
    )
    .filter(RetrieveImageData.inspection_round.in_(['2025-08V4','2025-09V4']))
    .filter(RetrieveImageData.is_deleted != True)
    .filter(RetrieveImageData.verified == True)
    .subquery()
)

query = (
    select(
        subq.c.defect_id,
        subq.c.road_no,
        subq.c.frame_number,
        subq.c.degree_classification,
        subq.c.confidence_detect,
        ImageClassification.defect_class_name  
    )
    .join(
        ImageClassification, 
        subq.c.defect_class_id == ImageClassification.defect_class_id
    ).where(subq.c.rn == 1)
)

road_defect_df = pd.read_sql(query, engine)
output_path = "Road Defects Summary.csv"

rename_map = {
    'defect_id': 'Defect ID', 'road_no': 'Road No',
    'degree_classification': 'Defect Type',
    'confidence_detect': 'Confidence', 'degree_classification': 'Degree',
    'defect_class_name': 'Defect Type'
}

road_defect_df = road_defect_df.rename(columns=rename_map)

road_defect_df['Name'] = (
    road_defect_df['Defect ID'].astype(str) + 
    '_fn_' + 
    road_defect_df['frame_number'].astype(str) + 
    '.jpg'
)

col = road_defect_df.pop('Name')
col_2 = road_defect_df.pop('frame_number')
col_3 = road_defect_df.pop('Defect Type')
road_defect_df.insert(0, 'Name', col)
road_defect_df.insert(3,'Defect Type', col_3)
road_defect_df.to_csv(output_path, index=False, encoding="utf-8")
print(f"Data succesfully printed to: {output_path}")
print(f"There are a total of {len(road_defect_df)} records.")

