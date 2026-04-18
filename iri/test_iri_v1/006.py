import pandas as pd
import numpy as np
from scipy import interpolate

GRAV_CSV = r"C:\Users\is2648257\Documents\Videos\Test_videos_04\2026-01-19-15-24-25\GravityVector_metadata.csv"
GYRO_CSV = r"C:\Users\is2648257\Documents\Videos\Test_videos_04\2026-01-19-15-24-25\Gyroscope_metadata.csv"
ACCEL_CSV = r"C:\Users\is2648257\Documents\Videos\Test_videos_04\2026-01-19-15-24-25\Accelerometer_metadata.csv"
GPS_CSV = r"C:\Users\is2648257\Documents\Videos\Test_videos_04\2026-01-19-15-24-25\Gps_metadata.csv"

def load_interpolation_data(grav_csv, gps_csv,accel_csv, gyro_csv):

    grav_df = pd.read_csv(grav_csv)
    gps_df = pd.read_csv(gps_csv)  
    accel_df = pd.read_csv(accel_csv)
    gyro_df = pd.read_csv(gyro_csv)

    rename_map = {
        'GravityVector_X': 'gx', 'GravityVector_Y': 'gy', 'GravityVector_Z': 'gz',
        'Accelerometer_X': 'ax', 'Accelerometer_Y': 'ay', 'Accelerometer_Z': 'az',
        'Gyroscope_X': 'gyro_x', 'Gyroscope_Y': 'gyro_y', 'Gyroscope_Z': 'gyro_z',
        'GoPro:GPSSpeed': 'speed', 'GoPro:GPSLatitude': 'gps_latitude', 
        'GoPro:GPSLongitude': 'gps_longitude', 'GoPro:GPSAltitude': 'gps_altitude',
        'GoPro:GPSDateTime': 'time', 'SourceFile': 'source_file'
    }

    grav_df = grav_df.rename(columns=rename_map)
    accel_df = accel_df.rename(columns=rename_map)
    gyro_df = gyro_df.rename(columns=rename_map)
    gps_df = gps_df.rename(columns=rename_map)

    start_time = pd.to_datetime(gps_df['time'].iloc[0], format='%Y:%m:%d %H:%M:%S.%f')

    grav_ticks = np.arange(len(grav_df)) * (1/240)
    grav_df['time'] = start_time + pd.to_timedelta(grav_ticks, unit='s')
    gyro_ticks = np.arange(len(gyro_df)) * (1/198.721)
    gyro_df['time'] = start_time + pd.to_timedelta(gyro_ticks, unit='s')
    accel_ticks = np.arange(len(accel_df)) * (1/198.721)
    accel_df['time'] = start_time + pd.to_timedelta(accel_ticks, unit='s')

    gps_df['time'] = pd.to_datetime(gps_df['time'], format='%Y:%m:%d %H:%M:%S.%f')

    for df in [grav_df, gyro_df, accel_df, gps_df]:
            df['time'] = df['time'].astype('int64') / 1e9 
            df.sort_values('time', inplace=True)

    min_time = max(grav_df['time'].min(), gps_df['time'].min(), accel_df['time'].min(), gyro_df['time'].min())
    max_time = min(grav_df['time'].max(), gps_df['time'].max(), accel_df['time'].max(), gyro_df['time'].max())

    common_times = np.arange(min_time, max_time, 1/240.0)

    print(f"Starting interpolation.....")
    print("Accel CSV columns:", accel_df.columns)
    print("Actual Gyro CSV columns:", gyro_df.columns)

    def interpolate_df(df, time_col, value_cols, new_times):
            interp_df = pd.DataFrame({'time': new_times})
            for col in value_cols:
                if col in df.columns:
                    interp_func = interpolate.interp1d(df[time_col], df[col], kind='linear', bounds_error=False, fill_value=np.nan)
                    interp_df[col] = interp_func(new_times)
            return interp_df

    grav_interp = interpolate_df(grav_df, 'time', ['gx', 'gy','gz'], common_times)
    accel_interp = interpolate_df(accel_df, 'time', ['ax', 'ay','az'], common_times)
    gyro_interp = interpolate_df(gyro_df, 'time', ['gyro_x', 'gyro_y','gyro_z'], common_times)
    gps_interp = interpolate_df(gps_df, 'time', ['speed', 'gps_latitude', 'gps_longitude', 'gps_altitude'], common_times)
    gyro_interp['rotation_angle'] = np.cumsum(gyro_interp['gyro_x'] * (1/240.0))

    merged_df = pd.DataFrame({'time': common_times})
    merged_df = merged_df.merge(grav_interp, on='time', how='left')
    merged_df = merged_df.merge(accel_interp, on='time', how='left')
    merged_df = merged_df.merge(gyro_interp, on='time', how='left')
    merged_df = merged_df.merge(gps_interp, on='time', how='left')
    merged_df['speed_ms'] = merged_df['speed'] / 3.6  # km/h to m/s
    merged_df['time'] = pd.to_datetime(merged_df['time'], unit='s')

    if not gps_df.empty and 'source_file' in gps_df.columns:
        file_val = gps_df['source_file'].iloc[0]
    else:
        file_val = 'unknown'
    merged_df.insert(0, 'source_file', file_val)
    
    merged_df.index = merged_df.index + 1
    merged_df.to_csv('interpolated_sensors.csv', index=True, index_label= "row_number")
    
    return merged_df

def main():
      df = load_interpolation_data(
        grav_csv=GRAV_CSV, 
        gps_csv=GPS_CSV, 
        accel_csv=ACCEL_CSV, 
        gyro_csv=GYRO_CSV
    )
      
      print(f"Total number of records is : {len(df)} ")
if __name__ == "__main__":
    main()
    
    


  