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

GRAV_CSV = r"C:\Users\is2648257\Documents\Videos\Test_videos_04\2026-01-19-15-24-25\GravityVector_metadata.csv"
GYRO_CSV = r"C:\Users\is2648257\Documents\Videos\Test_videos_04\2026-01-19-15-24-25\Gyroscope_metadata.csv"
ACCEL_CSV = r"C:\Users\is2648257\Documents\Videos\Test_videos_04\2026-01-19-15-24-25\Accelerometer_metadata.csv"
GPS_CSV = r"C:\Users\is2648257\Documents\Videos\Test_videos_04\2026-01-19-15-24-25\Gps_metadata.csv"    
SUSPENSION_TYPE = "HARD" 

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

    if iri <= IRI_QUALITY_1:
        return RoadQuality.EXCELLENT
    elif IRI_QUALITY_1 <= iri <= IRI_QUALITY_2:
        return RoadQuality.GOOD
    elif IRI_QUALITY_2 < iri <= IRI_QUALITY_3:
        return RoadQuality.FAIR
    else:
        return RoadQuality.POOR

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

def process_and_save_spatial(merged_df):
    final_df = merged_df.copy().dropna(subset=['gps_latitude', 'gps_longitude'])
    
    gdf_w_geometry = gpd.GeoDataFrame(
        final_df, 
        geometry=gpd.points_from_xy(final_df.gps_longitude, final_df.gps_latitude),
        crs="EPSG:4326"
    ).to_crs("EPSG:3857") 

    road_seg = gpd.read_file(r"C:\Users\is2648257\Documents\Videos\Csv\road_segments.gpkg")
    # print(road_seg.columns)

    road_w_merged = gpd.sjoin_nearest(gdf_w_geometry, road_seg, how='left', max_distance=20)
    # print(road_w_merged.columns)
    # road_w_merged['length_km'] = road_w_merged.geometry.length / 1000
    # print(road_w_merged.head())

    point_to_point_dist = road_w_merged.geometry.distance(road_w_merged.geometry.shift(1)).fillna(0)
    road_w_merged['distance'] = point_to_point_dist.cumsum() /1000

    total_distance_km = road_w_merged['distance'].iloc[-1]
    output_filename = "geometry_points.gpkg"
    road_w_merged.to_file(output_filename, driver='GPKG')
    print(f"Total Distance from GPS: {total_distance_km:,.2f} kilometers")

    return road_w_merged

def main():
    df = load_interpolation_data(
        grav_csv=GRAV_CSV, 
        gps_csv=GPS_CSV, 
        accel_csv=ACCEL_CSV, 
        gyro_csv=GYRO_CSV
    )
    df = process_and_save_spatial(df)

    source_file = df['source_file'].iloc[0] if 'source_file' in df.columns else 'unknown'
    segments = []
    grouped = df.groupby('segment_id')

    for segment_id, segment_df in grouped:
        if not segment_df.empty:
            start_dist = segment_df['from_km'].min()
            end_dist = segment_df['to_km'].max()
            total_seg_length = end_dist - start_dist
            
            segments.append({
                'segment_id': segment_id,
                'from_km': start_dist,
                'to_km': end_dist,
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
                'road_segment_id': segment['segment_id'],  
                'from_km': segment['from_km'],
                'to_km': segment['to_km'],
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
        distances = [(r['from_km'] + r['to_km']) / 2 for r in results]
        iris = [r['iri'] for r in results]
        plt.figure(figsize=(10, 6))
        plt.plot(distances, iris, marker='o', linestyle='-')
        plt.title(f'IRI vs Distance')
        plt.xlabel('Distance (km)')
        plt.ylabel('IRI')
        plt.grid(True)
        plot_filename = f"{source_file}_iri_plot.png" if source_file != 'unknown' else "iri_plot.png"
        plt.savefig(plot_filename)
        print(f"IRI plot saved to {plot_filename}")
        plt.close()
    else:
        print("No valid IRI calculations")
        print(f"Total number of records is : {len(df)} ")

if __name__ == "__main__":
    main()
    