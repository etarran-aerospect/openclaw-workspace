"""
QGIS Python Console Script — Vineyard Leak Detection v1.2

Improvements over v1.1
----------------------
- overwrite-safe output handling for rasters and GeoPackages
- same raster-first leak candidate workflow
- same threshold logic: q20, mean-1sd, mean-2sd

Use this version if previous runs failed because output .gpkg files already existed.
"""

import os
import math
from pathlib import Path

from qgis.core import (
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsField,
)
from qgis.PyQt.QtCore import QVariant

import processing

try:
    import numpy as np
except Exception:
    np = None

try:
    from osgeo import gdal
except Exception:
    gdal = None


# ============================================================================
# INPUTS — EDIT THESE
# ============================================================================

THERMAL_RASTER = r"C:/PATH/TO/full_thermal.tif"
VINE_MASK_RASTER = r"C:/PATH/TO/vine_mask.tif"
VINE_THERMAL_RASTER = r"C:/PATH/TO/vine_only_thermal.tif"
NONVINE_THERMAL_RASTER = r"C:/PATH/TO/nonvine_thermal.tif"

OUTPUT_DIR = r"C:/PATH/TO/leak_detection_outputs"
ADD_OUTPUTS_TO_QGIS = True
MIN_PATCH_PIXELS = 8
MIN_POLYGON_AREA_M2 = 0.25
PRIMARY_METHOD = "q20"


# ============================================================================
# HELPERS
# ============================================================================

def ensure_dir(path_str):
    Path(path_str).mkdir(parents=True, exist_ok=True)


def safe_remove_dataset(path_str):
    p = Path(path_str)
    if p.exists() and p.is_file():
        p.unlink()


def load_raster(path, name=None):
    layer = QgsRasterLayer(path, name or Path(path).stem)
    if not layer.isValid():
        raise RuntimeError(f"Invalid raster: {path}")
    return layer


def add_layer_if_requested(layer):
    if ADD_OUTPUTS_TO_QGIS and layer is not None and layer.isValid():
        QgsProject.instance().addMapLayer(layer)


def raster_array_values(raster_path):
    if gdal is None:
        raise RuntimeError(
            "GDAL Python bindings are not available in this QGIS environment."
        )

    ds = gdal.Open(raster_path)
    if ds is None:
        raise RuntimeError(f"Could not open raster with GDAL: {raster_path}")

    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()
    nodata = band.GetNoDataValue()

    if arr is None:
        raise RuntimeError(f"Could not read raster band as array: {raster_path}")

    if np is None:
        values = []
        rows, cols = arr.shape
        for r in range(rows):
            for c in range(cols):
                v = float(arr[r][c])
                if nodata is not None and v == nodata:
                    continue
                if math.isfinite(v):
                    values.append(v)
        if not values:
            raise RuntimeError(f"No valid raster values found in {raster_path}")
        return values

    flat = arr.astype("float64").ravel()
    if nodata is not None:
        flat = flat[flat != nodata]
    flat = flat[np.isfinite(flat)]
    if flat.size == 0:
        raise RuntimeError(f"No valid raster values found in {raster_path}")
    return flat


def layer_stats(raster_path):
    rl = load_raster(raster_path)
    provider = rl.dataProvider()
    stats = provider.bandStatistics(1)

    vals = raster_array_values(raster_path)

    if np is not None and hasattr(vals, "size"):
        q20 = float(np.quantile(vals, 0.20))
    else:
        vals = sorted(vals)
        q_idx = max(0, min(len(vals) - 1, int(0.2 * (len(vals) - 1))))
        q20 = float(vals[q_idx])

    return {
        "min": float(stats.minimumValue),
        "max": float(stats.maximumValue),
        "mean": float(stats.mean),
        "stddev": float(stats.stdDev),
        "q20": q20,
    }


def threshold_value(method, stats):
    if method == "q20":
        return stats["q20"]
    elif method == "mean_minus_1sd":
        return stats["mean"] - stats["stddev"]
    elif method == "mean_minus_2sd":
        return stats["mean"] - 2.0 * stats["stddev"]
    raise ValueError(f"Unknown threshold method: {method}")


def make_binary_raster(input_raster, threshold, out_path):
    safe_remove_dataset(out_path)
    expr = f'(A <= {threshold})'
    processing.run("gdal:rastercalculator", {
        "INPUT_A": input_raster,
        "BAND_A": 1,
        "FORMULA": expr,
        "NO_DATA": 0,
        "RTYPE": 5,
        "OPTIONS": "",
        "EXTRA": "",
        "OUTPUT": out_path,
    })
    return out_path


def sieve_binary_raster(input_raster, out_path, threshold_pixels=8):
    safe_remove_dataset(out_path)
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
    safe_remove_dataset(out_path)
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
    safe_remove_dataset(out_path)
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
    safe_remove_dataset(out_path)
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

    safe_remove_dataset(out_path)
    processing.run("native:savefeatures", {
        "INPUT": layer,
        "OUTPUT": out_path,
    })
    return out_path


def merge_vectors(inputs, out_path):
    safe_remove_dataset(out_path)
    processing.run("native:mergevectorlayers", {
        "LAYERS": inputs,
        "CRS": None,
        "OUTPUT": out_path,
    })
    return out_path


def sort_layer_by_score(input_vector, out_path):
    safe_remove_dataset(out_path)
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
        thr = threshold_value(method, stats)
        print(f"  Threshold method: {method} | threshold={thr:.4f}")

        binary_path = os.path.join(OUTPUT_DIR, f"{src_name}_{method}_binary.tif")
        sieved_path = os.path.join(OUTPUT_DIR, f"{src_name}_{method}_sieved.tif")
        poly_path = os.path.join(OUTPUT_DIR, f"{src_name}_{method}_poly.gpkg")
        filtered_path = os.path.join(OUTPUT_DIR, f"{src_name}_{method}_poly_filtered.gpkg")
        area_filtered_path = os.path.join(OUTPUT_DIR, f"{src_name}_{method}_poly_area.gpkg")
        enriched_path = os.path.join(OUTPUT_DIR, f"{src_name}_{method}_candidates.gpkg")

        make_binary_raster(raster_path, thr, binary_path)
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

report_path = os.path.join(OUTPUT_DIR, "leak_detection_stats_report.txt")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("Leak Detection v1.2 Stats Report\n")
    f.write("=" * 40 + "\n\n")
    f.write(f"Primary inspection method: {PRIMARY_METHOD}\n\n")
    for src_name, stats in stats_report:
        f.write(f"Source: {src_name}\n")
        for k, v in stats.items():
            f.write(f"  {k}: {v}\n")
        f.write("\n")

print("\nDone.")
print(f"Outputs written to: {OUTPUT_DIR}")
print(f"Merged ranked candidates: {ranked_path}")
print(f"Stats report: {report_path}")
