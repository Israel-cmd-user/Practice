import pandas as pd
import numpy as np
import math
import geopandas as gpd
from scipy import interpolate
import matplotlib.pyplot as plt
from enum import Enum

IRI_QUALITY_1 = 2
IRI_QUALITY_2 = 4
IRI_QUALITY_3 = 6
quality_1 = IRI_QUALITY_1
quality_2 = IRI_QUALITY_2
quality_3 = IRI_QUALITY_3

class IRITable:
    SOFT_SPN = 0
    MEDIUM_SPN = 1
    HARD_SPN = 2
    FIXED_DEVICE = 0
    NON_FIXED_DEVICE = 1
    SD_THRESHOLD = 1

    def __init__(self, suspension='SOFT'):
        self.suspension = suspension.upper()
        self.interceptArray = {
            'FIXED': {
                'SOFT': 1.69459656,
                'MEDIUM': 1.258364,
                'HARD': 1.879921
            },
            'NON_FIXED': {
                'SOFT': 2.045447,
                'MEDIUM': 1.403616,
                'HARD': 2.511125
            }
        }

        self.sdArray = {
            'FIXED': {
                'SOFT': 6.41623959,
                'MEDIUM': 5.215198143,
                'HARD': 5.852457679
            },
            'NON_FIXED': {
                'SOFT': 6.479570671,
                'MEDIUM': 6.902960942,
                'HARD': 6.177132368
            }
        }

        self.speedArray = {
            'FIXED': {
                'SOFT': -0.02443565,
                'MEDIUM': -0.028562,
                'HARD': -0.01145
            },
            'NON_FIXED': {
                'SOFT': -0.0291,
                'MEDIUM': -0.023693,
                'HARD': -0.03385
            }
        }

        self.sdArrayPow2 = {
            'FIXED': {'SOFT': 0, 'MEDIUM': 0, 'HARD': 0},
            'NON_FIXED': {'SOFT': 0, 'MEDIUM': 0, 'HARD': 0}
        }

        self.sdSpeedArray = {
            'FIXED': {
                'SOFT': -0.0347419,
                'MEDIUM': -0.020729451,
                'HARD': -0.03934122
            },
            'NON_FIXED': {
                'SOFT': -0.032741179,
                'MEDIUM': -0.030271466,
                'HARD': -0.011064654
            }
        }

    def getValue(self, array, isFixed):
        device = 'FIXED' if isFixed else 'NON_FIXED'
        return array[device][self.suspension]

    def getIntercept(self, isFixed, sd):
        return self.getValue(self.interceptArray, isFixed)

    def getSd(self, isFixed, sd):
        return self.getValue(self.sdArray, isFixed)

    def getSpeed(self, isFixed, sd):
        return self.getValue(self.speedArray, isFixed)

    def getSdPow2(self, isFixed, sd):
        return self.getValue(self.sdArrayPow2, isFixed)

    def getSdSpeed(self, isFixed, sd):
        return self.getValue(self.sdSpeedArray, isFixed)

class DeviceStateDetector:
    VECTOR_X = 0
    VECTOR_Y = 1
    VECTOR_Z = 2
    DEVICE_STATE_VERTICAL = 0
    DEVICE_STATE_HORIZONTAL = 1
    STATE_DETECTION_THRESHOLD = 9.80665 * 0.9

    def calcState(self, gx, gy, gz):
        if abs(gx) >= self.STATE_DETECTION_THRESHOLD or abs(gy) >= self.STATE_DETECTION_THRESHOLD:
            return self.DEVICE_STATE_VERTICAL
        elif abs(gz) >= self.STATE_DETECTION_THRESHOLD:
            return self.DEVICE_STATE_HORIZONTAL
        return -1

    def calcStateFromRecords(self, records):
        fixedState = 0
        nonFixedState = 0
        for r in records:
            state = self.calcState(r['gx'], r['gy'], r['gz'])
            if state == self.DEVICE_STATE_HORIZONTAL:
                nonFixedState += 1
            elif state == self.DEVICE_STATE_VERTICAL:
                fixedState += 1
        if fixedState > nonFixedState:
            return self.DEVICE_STATE_VERTICAL
        elif nonFixedState > fixedState:
            return self.DEVICE_STATE_HORIZONTAL
        return self.DEVICE_STATE_HORIZONTAL  # default

    def isDeviceFixedState(self, state):
        return state == self.DEVICE_STATE_VERTICAL

