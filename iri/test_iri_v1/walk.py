import pandas as pd
import numpy as np
import sys

FRAME_RATE = 239.76023976024
GPS_FILE_PATH = r'C:\Users\is2648257\Documents\Videos\2025-11-24-11-48-37\videos_metadata.csv'
FRAMES_FILE_PATH = r'C:\Users\is2648257\Documents\Videos\Csv\Book1.csv'

GPS_TIMESTAMP_COL = 'GoPro:GPSDateTime'
GPS_LAT_COL = 'GoPro:GPSLatitude'
GPS_LON_COL = 'GoPro:GPSLongitude'
GPS_ALT_COL = 'GoPro:GPSAltitude'
FRAME_NUM_COL = 'frame'

try:
    gps_df = pd.read_csv(GPS_FILE_PATH)
    gps_df[GPS_TIMESTAMP_COL] = gps_df[GPS_TIMESTAMP_COL].str.replace(':', '-', n=2)
    gps_df[GPS_TIMESTAMP_COL] = pd.to_datetime(gps_df[GPS_TIMESTAMP_COL])

    start_time = gps_df[GPS_TIMESTAMP_COL].iloc[0]
    gps_df['seconds_since_start'] = (gps_df[GPS_TIMESTAMP_COL] - start_time).dt.total_seconds()
    
except FileNotFoundError:
    print(f"Error: GPS file not found at {GPS_FILE_PATH}.")
    sys.exit() 

try:
    frames_df = pd.read_csv(FRAMES_FILE_PATH)
    frames_df['Frame_Timestamp_s'] = frames_df[FRAME_NUM_COL] / FRAME_RATE
except FileNotFoundError:
    print(f"Error: Frames file not found at {FRAMES_FILE_PATH}.")
    sys.exit()

def interpolate_coords(frame_time_s, gps_df):
    
    lower = gps_df[gps_df['seconds_since_start'] <= frame_time_s]
    upper = gps_df[gps_df['seconds_since_start'] > frame_time_s]

    if lower.empty or upper.empty:
        return np.nan, np.nan, np.nan
    
    # Get the specific rows (last of the lower, first of the upper)
    p1 = lower.iloc[-1]
    p2 = upper.iloc[0]

    t1 = p1['seconds_since_start']
    t2 = p2['seconds_since_start']
 
    if t2 == t1:
        return p1[GPS_LAT_COL], p1[GPS_LON_COL], p1[GPS_ALT_COL]

    fraction = (frame_time_s - t1) / (t2 - t1)

    lat = p1[GPS_LAT_COL] + fraction * (p2[GPS_LAT_COL] - p1[GPS_LAT_COL])
    lon = p1[GPS_LON_COL] + fraction * (p2[GPS_LON_COL] - p1[GPS_LON_COL])
    alt = p1[GPS_ALT_COL] + fraction * (p2[GPS_ALT_COL] - p1[GPS_ALT_COL])

    return lat, lon, alt

# WRAPPER FOR APPLY
def get_coords(row, df_gps_data):
    return interpolate_coords(row['Frame_Timestamp_s'], df_gps_data)

print("Starting interpolation...")

frames_df[['GPS_Latitude', 'GPS_Longitude', 'GPS_Altitude']] = frames_df.apply(
    lambda row: get_coords(row, gps_df), 
    axis=1, 
    result_type='expand'
)

final_colums = [
    FRAME_NUM_COL,
    'Frame_Timestamp_s',
    'GPS_Latitude',
    'GPS_Longitude',
    'GPS_Altitude'
]

final_df = frames_df[final_colums]

OUTPUT_FILE_NAME = 'interpolated_coords.csv'
final_df.to_csv(OUTPUT_FILE_NAME, index=False)

print("\n---Processing Complete---")
print(f"Succesfully saved to {OUTPUT_FILE_NAME}")
print(final_df.head())