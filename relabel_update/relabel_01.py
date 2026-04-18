import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import (create_engine, Column, String,Float,Numeric, Boolean, Integer,tuple_,func, text, DateTime)
from sqlalchemy.orm import sessionmaker, declarative_base
from decimal import Decimal

load_dotenv()

TABLE_NAME = os.getenv("TABLE_NAME")
SCHEMA_NAME = os.getenv("SCHEMA_NAME")
DB_URL = os.getenv("DB_URL")
ROOT_PATH = os.getenv("ROOT_PATH")
TARGET_ROUND = os.getenv("TARGET_ROUND")
TARGET_ROUND_2 = os.getenv("TARGET_ROUND_2")
TARGET_ROUND_3 = os.getenv("TARGET_ROUND_3")
TARGET_ROUND_4 = os.getenv("TARGET_ROUND_4")
INSPECTION_ROUNDS = [TARGET_ROUND, TARGET_ROUND_2, TARGET_ROUND_3, TARGET_ROUND_4]
MY_COLUMNS = ['metadata_id', 'file_list', 'flags', 'temporal_coordinates', 'spatial_coordinates', 'metadata']

Base = declarative_base()

class ImageData(Base):
    __tablename__ = TABLE_NAME
    __table_args__ ={"schema": SCHEMA_NAME} 

    id = Column(Integer, primary_key=True, autoincrement=True)
    defect_id = Column(String (30))
    road_no = Column(String (20))
    segment_id_500m = Column(String (20))
    gps_latitude = Column(Float)
    video_source = Column(String (30))
    gps_longitude = Column(Float)
    gps_altitude_m = Column(Float)
    ra_region = Column(String (30))
    ra_area = Column(String(30))
    track_id = Column(Integer)
    confidence_detect = Column(Numeric(precision=5, scale=2))
    inspection_round = Column(String(30))
    degree_classification = Column(String(30))
    frame_x_min = Column(Float)
    frame_y_min = Column(Float)
    frame_x_max = Column(Float)
    frame_y_max = Column(Float)
    frame_number = Column(Integer)
    verified = Column(Boolean)
    is_deleted = Column(Boolean)
    is_sealed = Column (Boolean)
    timestamp = Column(DateTime)
    distance_to_segment = Column(Numeric(precision=5, scale=2))

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

pd.set_option('future.no_silent_downcasting', True)

def integrate_db_and_reindex(cleaned_df, session, ImageData):
    
    identity_cols = ['defect_id', 'frame_number', 'inspection_round']
    extra_db_cols = ['gps_longitude', 'gps_latitude', 'gps_altitude_m', 'distance_to_segment',
                     'confidence_detect', 'degree_classification', 'verified','is_deleted',
                     'ra_region', 'ra_area','road_no', 'segment_id_500m', 'is_sealed', 'timestamp'
    ]
    all_target_cols = identity_cols + extra_db_cols
    query_columns = [getattr(ImageData, col) for col in all_target_cols]

    search_keys = list(
        cleaned_df[identity_cols]
        .drop_duplicates()
        .dropna(subset=identity_cols)
        .itertuples(index=False, name=None)
    )

    db_hits_list = []
    for i in range(0, len(search_keys), 500):
        batch = search_keys[i : i + 500]
        # Using *query_columns ensures only items defined are returned per row
        hits = (
            session.query(*query_columns)
            .filter(tuple_(ImageData.defect_id, 
                           ImageData.frame_number, 
                           ImageData.inspection_round).in_(batch))
            .all()
        )
        db_hits_list.extend(hits)

    hits_df = pd.DataFrame(db_hits_list, columns=all_target_cols)
    final_df = pd.merge(cleaned_df, hits_df, on=identity_cols, how='left')

    max_db_track_id = session.query(func.max(ImageData.track_id)).scalar() or 0
    
    unique_local_tracks = sorted(final_df['track_id'].dropna().unique())
    track_mapping = {old: (max_db_track_id + i + 1) for i, old in enumerate(unique_local_tracks)}
    
    final_df['track_id'] = final_df['track_id'].map(track_mapping)
    final_df['defect_id'] = final_df['video_source'].astype(str) + "_" + final_df['track_id'].astype(str)
    
    # Rebuild the final defect_id string
    final_df[extra_db_cols] = (
        final_df.groupby('defect_id')[extra_db_cols]
        .transform(lambda x: x.ffill().bfill()).infer_objects(copy=False)
    )

    start_id = max_db_track_id + 1
    final_df['track_id'] = range(start_id, start_id + len(final_df))
    final_df['defect_id'] = final_df['video_source'].astype(str) + "_" + final_df['track_id'].astype(str)

    final_df['confidence_detect'] = Decimal('1.00')
    final_df['degree_classification'] = 'NotRated'

    return final_df