class RoadConditionDetection:
    G = 9.80665
    ANGLE_THRESHOLD = 15
    IRI_DEFAULT_VALUE = 1.0

    def __init__(self, iriTable, deviceDetector):
        self.iriTable = iriTable
        self.deviceDetector = deviceDetector

    def getAv(self, gx, gy, gz, ax, ay, az):
        av = (ax * gx + ay * gy + az * gz) / self.G
        return av

    def isValidRotationAngle(self, rotation_angle):
        return abs(rotation_angle) <= self.ANGLE_THRESHOLD

    def getSTD(self, records):
        sumAvs = 0
        count = 0
        valid_records = [r for r in records if self.isValidRotationAngle(r['rotation_angle'])]
        if not valid_records:
            return 0
        meanAv = np.mean([self.getAv(r['gx'], r['gy'], r['gz'], r['ax'], r['ay'], r['az']) for r in valid_records])
        for r in valid_records:
            av = self.getAv(r['gx'], r['gy'], r['gz'], r['ax'], r['ay'], r['az'])
            subAv = av - meanAv
            sumAvs += subAv * subAv
            count += 1
        if count - 1 <= 0:
            return 0
        std = math.sqrt(1.0 / (count - 1) * sumAvs)
        return std

    def calculateIRI(self, std, speed, isFixed):
        interceptConst = self.iriTable.getIntercept(isFixed, std)
        sdConst = self.iriTable.getSd(isFixed, std)
        speedConst = self.iriTable.getSpeed(isFixed, std)
        sdConstPow2 = self.iriTable.getSdPow2(isFixed, std)
        sdSpeedConst = self.iriTable.getSdSpeed(isFixed, std)
        iri = interceptConst + sdConst * std + speedConst * speed + sdConstPow2 * std * std + sdSpeedConst * std * speed
        if iri < 0:
            iri = 0
        return iri

    def processData(self, records):
        if not records:
            return None
        deviceState = self.deviceDetector.calcStateFromRecords(records)
        isFixed = self.deviceDetector.isDeviceFixedState(deviceState)
        stdDeviation = self.getSTD(records)
        if not np.isfinite(stdDeviation) or stdDeviation <= 0:
            return None
        avgSpeed = np.mean([r['speed'] for r in records]) / 3.6  # convert to m/s 
        iri = self.calculateIRI(stdDeviation, avgSpeed, isFixed)
        road_quality = get_road_quality(iri).value
        return {
            'iri': iri,
            'std': stdDeviation,
            'avg_speed': avgSpeed,
            'is_fixed': isFixed, 
            'road_condition': road_quality
        }
    
class RoadQuality(Enum):

    EXCELLENT = "Execellent"
    GOOD = "Good"
    FAIR = "Fair"
    POOR = "Poor"

def get_road_quality(iri:float) -> RoadQuality:

    if iri < IRI_QUALITY_1:
        return RoadQuality.EXCELLENT
    elif iri <= IRI_QUALITY_2:
        return RoadQuality.GOOD
    elif iri <= IRI_QUALITY_3:
        return RoadQuality.FAIR
    else:
        return RoadQuality.POOR

