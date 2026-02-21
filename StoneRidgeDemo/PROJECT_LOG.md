# VineGuard / Stone Ridge Vineyard / Block A02 — Project Log

Date: 2026-02-09
Owner: Ethan

## Goal
Build VineGuard: a weekly, high-confidence, actionable vineyard health report + simple app UI.
- Primary UI should be **clean RGB** with **numbered pins**.
- Pins answer: **where the problem is, what it is, what to do**.
- NDVI/Thermal/other indices are **optional inspection layers**, not the main output.
- Emphasis: **high-confidence alerts**, avoid alert fatigue.

## Data / Paths
- Base data root (Windows): `H:\Barrelli_Creek_A02_CAB_SAUV_23.5_AC`
- WSL path: `/mnt/h/Barrelli_Creek_A02_CAB_SAUV_23.5_AC`
- Block boundary: `BLOCK_A02_CAB_SAUV_23.5_AC.shp` (had null geometries; we built a union cutline in GPKG)
- Selected dates for temporal demo:
  - 2025-06-16
  - 2025-07-03
  - 2025-08-04
  - 2025-09-02 (diurnal; standardize to **1pm** for demo)

## Key design decisions
- QGIS version: 3.40.10
- Use **block-relative** normalization across dates/locations.
- “Balanced” fusion thresholding for candidate areas:
  - NDVI in **bottom 20th percentile** AND Thermal in **top 80th percentile** (computed per block per flight)
- Output v1 is a static HTML report (no tileserver): map image + pins + side panel.
- Map UI layout adjusted for iPad: left column map + selected pin panel; right column executive summary + action items.

## Deliverables created (Windows-friendly)
Main demo directory:
- `C:\Users\seanc\Documents\StoneRidgeDemo\`

### Single-date report (latest)
- `C:\Users\seanc\Documents\StoneRidgeDemo\run_2025-08-04_A02_v2_balanced\report.html`

### Temporal viewer
- `C:\Users\seanc\Documents\StoneRidgeDemo\temporal_A02\index.html`
  - Each date has its own folder with `report.html`.
  - 2025-09-02 uses 1pm thermal but dropdown label shows just “2025-09-02”.

Run local web server (required; file:// blocks fetch):
- `cd C:\Users\seanc\Documents\StoneRidgeDemo\temporal_A02`
- `python3 -m http.server 8011`
- Open: `http://localhost:8011/index.html`

## UI/UX work completed
- Pins numbered **1–8** and rendered inside colored circles.
- Legend with severity colors.
- Clicking same pin again or map background clears selection.
- NDVI uses RdYlGn-like color ramp with **transparent NoData**.
- Thermal uses inferno-style ramp.
- Removed grid overlays from main flow after user feedback (grid not useful for manager UX).
- For temporal reports: rotated map content **-21°**, then tuned to reduce cropping:
  - `translateY(-6%) rotate(-21deg) scale(0.90)`
- Fixed regression where `.pin { position:absolute }` went missing (pins disappeared).

## Temporal / grid work (internal + support)
Even though grid overlays are no longer central to UX, we built the plumbing for temporal metrics:

### A02 10m grid (block-wide)
- `C:\Users\seanc\Documents\StoneRidgeDemo\temporal_A02\focus_area\grid10m_block.gpkg`
  - 1067 cells
  - `focus_area` flag set for cells intersecting FID 17 polygon (19 cells)

### Time series CSV for grid
- `C:\Users\seanc\Documents\StoneRidgeDemo\temporal_A02\focus_area\a02_grid10m_timeseries.csv`
  - per date per cell: ndvi_mean, thermal_mean, ndvi_percentile, thermal_percentile, focus_area

## Treatment polygons (used only to choose a focus area)
- `H:\...\2025_A02_Treatments_All\2025_A02_Treatments_All.shp`
- User specified “Feature ID 17” as drastic-change focus.
  - Extracted and gridded in `...\temporal_A02\treatment_grid\`.
- Note: this **should not** be labeled as treatment in client-facing UI.

## Scripts created/modified (WSL workspace)
Workspace root: `/home/seanc/.openclaw/workspace/stone_ridge_demo`

Key scripts:
- `build_demo_a02_2025-08-04.py` — report generator (pins, thumbnails, HTML)
- `make_percentile_mask.py` — build mask from NDVI/thermal percentiles (balanced p20/p80)
- `build_temporal_a02.sh` — builds per-date runs into `Documents/StoneRidgeDemo/temporal_A02`
- `make_grid_clip.py` — create clipped polygon grid (OGR-only)
- `tag_focus_area.py` — tag grid cells intersecting focus polygon
- `zonal_timeseries.py` — zonal means + block-relative percentile ranks per cell per date
- Patch scripts:
  - `patch_report_add_overlays.py` (later de-emphasized)
  - `patch_remove_grid_overlays.py`
  - `patch_rotate_map.py`, `patch_rotate_tune.py`, `patch_fix_pin_css_and_tune.py`

Color ramps:
- `ramps/ndvi_rdy_lgn_0-255.txt` (NDVI, transparent 0)
- `ramps/thermal_inferno_0-255.txt`
- `ramps/percentile_rdy_lgn_0-100.txt` (transparent 0)
- `ramps/percentile_inferno_0-100.txt`

## Known issues / TODO
- Rotation/cropping still may need small tuning per iPad viewport.
- Candidate/pin generation is still simplistic (area-based selection); should evolve to:
  - persistence gate across flights
  - stronger anomaly qualification
  - explicit “Alert vs Investigate” tiers
- UI: rename layer buttons to “Inspect” language (RGB default).
- Temporal story: “weekly vs monthly days gained” simulation not implemented yet.

## What to do tomorrow (suggested next steps)
1) Lock a pin taxonomy + actions text (irrigation deficit vs heat stress vs investigate).
2) Add alert qualification (persistence/extremeness/area/edge buffer/data quality).
3) Add temporal change summaries (focus area vs rest of block) without showing a grid overlay.
4) Start multi-block selector (if desired) using same folder structure.
