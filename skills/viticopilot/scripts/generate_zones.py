#!/usr/bin/env python3
"""Generate simple management zones from a single-band raster.

Usage
-----
    generate_zones <input_raster_path> <threshold_value>

This script:
- Reads a single-band raster (e.g. NDVI or thermal index).
- Classifies pixels into two classes based on a threshold:
    0 = below threshold (e.g. low vigor / high stress)
    1 = above threshold (e.g. high vigor / low stress)
- Polygonizes the classified raster into vector zones.
- Writes output as `<input_raster_path>_Zones.geojson`.

This is intentionally simple for demo / prescription prototyping.
"""

import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape


def generate_zones(input_path: Path, threshold: float) -> Path:
    output_path = input_path.with_name(input_path.stem + "_Zones.geojson")

    with rasterio.open(input_path) as src:
        data = src.read(1).astype("float32")
        transform = src.transform

    # Simple binary classification
    classified = np.zeros_like(data, dtype="uint8")
    classified[data > threshold] = 1

    # Polygonize
    geometries = []
    values = []

    for geom, value in shapes(classified, mask=None, transform=transform):
        # Skip nodata or empty polygons
        if value is None:
            continue
        geometries.append(shape(geom))
        values.append(int(value))

    if not geometries:
        raise RuntimeError("No geometries produced from classification; check threshold and input raster.")

    gdf = gpd.GeoDataFrame({"zone_class": values}, geometry=geometries, crs="EPSG:4326")

    # If the input has a different CRS, you can adapt this to read src.crs and reproject.

    # Add simple descriptive fields for use in QGIS/qgis2web popups
    # 0 -> low, 1 -> high (you can reinterpret depending on index)
    gdf["zone_type"] = gdf["zone_class"].map({0: "Low", 1: "High"})

    gdf.to_file(output_path, driver="GeoJSON")
    return output_path


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: generate_zones <input_raster_path> <threshold_value>")
        return 1

    input_file = Path(argv[1]).expanduser().resolve()
    threshold = float(argv[2])

    if not input_file.exists():
        print(f"Input file does not exist: {input_file}")
        return 1

    print(f"Generating management zones from {input_file} using threshold {threshold} …")
    print("Classification: value <= threshold -> 0 (Low), value > threshold -> 1 (High)")

    out = generate_zones(input_file, threshold)
    print(f"Zones written to: {out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv))
