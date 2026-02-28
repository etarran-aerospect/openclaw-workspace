# AeroSpect Website Finalization Runbook (2026-02-27)

## Objective
Ship a polished, conversion-focused AeroSpect site update with NDVI → Action section, consistent messaging, and launch QA done in one pass.

## Single Prompt for Lovable (paste as-is)

Build a production-ready Next.js (App Router) + TypeScript + Tailwind website update for AeroSpect.

Use this as source/fidelity reference:
- https://www.aerospectinc.com/

Required sections/order:
1) Hero
2) Services
3) Why Choose Us
4) Outcomes / Deliverables
5) NDVI to Action comparison section
6) Final CTA + contact

Design/brand constraints:
- Keep current brand voice: technical, premium, practical
- Keep section flow recognizable (no full redesign)
- Improve spacing/typography/hierarchy subtly
- Fully responsive (mobile/tablet/desktop)
- Accessibility baseline: semantic HTML, keyboard focus states, alt text, heading hierarchy
- SEO baseline metadata + OpenGraph

Implement NDVI section:
- Headline: From Data to Decisions
- Body: NDVI maps are powerful, but often difficult to interpret in the field. We translate complex aerial data into row-level action zones so your team knows exactly where to irrigate, scout for pests/disease, and fix leaks.
- Left: Raw NDVI Map
- Right: Actionable Vineyard Insights
- Caption: Same block, different outcome: from raw vegetation index data to specific field actions.
- Legend:
  - Orange = Irrigation Needed
  - Red = Pest/Disease Pressure
  - Blue = Irrigation Leak
- Side-by-side on desktop, stacked on mobile
- Add toggle: Show Labels / Hide Labels

Component requirements:
- NdviToActionComparison.tsx
- ActionLegend.tsx
- Typed data model from `ndvi-overlay-data-2026-02-26.ts`
- Percentage-based overlay coordinates
- Keyboard accessible interactions

Output requirements:
- Clean reusable components
- README with setup/run/build/deploy
- MIGRATION_NOTES with exact matches vs approximations
- QA checklist with pass/fail for mobile, accessibility, and performance

## Final Homepage Copy Blocks

### Hero
**Headline:** Aerial Intelligence for Smarter Vineyard Decisions  
**Subhead:** We combine thermal and multispectral drone data to identify irrigation stress, pest/disease pressure, and leak anomalies—so your team knows exactly where to act.  
**Primary CTA:** Book a Vineyard Flight  
**Secondary CTA:** See How It Works

### Services
- Thermal Stress Mapping
- Multispectral Vigor Analysis (NDVI/NDRE/GNDVI)
- Irrigation Leak Detection
- Zone-Based Action Reports

### Why Choose Us
- Actionable outputs, not just maps
- Row-level targeting for field crews
- Fast turnaround and repeatable monitoring
- Built for vineyard operations, not generic GIS audiences

### Outcomes / Deliverables
- Priority action zones (irrigate / scout / repair)
- Annotated map outputs for field execution
- Confidence-tagged observations
- Executive summary for managers + practical task list for crews

### Final CTA
**Headline:** Turn this week’s flight into next week’s better decisions.  
**Button:** Request a Demo Deliverable

## NDVI Asset Acceptance Gates (must pass)
- NDVI/RGB same crop/extent/dimensions
- 16:9 preferred (2400x1350; min 1920x1080)
- Image weight target <450KB each
- Overlay points align on landmarks
- Mobile labels readable and non-overlapping

## Launch QA (must pass)
- Lighthouse perf >= 85 mobile
- Keyboard-only navigation works for interactive NDVI controls
- No layout breaks at 390px, 768px, 1024px, 1440px
- CTA buttons visible and consistent across sections
- Contact path tested end-to-end

## Go-Live Definition
Ready when all launch QA checks pass and NDVI section is visually/technically aligned with real assets.
