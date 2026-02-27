# Asset Handoff Checklist — NDVI/RGB Comparison

## Export specs
- Preferred size: 2400 × 1350 px (16:9)
- Minimum: 1920 × 1080 px
- NDVI + RGB must be identical dimensions/crop

## Format
- Production: WebP (quality 80–88)
- Archive originals: TIFF/PNG

## Naming
- vineyard-block-01-ndvi.webp
- vineyard-block-01-rgb.webp
- vineyard-block-01-overlays.json (optional)

## Paths
- /public/images/insights/vineyard-block-01-ndvi.webp
- /public/images/insights/vineyard-block-01-rgb.webp
- /data/overlays/vineyard-block-01.json

## Alignment (critical)
- Same CRS alignment before export
- Same extent + orientation + pixel dimensions
- Verify overlay anchor points on landmarks

## Readability
- NDVI: increase contrast enough to show vigor zones
- RGB: keep natural color and visible vine rows

## Mobile
- Short labels
- Tap for details/tooltip

## Performance
- Target per image < 450KB (hard cap < 700KB)
- Lazy-load below fold

## QA
- Overlays align on RGB
- Labels readable on mobile
- Slider smooth on touch
- Focus states visible
- Contrast accessible
