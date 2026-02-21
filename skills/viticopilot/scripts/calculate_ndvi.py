#!/usr/bin/env python3
"""Calculate NDVI from a multispectral raster.

Usage
-----
    calculate_ndvi <input_file_path> <red_band_index> <nir_band_index>

Notes
-----
- Band indices are 1-based (GDAL/rasterio convention).
- Output is written as `<input_file_path>_NDVI.tif` in the same directory.
- Original raster is never modified.
"""

import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import Affine


def calculate_ndvi(input_path: Path, red_band: int, nir_band: int) -> Path:
    output_path = input_path.with_name(input_path.stem + "_NDVI.tif")

    with rasterio.open(input_path) as src:
        red = src.read(red_band).astype("float32")
        nir = src.read(nir_band).astype("float32")

        # Avoid division by zero
        denom = nir + red
        # Where denom == 0, set to nan to avoid inf
        denom[denom == 0] = np.nan

        ndvi = (nir - red) / denom

        profile = src.profile
        profile.update(
            dtype="float32",
            count=1,
            nodata=np.nan,
        )

        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(ndvi, 1)

    return output_path


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("Usage: calculate_ndvi <input_file_path> <red_band_index> <nir_band_index>")
        return 1

    input_file = Path(argv[1]).expanduser().resolve()
    red_band = int(argv[2])
    nir_band = int(argv[3])

    if not input_file.exists():
        print(f"Input file does not exist: {input_file}")
        return 1

    print(f"Computing NDVI from {input_file} (red band={red_band}, NIR band={nir_band}) …")
    print("Formula: NDVI = (NIR - Red) / (NIR + Red)")

    out = calculate_ndvi(input_file, red_band, nir_band)
    print(f"NDVI written to: {out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv))
