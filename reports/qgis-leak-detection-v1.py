"""
QGIS Python Console Script — Vineyard Leak Detection v1

Purpose
-------
Build a first-pass leak detection workflow using rasters you already have:
- full thermal ortho
- vine mask raster
- vine-only thermal raster
- non-vine thermal raster

This version is raster-first and does NOT require row centerlines.
It identifies cool anomaly zones using three threshold methods:
- lower quintile (recommended primary method from the paper)
- mean - 1 standard deviation
- mean - 2 standard deviations

Outputs
-------
For each source raster (whole / vine / nonvine), this script creates:
- thresholded anomaly rasters
- cleaned binary rasters
- polygonized candidate leak layers

It also creates a merged candidate polygon layer with:
- source raster name
- threshold method
- raster stats used
- polygon area
- a simple confidence score

How to use
----------
1. Open QGIS.
2. Load this script into the Python console editor.
3. Edit the INPUTS and OUTPUTS section below.
4. Run the whole script.

Notes
-----
- Assumes rasters are already aligned / same CRS / same pixel grid, or close enough.
- Uses GDAL / QGIS Processing tools available in standard QGIS installs.
- Confidence scoring is intentionally simple in v1.
- This script is designed to be understandable and modifiable, not minified.
"""

import os
import math
from pathlib import Path

