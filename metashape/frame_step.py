import pandas as pd
import numpy as np

# --- CONFIGURATION WINDOW ---
START_WINDOW = "00:30"  # MM:SS format (e.g., skip first 30 seconds)
END_WINDOW = "04:30"    # MM:SS format (e.g., cut off at 4 minutes 30 seconds)
FRAME_STEP = 10
FPS = 239.76023976023976

def time_str_to_seconds(t_str):
    """Converts MM:SS string to total seconds."""
    minutes, seconds = map(float, t_str.split(':'))
    return (minutes * 60) + seconds

# Convert window strings to seconds
start_secs = time_str_to_seconds(START_WINDOW)
end_secs = time_str_to_seconds(END_WINDOW)

# 1. READ AND CLEAN GPS DATA
df = pd.read_csv(r"F:\1\2026-05-26-11-08-30\Gps_metadata.csv")
df['unix_time'] = pd.to_datetime(df['GoPro:GPSDateTime'], format='%Y:%m:%d %H:%M:%S.%f').astype(np.int64) / 10**9

# Clean trailing duplicates (The 400 rows of overflow)
df['moved'] = df['GoPro:GPSLatitude'].diff().abs() + df['GoPro:GPSLongitude'].diff().abs()
last_moving_row = df[df['moved'] > 0].index.max()
df_clean = df.iloc[:last_moving_row + 1].copy()

# Treat the first GPS timestamp as Time = 0
start_time = df_clean['unix_time'].iloc[0]
df_clean['relative_time'] = df_clean['unix_time'] - start_time

# 2. BOUNDARY CHECKS
max_gps_duration = df_clean['relative_time'].max()
if end_secs > max_gps_duration:
    print(f"Warning: END_WINDOW ({END_WINDOW}) exceeds data duration ({max_gps_duration:.2f}s). Capping to end.")
    end_secs = max_gps_duration

# 3. GENERATE TARGET WINDOW FRAMES
# Calculate the exact frame offsets in the 240fps timeline
start_frame = int(start_secs * FPS)
end_frame = int(end_secs * FPS)

# Generate actual frame numbers on the master 240fps timeline inside our window
actual_frames = list(range(start_frame, end_frame, FRAME_STEP))

# Map sequential image labels: 0, 1, 2, 3... corresponding to the extracted subset
image_labels = list(range(len(actual_frames)))

# Calculate time based on the ACTUAL frame position in the 240fps timeline
target_times = [f / FPS for f in actual_frames]

# 4. INTERPOLATE WITHIN WINDOW
interp_lat = np.interp(target_times, df_clean['relative_time'], df_clean['GoPro:GPSLatitude'])
interp_lon = np.interp(target_times, df_clean['relative_time'], df_clean['GoPro:GPSLongitude'])
interp_alt = np.interp(target_times, df_clean['relative_time'], df_clean['GoPro:GPSAltitude'])

# 5. OUTPUT PREPARATION
output = pd.DataFrame({
    'label': [f"frame{i}.png" for i in image_labels],
    'lon': interp_lon,
    'lat': interp_lat,
    'alt': interp_alt
})

output.to_csv("metashape.csv", index=False)
print(f"Done! Extracted {len(output)} frames from {START_WINDOW} to {END_WINDOW} (Step: {FRAME_STEP}).")