import pandas as pd
import numpy as np


df = pd.read_csv(r"C:\Users\is2648257\Documents\Videos\Test videos\Test_videos_7\2026-04-29-15-09-37\Gps_metadata.csv")
df['unix_time'] = pd.to_datetime(df['GoPro:GPSDateTime'], format='%Y:%m:%d %H:%M:%S.%f').astype(np.int64) / 10**9

# Clean trailing duplicates (The 400 rows of overflow)
df['moved'] = df['GoPro:GPSLatitude'].diff().abs() + df['GoPro:GPSLongitude'].diff().abs()
last_moving_row = df[df['moved'] > 0].index.max()
df_clean = df.iloc[:last_moving_row + 1].copy()

# We treat the first GPS timestamp as Time = 0
start_time = df_clean['unix_time'].iloc[0]
df_clean['relative_time'] = df_clean['unix_time'] - start_time

fps = 240
frame_step = 10
max_duration = df_clean['relative_time'].max()

# 'labels' will be 0, 1, 2, 3... 
# 'actual_frames' will be 0, 10, 20, 30... 
max_label_index = int((max_duration * fps) / frame_step)
image_labels = list(range(0, max_label_index))
actual_frames = [i * frame_step for i in image_labels]

# Calculate time based on the ACTUAL frame position in the 240fps timeline
target_times = [f / fps for f in actual_frames]

# Interpolate using the corrected time axis
interp_lat = np.interp(target_times, df_clean['relative_time'], df_clean['GoPro:GPSLatitude'])
interp_lon = np.interp(target_times, df_clean['relative_time'], df_clean['GoPro:GPSLongitude'])
interp_alt = np.interp(target_times, df_clean['relative_time'], df_clean['GoPro:GPSAltitude'])

output = pd.DataFrame({
    'label': [f"frame{i}.png" for i in image_labels],
    'lon': interp_lon,
    'lat': interp_lat,
    'alt': interp_alt
})

output.to_csv("metashape.csv", index=False)