def build_and_merge_rounds(base_path, output_folder):
    local_csv_map = {round_id: [] for round_id in INSPECTION_ROUNDS}

    print(f"\nGrouping files...")
    print(f"Looking for these rounds: {INSPECTION_ROUNDS}")

    for root, _, files in os.walk(base_path):
        for filename in files:
            if not filename.lower().endswith('.csv'):
                continue

            matched = False
            for round_id in INSPECTION_ROUNDS:
                if round_id and (round_id in filename):
                    local_csv_map[round_id].append(os.path.join(root, filename))
                    matched = True
                    break 

            if not matched:
                print(f"Ignored file (no round ID match): {filename}")

            csv_parts = filename.split('_')
            
            if len(csv_parts) >= 2:
                csv_id = f"{csv_parts[0]}_{csv_parts[1]}"
                
                # Strip '.csv' from the second part if there's a suffix
                if csv_id.endswith('.csv'):
                    csv_id = csv_id[:-4]

                if csv_id in local_csv_map:
                    local_csv_map[csv_id].append(os.path.join(root, filename))

    # Perform the merge
    for round_id, file_paths in local_csv_map.items():
        if not file_paths:
            print(f"No files found for {round_id}. Skipping.")
            continue

        rename_map = {
            '# CSV_HEADER = metadata_id': 'metadata_id'
        }

        print(f"Processing: {round_id}")
        df_list = []
        for f in file_paths:
            df = pd.read_csv(f, skiprows=10, names=MY_COLUMNS, low_memory=False)
            df = df.rename(columns=rename_map)
            df['inspection_round'] = round_id
            df_list.append(df)

        combined_df = pd.concat(df_list, ignore_index=True)
        cleaned_df = extract_csv_values(combined_df)

        cleaned_df = cleaned_df.dropna(subset=['defect_class_id'])

        cols_to_drop = ['file_list', 'spatial_coordinates','temporal_coordinates', 'flags', 'metadata_id', 'x','metadata']
        cleaned_df.drop(columns=cols_to_drop, errors='ignore', inplace=True)

        raw_output =os.path.join(output_folder, f"{round_id}_merged.csv")
        cleaned_df.to_csv(raw_output, index=False)

        if not cleaned_df.empty:
            cleaned_df = integrate_db_and_reindex(cleaned_df, session, ImageData)

        output_name = os.path.join(output_folder, f"{round_id}_db.csv")
        cleaned_df.to_csv(output_name, index=False)    

        db_ready_df = cleaned_df.drop(columns= ['id'], errors='ignore')

        try:
            cleaned_df.to_sql(
                name=TABLE_NAME, 
                con=engine, 
                schema=SCHEMA_NAME, 
                if_exists='append', 
                index=False,
                method='multi'
            )
            session.commit()
            print(f"Successfully inserted {len(db_ready_df)} rows for {round_id}")
            update_query = """
                UPDATE wip_2026_02.road_defects AS target
                SET geom = source.geom
                FROM wip_2026_02.road_defects AS source
                WHERE target.video_source = source.video_source 
                AND target.inspection_round = source.inspection_round 
                AND target.frame_number = source.frame_number
                AND target.geom IS NULL AND source.geom IS NOT NULL;
                """
            session.execute(text(update_query))
            session.commit()
            print(f"Successfully filled geometry for {round_id}")

        except Exception as e:
            session.rollback()
            print(f"\n!!! DATABASE ERROR on Round: {round_id} !!!")
    
            if hasattr(e, 'orig'):
                print(f"Specific SQL Error: {e.orig}")
            else:
                print(f"Error: {str(e)[:500]}") # Print the first 500 chars of the error
        yield round_id, cleaned_df

def extract_csv_values(merged_df):
    df = merged_df.copy()
    chars_to_remove = '[]{}"\':'

    f_parts = df['file_list'].str.strip(chars_to_remove).str.split('_')
    s_parts = df['spatial_coordinates'].str.strip(chars_to_remove).str.split(',')
    m_parts = df['metadata'].str.strip(chars_to_remove).str.split(':')

    # file_list logic
    df['video_source'] = f_parts.str[0]
    df['track_id'] = f_parts.str[1]
    df['defect_id'] = f_parts.str[0] + "_" + f_parts.str[1]
    df['frame_number'] = f_parts.str[3].str.split('.').str[0]
    df['frame_number'] = pd.to_numeric(df['frame_number'], errors='coerce')

    # spatial_coordinates logic
    coord_cols = ['x','frame_x_min', 'frame_y_min', 'frame_x_max', 'frame_y_max']
    s_parts= s_parts.fillna({i: [] for i in s_parts.index})
    df[coord_cols] = pd.DataFrame(s_parts.tolist(), index=df.index)
    for col in coord_cols:
        df[col] = pd.to_numeric(df[col], errors= 'coerce')

    df['frame_x_max'] = df['frame_x_min'] + df['frame_x_max']
    df['frame_y_max'] = df['frame_y_min'] + df['frame_y_max']
    cols_to_round = ['frame_x_min', 'frame_y_min', 'frame_x_max', 'frame_y_max']
    df[cols_to_round] = df[cols_to_round].round(0)

    # metadata logic
    clean_strings = df['metadata'].str.strip('{}').str.replace('"', '', regex=False)
    m_parts = clean_strings.str.split(':')
    df['defect_class_id'] = pd.to_numeric(m_parts.str[1], errors='coerce')

    return df    

if __name__ == "__main__":
    input_path = r'C:\Users\is2648257\Documents\Videos\Csv\relabeling csv'
    output_path = r'C:\Users\is2648257\Documents\Videos\Csv\relabeling csv\results'
    
    for r_id, cleaned_df in build_and_merge_rounds(input_path, output_path):
        print(f"\n--- Processing Complete for {r_id} ---")
        # print(f"New columns: {cleaned_df.columns.tolist()}")