def load_and_interpolate_data( accel_csv, gravity_csv, gyro_csv, gps_csv):
    # Read CSVs
    accel_df = pd.read_csv(accel_csv)
    gravity_df = pd.read_csv(gravity_csv)
    gyro_df = pd.read_csv(gyro_csv)
    gps_df = pd.read_csv(gps_csv)

    accel_df = accel_df.rename(columns={'Accelerometer_Y': 'ax', 'Accelerometer_X': 'ay', 'Accelerometer_Z': 'az', 'SourceFile': 'source_file'})
    gravity_df = gravity_df.rename(columns={'GravityVector_Y': 'gx', 'GravityVector_X': 'gy', 'GravityVector_Z': 'gz', 'SourceFile': 'source_file'})
    gyro_df = gyro_df.rename(columns={'Gyroscope_Y': 'gyro_x', 'Gyroscope_X': 'gyro_y', 'Gyroscope_Z': 'gyro_z', 'SourceFile': 'source_file'})
    gps_df = gps_df.rename(columns={'GoPro:GPSDateTime': 'time', 'GoPro:GPSSpeed': 'speed', 'SourceFile': 'source_file',  'GoPro:GPSLatitude': 'gps_latitude',  'GoPro:GPSLongitude': 'gps_longitude'})

    gps_df['time'] = pd.to_datetime(gps_df['time'], format='%Y:%m:%d %H:%M:%S.%f')
    start_time = pd.to_datetime(gps_df['time'].iloc[0], format='%Y:%m:%d %H:%M:%S.%f')

    accel_ticks = np.arange(len(accel_df)) * (1/200)
    accel_df['time'] = start_time + pd.to_timedelta(accel_ticks, unit='s')

    gyro_ticks = np.arange(len(gyro_df)) * (1/200)
    gyro_df['time'] = start_time + pd.to_timedelta(gyro_ticks, unit='s')

    grav_ticks = np.arange(len(gravity_df)) * (1/240)
    gravity_df['time'] = start_time + pd.to_timedelta(grav_ticks, unit='s')

    # Drop rows with invalid time
    accel_df = accel_df.dropna(subset=['time'])
    gravity_df = gravity_df.dropna(subset=['time'])
    gyro_df = gyro_df.dropna(subset=['time'])
    gps_df = gps_df.dropna(subset=['time'])

    for df in [accel_df, gyro_df, gravity_df, gps_df]:
        df['time'] = df['time'].astype('int64') / 1e9  # Convert nanoseconds to seconds
        df.sort_values('time', inplace=True)

    # Sort by time
    # accel_df = accel_df.sort_values('time')
    # gravity_df = gravity_df.sort_values('time')
    # gyro_df = gyro_df.sort_values('time')
    # gps_df = gps_df.sort_values('time')

    # Determine common time range
    min_time = max( accel_df['time'].min(), gravity_df['time'].min(), gyro_df['time'].min(), gps_df['time'].min())
    max_time = min( accel_df['time'].max(), gravity_df['time'].max(), gyro_df['time'].max(), gps_df['time'].max())

    # Common time grid 
    common_times = np.arange(min_time, max_time, 1/240.0)

    # Interpolate each dataframe to common time grid
    def interpolate_df(df, time_col, value_cols, new_times):
        interp_df = pd.DataFrame({'time': new_times})
        for col in value_cols:
            if col in df.columns:
                interp_func = interpolate.interp1d(df[time_col], df[col], kind='linear', bounds_error=False, fill_value=np.nan)
                interp_df[col] = interp_func(new_times)
        return interp_df

    accel_interp = interpolate_df(accel_df, 'time', ['ax', 'ay', 'az'], common_times)
    gravity_interp = interpolate_df(gravity_df, 'time', ['gx', 'gy'], common_times)
    gyro_interp = interpolate_df(gyro_df, 'time', ['gyro_x', 'gyro_y'], common_times)
    gps_interp = interpolate_df(gps_df, 'time', ['speed', 'gps_latitude', 'gps_longitude'], common_times)

    if 'gz' in gravity_df.columns:
        gz_interp = interpolate_df(gravity_df, 'time', ['gz'], common_times)
        gravity_interp = gravity_interp.merge(gz_interp, on='time', how='left')

    # Integrate gyroscope data to get rotation angles
    gyro_interp['rotation_angle'] = np.cumsum(gyro_interp['gyro_x'] * (1/200.0))  

    merged_df = pd.DataFrame({'time': common_times})
    merged_df = merged_df.merge(accel_interp, on='time', how='left')
    merged_df = merged_df.merge(gravity_interp, on='time', how='left')
    merged_df = merged_df.merge(gyro_interp, on='time', how='left')
    merged_df = merged_df.merge(gps_interp, on='time', how='left')

    # Add source file
    if not gps_df.empty:
        merged_df['source_file'] = gps_df['source_file'] if 'source_file' in gps_df.columns else 'unknown'

    if 'az' in merged_df.columns:
        merged_df['az'] = merged_df['az'].fillna(9.81)
    else:
        merged_df['az'] = 9.81

    if 'gz' in merged_df.columns:
        merged_df['gz'] = merged_df['gz'].fillna(0.0)
    else:
        merged_df['gz'] = 0.0

    merged_df['speed_ms'] = merged_df['speed'] / 3.6  # km/h to m/s

    # # Calculate cumulative distance (speed in m/s, time in seconds)
    # dt = 1/240.0  # time step
    # merged_df['distance'] = (merged_df['speed_ms'] * dt).cumsum()

    merged_df['time'] = pd.to_datetime(merged_df['time'], unit='s')

    merged_df.to_csv('merged_data.csv', index=False)

    process_and_save_spatial(merged_df)

    return merged_df

