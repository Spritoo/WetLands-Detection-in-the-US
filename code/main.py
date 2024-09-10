import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
import numpy as np
from pyproj import Transformer


def create_circle(center, radius, num_points=100):
    """Create a circular Polygon around a center point.

    Args:
        center (tuple): (x, y) coordinates of the circle center.
        radius (float): Radius of the circle in meters.
        num_points (int): Number of points to approximate the circle.

    Returns:
        Polygon: A shapely Polygon representing the circle.
    """
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    x_center, y_center = center
    x_points = x_center + radius * np.cos(angles)
    y_points = y_center + radius * np.sin(angles)
    points = list(zip(x_points, y_points))
    return Polygon(points)


def calculate_intersection_area(circle, features):
    """Calculate the area of the circle that intersects with the given features.

    Args:
        circle (Polygon): The circular Polygon.
        features (GeoDataFrame): The GeoDataFrame containing features.

    Returns:
        float: Area of the intersection in square meters.
    """
    intersection_area = 0
    for _, feature in features.iterrows():
        intersection = circle.intersection(feature.geometry)
        intersection_area += intersection.area
    return intersection_area

excelFilePath = 'coordinates.xlsx'
latColumnName = 'Lat'
longColumnName = 'Lng'
acreColumnName = 'Acre'
# Load the Excel file
df = pd.read_excel(excelFilePath)
df.dropna(subset=[longColumnName, latColumnName, acreColumnName], inplace=True)
df.drop_duplicates(subset=[longColumnName, latColumnName], inplace=True)

# Create Transformer object for converting between EPSG:4326 and EPSG:32610
transformer_to_utm = Transformer.from_crs("EPSG:4326", "EPSG:32610", always_xy=True)

# Load the layer from the GeoPackage
gpkgs = gpd.read_file('CA_Wetlands_Geopackage.gpkg', layer='California_Wetlands')

# Ensure the GeoDataFrame is in the same CRS as the circle
gpkgs = gpkgs.to_crs(epsg=32610)

# List to store the wetlands percentage for each land parcel
wetlands_percentages = []

# Iterate through each row in the Excel sheet
for index, row in df.iterrows():
    lon, lat = row[longColumnName], row[latColumnName]
    acres = row[acreColumnName]

    # Convert acres to square meters
    area_sqm = (acres * 4046.86)   # Convert acres to square meters

    # Calculate the radius in meters
    radius_meters = np.sqrt(area_sqm / np.pi)

    # Convert the center point to UTM
    x_center, y_center = transformer_to_utm.transform(lon, lat)

    # Create the circle in UTM coordinates
    circle_utm = create_circle((x_center, y_center), radius_meters)

    # Check for intersection
    intersects = gpkgs[gpkgs.geometry.intersects(circle_utm)]

    # Calculate the area of the intersection
    intersection_area = calculate_intersection_area(circle_utm, intersects)

    # Calculate the area of the circle
    circle_area = circle_utm.area

    # Calculate the percentage of intersection (wetlands coverage)
    intersection_percentage = (intersection_area / circle_area) * 100 if circle_area > 0 else 0

    # Append the wetlands percentage to the list
    wetlands_percentages.append(intersection_percentage)

# Add the wetlands percentage column to the original DataFrame
df['Wetlands Percentage (%)'] = wetlands_percentages

# Output the modified DataFrame to a new Excel file
df.to_excel(f'{excelFilePath}wetlands.xlsx', index=False)

print("Process completed and results saved to 'land_parcels_with_wetlands_percentage.xlsx'.")
