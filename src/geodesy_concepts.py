#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: geodesy_concepts.py
Description: 
    This script reinforces the concepts of Coordinate Reference System (CRS) hierarchies
    and Datum Shifts using the GDAL and PROJ libraries.
    
    It demonstrates:
    1. The Hierarchy: How EPSG:4326 is a container for Datum (6326) and Ellipsoid (7030).
    2. The Datum Shift: How the "same" physical point changes coordinates when the Datum changes.
    3. The Error: The real-world distance error if Datums are ignored.

Dependencies:
    - gdal (osgeo)
    - pyproj
    
    Install via: pip install gdal pyproj

Reference:
    This script complements the visual structure seen in: /assets/image_1.png
"""

import sys

# Try importing GDAL and PyProj with friendly error handling for novices
try:
    from osgeo import osr
    from pyproj import Transformer, Geod
except ImportError as e:
    print("Error: Missing required libraries.")
    print(f"Details: {e}")
    print("Please install them using: pip install gdal pyproj")
    sys.exit(1)


def print_header(title):
    """Helper function to print clean headers."""
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}")


def inspect_epsg_hierarchy():
    """
    Concept 1: The Hierarchy
    Dissects EPSG:4326 to show the hidden 'Child' codes inside it.
    Reference: See /assets/image_28e358.png for the WKT visualization.
    """
    print_header("1. INSPECTING THE HIERARCHY (EPSG:4326)")
    print("Goal: Prove that EPSG:4326 is a container for other codes.\n")

    # Create a Spatial Reference object for WGS 84
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    # 1. The Parent (The Coordinate System)
    # This corresponds to the outer GEOGCS[...] block in your screenshot
    print(f"PARENT SYSTEM: {srs.GetName()}")
    print(f" -> Authority Code: {srs.GetAuthorityCode(None)} (The 'Whole Car')")

    # 2. The Child (The Datum - The Anchor)
    # This corresponds to the DATUM[...] block in your screenshot
    datum_name = srs.GetAttrValue("DATUM")
    datum_code = srs.GetAuthorityCode("DATUM")
    
    print(f"\n  -> CHILD COMPONENT (DATUM): {datum_name}")
    print(f"  -> Datum Code: {datum_code}") 
    print("     (Matches the '6326' seen in your assets/image_28e358.png)")

    # 3. The Grandchild (The Ellipsoid - The Shape)
    # This corresponds to the SPHEROID[...] block in your screenshot
    ellipsoid_name = srs.GetAttrValue("SPHEROID")
    ellipsoid_code = srs.GetAuthorityCode("SPHEROID")
    
    print(f"\n    -> GRANDCHILD COMPONENT (ELLIPSOID): {ellipsoid_name}")
    print(f"    -> Ellipsoid Code: {ellipsoid_code}")


def demonstrate_datum_shift():
    """
    Concept 2: The Datum Shift
    Shows how coordinates change when moving from NAD27 (Old US Datum) 
    to WGS84 (Modern GPS Datum).
    """
    print_header("2. THE DATUM SHIFT (Moving the Anchor)")
    print("Goal: Show that the 'same' physical spot has different numbers in different datums.\n")

    # Physical Location: Meades Ranch, Kansas (The anchor point for NAD27)
    # Defined exactly in the NAD27 system
    lat_nad27 = 39.224079
    lon_nad27 = -98.541802

    print(f"Physical Point: Meades Ranch, Kansas")
    print(f"Original Coordinate (NAD27 / EPSG:4267): {lat_nad27}, {lon_nad27}")

    # Create a transformer from NAD27 (EPSG:4267) to WGS84 (EPSG:4326)
    # This mathematically 'moves the anchor' of the coordinate system
    transformer = Transformer.from_crs("EPSG:4267", "EPSG:4326", always_xy=True)

    # Transform (Note: always_xy=True means input is (lon, lat))
    lon_wgs84, lat_wgs84 = transformer.transform(lon_nad27, lat_nad27)

    print(f"Transformed Coordinate (WGS84 / EPSG:4326): {lat_wgs84:.6f}, {lon_wgs84:.6f}")
    
    return (lon_nad27, lat_nad27), (lon_wgs84, lat_wgs84)


def calculate_error(coord_nad27, coord_wgs84):
    """
    Concept 3: The Error Calculation
    Calculates the physical distance between the two coordinate sets 
    if the Datum difference was ignored.
    """
    print_header("3. THE REAL WORLD ERROR")
    print("Goal: Measure the mistake if you confuse the Datums.\n")

    # Unpack coordinates
    lon_old, lat_old = coord_nad27
    lon_new, lat_new = coord_wgs84

    # Use the Geodesic class (acting as a ruler on the WGS84 ellipsoid)
    geod = Geod(ellps='WGS84')

    # Measure distance between the "Old Number" and "New Number"
    # inv returns: azimuth1, azimuth2, distance_in_meters
    _, _, distance_meters = geod.inv(lon_new, lat_new, lon_old, lat_old)

    print(f"If you input the NAD27 coordinates into a WGS84 GPS...")
    print(f"You would be off by: {distance_meters:.2f} meters")
    print(f"({distance_meters * 3.28084:.2f} feet)")
    
    print("\nCONCLUSION: 4326 (The System) defines WHICH Datum (6326) to use.")
    print("If you use the wrong system, you use the wrong anchor!")


def main():
    print("Running Geodesy Concept Script...")
    
    # 1. Run Hierarchy Inspection
    inspect_epsg_hierarchy()
    
    # 2. Run Datum Shift Demonstration
    coords_nad27, coords_wgs84 = demonstrate_datum_shift()
    
    # 3. Calculate Error
    calculate_error(coords_nad27, coords_wgs84)
    
    print_header("SCRIPT COMPLETE")

if __name__ == "__main__":
    main()