from qgis.core import (
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsVectorFileWriter,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QVariant

import processing


# ============================================================================
# INPUTS — EDIT THESE
# ============================================================================

THERMAL_RASTER = r"C:/PATH/TO/full_thermal.tif"
VINE_MASK_RASTER = r"C:/PATH/TO/vine_mask.tif"          # optional for later use / QA
VINE_THERMAL_RASTER = r"C:/PATH/TO/vine_only_thermal.tif"
NONVINE_THERMAL_RASTER = r"C:/PATH/TO/nonvine_thermal.tif"

OUTPUT_DIR = r"C:/PATH/TO/leak_detection_outputs"
ADD_OUTPUTS_TO_QGIS = True
MIN_PATCH_PIXELS = 8          # sieve threshold to remove tiny speckles
MIN_POLYGON_AREA_M2 = 0.25    # drop tiny polygons after polygonizing
PRIMARY_METHOD = "q20"       # one of: q20, mean_minus_1sd, mean_minus_2sd


# ============================================================================
# HELPERS
# ============================================================================

def ensure_dir(path_str):
    Path(path_str).mkdir(parents=True, exist_ok=True)


def load_raster(path, name=None):
    layer = QgsRasterLayer(path, name or Path(path).stem)
    if not layer.isValid():
        raise RuntimeError(f"Invalid raster: {path}")
    return layer


def add_layer_if_requested(layer):
    if ADD_OUTPUTS_TO_QGIS and layer is not None and layer.isValid():
        QgsProject.instance().addMapLayer(layer)


def layer_stats(raster_path):
    """
    Returns dict with min, max, mean, stddev, q20 from raster values.
    Uses native raster layer statistics + raster-to-points export for q20 via numpy-free route.
    For v1, q20 is derived via raster pixel extraction to CSV-friendly points using GDAL/QGIS.
    """
    rl = load_raster(raster_path)
    provider = rl.dataProvider()
    stats = provider.bandStatistics(1)

    # Extract raster pixel values to points for quantile estimate.
    # This is heavier than pure numpy, but more portable in QGIS console environments.
    pts_path = os.path.join(OUTPUT_DIR, f"_tmp_{Path(raster_path).stem}_points.gpkg")
    pts_layer_name = f"tmp_pts_{Path(raster_path).stem}"

    processing.run("native:pixelstopoints", {
        "INPUT_RASTER": raster_path,
        "RASTER_BAND": 1,
        "FIELD_NAME": "val",
        "OUTPUT": f"{pts_path}|layername={pts_layer_name}",
    })

    pts = QgsVectorLayer(f"{pts_path}|layername={pts_layer_name}", pts_layer_name, "ogr")
    if not pts.isValid():
        raise RuntimeError(f"Could not create point layer for quantile: {raster_path}")

    values = []
    for f in pts.getFeatures():
        v = f["val"]
        if v is None:
            continue
        try:
            fv = float(v)
            if math.isfinite(fv):
                values.append(fv)
        except Exception:
            pass

    if not values:
        raise RuntimeError(f"No valid raster values found in {raster_path}")

    values.sort()
    q_idx = max(0, min(len(values) - 1, int(0.2 * (len(values) - 1))))
    q20 = values[q_idx]

    return {
        "min": float(stats.minimumValue),
        "max": float(stats.maximumValue),
        "mean": float(stats.mean),
        "stddev": float(stats.stdDev),
        "q20": float(q20),
    }


def raster_threshold_expression(method, stats):
    if method == "q20":
        threshold = stats["q20"]
        return f'("A@1" <= {threshold})'
    elif method == "mean_minus_1sd":
        threshold = stats["mean"] - stats["stddev"]
        return f'("A@1" <= {threshold})'
    elif method == "mean_minus_2sd":
        threshold = stats["mean"] - 2.0 * stats["stddev"]
        return f'("A@1" <= {threshold})'
    else:
        raise ValueError(f"Unknown threshold method: {method}")


def threshold_value(method, stats):
    if method == "q20":
        return stats["q20"]
    elif method == "mean_minus_1sd":
        return stats["mean"] - stats["stddev"]
    elif method == "mean_minus_2sd":
        return stats["mean"] - 2.0 * stats["stddev"]
    raise ValueError(method)


def make_binary_raster(input_raster, method, stats, out_path):
    expr = raster_threshold_expression(method, stats)
    processing.run("gdal:rastercalculator", {
        "INPUT_A": input_raster,
        "BAND_A": 1,
        "FORMULA": expr,
        "NO_DATA": 0,
        "RTYPE": 5,  # Float32 works fine for simple binary outputs
        "OPTIONS": "",
        "EXTRA": "",
        "OUTPUT": out_path,
    })
    return out_path


def sieve_binary_raster(input_raster, out_path, threshold_pixels=8):
    processing.run("gdal:sieve", {
        "INPUT": input_raster,
        "THRESHOLD": threshold_pixels,
        "EIGHT_CONNECTEDNESS": False,
        "NO_MASK": True,
        "MASK_LAYER": None,
        "EXTRA": "",
        "OUTPUT": out_path,
    })
    return out_path


def polygonize_raster(input_raster, out_path, field_name="value"):
    processing.run("gdal:polygonize", {
        "INPUT": input_raster,
        "BAND": 1,
        "FIELD": field_name,
        "EIGHT_CONNECTEDNESS": False,
        "EXTRA": "",
        "OUTPUT": out_path,
    })
    return out_path


def filter_value_one_and_add_area(input_vector, out_path):
    # Keep only polygons where raster value == 1 and compute area.
    processing.run("native:extractbyexpression", {
        "INPUT": input_vector,
        "EXPRESSION": '"value" = 1',
        "OUTPUT": out_path,
    })

    processing.run("native:fieldcalculator", {
        "INPUT": out_path,
        "FIELD_NAME": "area_m2",
        "FIELD_TYPE": 0,
        "FIELD_LENGTH": 20,
        "FIELD_PRECISION": 3,
        "FORMULA": "$area",
        "OUTPUT": out_path,
    })
    return out_path


def filter_min_area(input_vector, min_area, out_path):
    processing.run("native:extractbyexpression", {
        "INPUT": input_vector,
        "EXPRESSION": f'"area_m2" >= {min_area}',
        "OUTPUT": out_path,
    })
    return out_path


def add_metadata_fields(input_vector, source_name, method, stats, out_path):
    layer = QgsVectorLayer(input_vector, Path(input_vector).stem, "ogr")
    if not layer.isValid():
        raise RuntimeError(f"Invalid vector for metadata add: {input_vector}")

    fields_to_add = [
        ("src_name", QVariant.String, source_name),
        ("method", QVariant.String, method),
        ("thr_val", QVariant.Double, threshold_value(method, stats)),
        ("mean_val", QVariant.Double, stats["mean"]),
        ("stddev", QVariant.Double, stats["stddev"]),
        ("q20", QVariant.Double, stats["q20"]),
    ]

    provider = layer.dataProvider()
    provider.addAttributes([QgsField(n, t) for n, t, _ in fields_to_add])
    layer.updateFields()

    idx = {f.name(): i for i, f in enumerate(layer.fields())}
    layer.startEditing()
    for feat in layer.getFeatures():
        for name, _type, value in fields_to_add:
            feat[idx[name]] = value
        layer.updateFeature(feat)
    layer.commitChanges()

    # confidence score (simple v1 logic)
    # stronger if q20, then mean-1sd, then mean-2sd; plus area bonus
    provider = layer.dataProvider()
    provider.addAttributes([QgsField("score", QVariant.Int)])
    layer.updateFields()
    idx = {f.name(): i for i, f in enumerate(layer.fields())}

    layer.startEditing()
    for feat in layer.getFeatures():
        area = float(feat["area_m2"] or 0)
        score = 1
        if method == "q20":
            score += 3
        elif method == "mean_minus_1sd":
            score += 2
        elif method == "mean_minus_2sd":
            score += 1

        if area > 1:
            score += 1
        if area > 5:
            score += 1
        if area > 20:
            score += 1

        feat[idx["score"]] = score
        layer.updateFeature(feat)
    layer.commitChanges()

    QgsVectorFileWriter.writeAsVectorFormat(layer, out_path, "UTF-8", layer.crs(), "GPKG")
    return out_path


def merge_vectors(inputs, out_path):
    processing.run("native:mergevectorlayers", {
        "LAYERS": inputs,
        "CRS": None,
        "OUTPUT": out_path,
    })
    return out_path


def sort_layer_by_score(input_vector, out_path):
    processing.run("native:orderbyexpression", {
        "INPUT": input_vector,
        "EXPRESSION": '"score" * -1',
        "ASCENDING": True,
        "NULLS_FIRST": False,
        "OUTPUT": out_path,
    })
    return out_path


# ============================================================================
# MAIN
# ============================================================================

ensure_dir(OUTPUT_DIR)

inputs = {
    "whole": THERMAL_RASTER,
    "vine": VINE_THERMAL_RASTER,
    "nonvine": NONVINE_THERMAL_RASTER,
}

methods = ["q20", "mean_minus_1sd", "mean_minus_2sd"]
all_vector_outputs = []
stats_report = []

for src_name, raster_path in inputs.items():
    print(f"\n--- Processing source: {src_name} ---")
    stats = layer_stats(raster_path)
    stats_report.append((src_name, stats))
    print(f"Stats for {src_name}: {stats}")

    for method in methods:
        print(f"  Threshold method: {method}")

        binary_path = os.path.join(OUTPUT_DIR, f"{src_name}_{method}_binary.tif")
        sieved_path = os.path.join(OUTPUT_DIR, f"{src_name}_{method}_sieved.tif")
        poly_path = os.path.join(OUTPUT_DIR, f"{src_name}_{method}_poly.gpkg")
        filtered_path = os.path.join(OUTPUT_DIR, f"{src_name}_{method}_poly_filtered.gpkg")
        area_filtered_path = os.path.join(OUTPUT_DIR, f"{src_name}_{method}_poly_area.gpkg")
        enriched_path = os.path.join(OUTPUT_DIR, f"{src_name}_{method}_candidates.gpkg")

        make_binary_raster(raster_path, method, stats, binary_path)
        sieve_binary_raster(binary_path, sieved_path, MIN_PATCH_PIXELS)
        polygonize_raster(sieved_path, poly_path, "value")
        filter_value_one_and_add_area(poly_path, filtered_path)
        filter_min_area(filtered_path, MIN_POLYGON_AREA_M2, area_filtered_path)
        add_metadata_fields(area_filtered_path, src_name, method, stats, enriched_path)

        all_vector_outputs.append(enriched_path)
        add_layer_if_requested(QgsRasterLayer(binary_path, Path(binary_path).stem))
        add_layer_if_requested(QgsRasterLayer(sieved_path, Path(sieved_path).stem))
        add_layer_if_requested(QgsVectorLayer(enriched_path, Path(enriched_path).stem, "ogr"))

merged_path = os.path.join(OUTPUT_DIR, "merged_leak_candidates.gpkg")
ranked_path = os.path.join(OUTPUT_DIR, "merged_leak_candidates_ranked.gpkg")

merge_vectors(all_vector_outputs, merged_path)
sort_layer_by_score(merged_path, ranked_path)

merged_layer = QgsVectorLayer(ranked_path, "merged_leak_candidates_ranked", "ogr")
add_layer_if_requested(merged_layer)

# Write stats report text file
report_path = os.path.join(OUTPUT_DIR, "leak_detection_stats_report.txt")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("Leak Detection v1 Stats Report\n")
    f.write("=" * 40 + "\n\n")
    for src_name, stats in stats_report:
        f.write(f"Source: {src_name}\n")
        for k, v in stats.items():
            f.write(f"  {k}: {v}\n")
        f.write("\n")

print("\nDone.")
print(f"Outputs written to: {OUTPUT_DIR}")
print(f"Merged ranked candidates: {ranked_path}")
print(f"Stats report: {report_path}")
print(f"Recommended primary method to inspect first: {PRIMARY_METHOD}")