def process_and_save_spatial(merged_df):
    final_df = merged_df.copy().dropna(subset=['gps_latitude', 'gps_longitude'])
    
    gdf_w_geometry = gpd.GeoDataFrame(
        final_df, 
        geometry=gpd.points_from_xy(final_df.gps_longitude, final_df.gps_latitude),
        crs="EPSG:4326"
    ).to_crs("EPSG:3857") 

    road_seg = gpd.read_file(r"C:\Users\is2648257\Documents\Videos\Csv\road_segments.gpkg")
    road_w_merged = gpd.sjoin_nearest(gdf_w_geometry, road_seg, how='left')

    point_to_point_dist = road_w_merged.geometry.distance(road_w_merged.geometry.shift(1)).fillna(0)
    
    road_w_merged['distance'] = point_to_point_dist.cumsum()

    total_distance_m = road_w_merged['distance'].iloc[-1]
    print(f"Total Distance from GPS: {total_distance_m:,.2f} meters")

    return road_w_merged

ACCEL_CSV = r"C:\Users\is2648257\Documents\Videos\Test_videos_02\2026-01-14-11-54-34\accelerometer.csv"  
GRAVITY_CSV = r"C:\Users\is2648257\Documents\Videos\Test_videos_02\2026-01-14-11-38-36\gravity_vector.csv" 
GYRO_CSV = r"C:\Users\is2648257\Documents\Videos\Test_videos_02\2026-01-14-11-46-14\gyroscope.csv"     
GPS_CSV = r"C:\Users\is2648257\Documents\Videos\Test_videos_02\2026-01-14-11-38-36\videos_metadata.csv"             
SUSPENSION_TYPE = "HARD" 

def main():
    # Load and interpolate data
    df = load_and_interpolate_data( ACCEL_CSV, GRAVITY_CSV, GYRO_CSV, GPS_CSV)
    df = process_and_save_spatial(df)

    source_file = df['source_file'].iloc[0] if 'source_file' in df.columns else 'unknown'

    # max_distance = df['distance'].max()
    # segment_size = 500.0 
    segments = []
    grouped = df.groupby('segment_id', sort=False)

    for segment_id, segment_df in grouped:
        if not segment_df.empty:
            start_dist = segment_df['distance'].min()
            end_dist = segment_df['distance'].max()
            total_seg_length = end_dist - start_dist
            
            segments.append({
                'segment_id': segment_id,
                'start_distance': start_dist,
                'end_distance': end_dist,
                'segment_length': total_seg_length,
                'data': segment_df.to_dict('records')
            })

    # Class initialisation
    iriTable = IRITable(SUSPENSION_TYPE)
    deviceDetector = DeviceStateDetector()
    roadDetector = RoadConditionDetection(iriTable, deviceDetector)

    # Process each segment
    results = []
    for segment in segments:
        result = roadDetector.processData(segment['data'])
        if result:
            results.append({
                'SourceFile': source_file,
                'road_segment_id': segment_id,  
                'start_distance': segment['start_distance'],
                'end_distance': segment['end_distance'],
                'iri': result['iri'],
                'std': result['std'],
                'avg_speed': result['avg_speed'],
                'is_fixed': result['is_fixed'],
                'data_points': len(segment['data']),
                'road_condition': result['road_condition']
            })

    # Output to CSV
    if results:
        output_df = pd.DataFrame(results)
        output_filename = f"{source_file}_iri_results.csv" if source_file != 'unknown' else "iri_results.csv"
        output_df.to_csv(output_filename, index=False, float_format='%.2f')
        print(f"IRI results saved to {output_filename}")
        print(f"Processed {len(results)} segments")

        # Plot IRI vs distance
        distances = [(r['start_distance'] + r['end_distance']) / 2 for r in results]
        iris = [r['iri'] for r in results]
        plt.figure(figsize=(10, 6))
        plt.plot(distances, iris, marker='o', linestyle='-')
        plt.title(f'IRI vs Distance')
        plt.xlabel('Distance (m)')
        plt.ylabel('IRI')
        plt.grid(True)
        plot_filename = f"{source_file}_iri_plot.png" if source_file != 'unknown' else "iri_plot.png"
        plt.savefig(plot_filename)
        print(f"IRI plot saved to {plot_filename}")
        plt.close()
    else:
        print("No valid IRI calculations")

if __name__ == "__main__":
    main()
    