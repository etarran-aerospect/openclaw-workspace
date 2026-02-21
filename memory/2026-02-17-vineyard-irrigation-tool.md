# Vineyard Irrigation Insights Tool – Working Notes (2026-02-17)

## High-level vision
- Move away from showing raw NDVI maps.
- Deliver a "Block Irrigation Insights" view per vineyard block/date:
  - Map: vine-only irrigation zones (Deficit / Neutral / Excess / Critical).
  - Metrics: thermal, irrigation, vegetation health percentages.
  - Recommended actions: concise, actionable irrigation guidance per zone.

## Existing capabilities Ethan already built
- Thermal + multispectral fusion and thresholding pipeline.
- Scripts produce:
  - Per-index summaries (NDVI, GNDVI, NDRE, NDWI, SAVI, MSAVI2, VARI, CIgreen, CIrededge) with min/max/mean/std.
  - Thermal orthomosaic analysis JSON/TXT with:
    - Thermal stress metrics (extreme heat %, heat stress %, optimal %, cool %).
    - Irrigation analysis metrics (water_stress %, irrigation_needed %, uniform %, variable %, efficiency score).
    - Vegetation health metrics (healthy %, stressed %, severely_stressed %, anomalies %).
    - Anomaly detection stats and thermal zones (5 temperature bands with area %, mean temp, etc.).
  - Auto-generated textual recommendations sections (Thermal Stress, Irrigation, Irrigation Efficiency).
- Data lives primarily on external drive D: (WSL: /mnt/d), with vineyard projects like Indian_Springs, Sunscreen trials, etc.

## Indian Springs / NDVI work (today)
- QGIS project "Indian Springs" has:
  - RGB orthomosaic.
  - NDVI raster with range approx 0.075–0.94; vines ~0.5–0.9.
  - NDVI-based zones layer (`NDVI_Zones`) created via classification & polygonization.
  - `NDVI_Zones` has fields:
    - `zone_type` (Low / Medium / High vigor).
    - `action` (text describing scouting/irrigation/canopy actions).
- Lessons learned:
  - Polygonizing full-res NDVI produced ~1.1M features (too heavy → crashes & slow qgis2web).
  - Need to dissolve by class and/or resample NDVI to coarser resolution before polygonize.
  - For demo, dissolve zones by `zone_type` and hide "All other"/sliver categories.
  - Bare soil/roads should be masked out (vine-only NDVI) so vigor map is for vines, not everything.

## Thermal orthomosaic analysis example (2025-10-17)
- File: `thermal_ortho.tif` (EPSG:4326) with shape (11637, 8119).
- Temperature stats: mean ~29.9°C, median ~27°C, Q25 ~24.4°C, Q75 ~33.3°C, min ~13.5°C, max ~65.5°C.
- Thermal stress (area fractions):
  - Extreme heat: ~14% of area.
  - Heat stress: ~7%.
  - Optimal: ~66%.
  - Cool: ~0%.
- Irrigation analysis:
  - Water-stress area: ~28%.
  - Irrigation-needed area: ~16.6%.
  - Irrigation-zonable area: ~10%.
  - Uniform areas: ~25%.
  - Variable areas: ~25%.
  - Irrigation efficiency score: ~25%.
- Vegetation health:
  - Healthy: ~56%.
  - Stressed: ~27.6%.
  - Severely stressed: ~6.5%.
  - Anomalies: ~0.5%.
- Thermal zones (5 bands) with meaningful temperature ranges and area % already computed.
- Auto-generated recommendations sections exist (Thermal Stress / Irrigation / Irrigation Efficiency).

## Product direction we converged on
- Product focus: "Irrigation Insights" rather than "NDVI maps".
- For each block/date, deliver:
  1. **Map**
     - Vines-only irrigation zones (Deficit / Neutral / Excess / Critical) derived from fused thermal + NDVI.
     - Popups with `zone_type` + `irrigation_action`.
  2. **Metrics card**
     - Pull from existing JSON/CSV (thermal, irrigation, veg health).
     - Show key percentages and simple scores.
  3. **Recommendations**
     - 3–5 bullets mapping metrics to irrigation moves (where to increase/hold/reduce; where to scout).
- Demo/UX target:
  - Use qgis2web export as v0 map (RGB + zones + popups).
  - Use block report (from TXT/JSON) as metrics card.
  - Present on Zoom + in person as a vineyard management screen, not a GIS project.

## Planned rule framework (to formalize later)
- Combine NDVI vigor classes with thermal classes into zone types:
  - Low/Med NDVI + Hot/Extreme thermal → **Deficit** (increase irrigation, check system).
  - Medium NDVI + Optimal thermal → **Neutral** (maintain current schedule).
  - High NDVI + Cool/Normal thermal → **Excess** (reduce irrigation slightly; more canopy work).
  - Any NDVI + Very hot + anomaly → **Critical** (field check ASAP).
- These rules will drive both:
  - Pixel-to-zone classification for the map.
  - Text for `irrigation_action` fields and summary recommendations.

## Immediate next steps (when Ethan returns)
1. Choose one vineyard block + date (likely the thermal_ortho example) as the "hero" case.
2. For that block:
   - Use existing fusion outputs to produce a simplified irrigation zones layer (few polygons, dissolved by zone_type).
   - Attach `zone_type` + `irrigation_action` matching the rule framework.
   - Export a qgis2web map (RGB + zones + popups).
   - Build a 1-page Block Irrigation Insights summary using the metrics & recommendations already in the TXT/JSON.
3. Use this hero block as the core demo on Zoom and in person.
4. Later: wrap the fusion + zoning pipeline into a repeatable CLI and a simple web UI.

## Meta
- Ethan mentioned also working on this on another machine with another Claude agent that could write directly to the external drive. That prior work + these notes should be reconciled later.
- This file is meant to prevent "starting over" next time: it summarizes the current engine capabilities and the product direction (irrigation-focused block insights built on thermal+multispectral fusion).
