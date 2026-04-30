import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import LineString

rename_map = {
'GoPro:GPSLatitude' : 'lat', 'GoPro:GPSLongitude' : 'lon', 'GoPro:GPSAltitude': 'alt'
}

df = pd.read_csv (r"C:\Users\is2648257\Documents\Videos\Test_videos_6\2026-04-28-10-47-30\Gps_metadata.csv").rename(columns=rename_map)

df = df.drop("GoPro:ElectronicImageStabilization", axis='columns')
df = df.dropna(how='any')

# df.to_csv("new_gps.csv", index=False)

gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.lon,df.lat,df.alt),
    crs="EPSG:4326"
)

gdf_meters = gdf.to_crs(epsg=3857)

path_line = LineString(gdf_meters.geometry.tolist())

distances = np.arange(0, path_line.length, 20)
interpolated_points = [path_line.interpolate(d) for d in distances]


result_gdf = gpd.GeoDataFrame(geometry=interpolated_points, crs="EPSG:3857")
result_gdf = result_gdf.to_crs(epsg=4326)

result_gdf['Longitude'] = result_gdf.geometry.x
result_gdf['Latitude'] = result_gdf.geometry.y
result_gdf['Altitude'] = result_gdf.geometry.z
result_gdf['Distance_m'] = distances

result_gdf.to_file("gps_intervals.gpkg", driver='GPKG')

result_gdf.drop(columns='geometry').to_csv("gps_intervals.csv", index=False)