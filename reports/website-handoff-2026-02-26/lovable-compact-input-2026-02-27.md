# Lovable Compact Input (copy/paste)

Rebuild/update https://www.aerospectinc.com/ in Next.js (App Router) + TypeScript + Tailwind with high fidelity (no full redesign), subtle polish only.

Sections in order:
1) Hero
2) Services
3) Why Choose Us
4) Outcomes/Deliverables
5) NDVI→Action comparison
6) Final CTA + Contact

Brand/tone: technical, premium, practical. Fully responsive + accessible + SEO baseline.

Hero copy:
- Headline: Aerial Intelligence for Smarter Vineyard Decisions
- Subhead: We combine thermal and multispectral drone data to identify irrigation stress, pest/disease pressure, and leak anomalies—so your team knows exactly where to act.
- CTAs: Book a Vineyard Flight / See How It Works

NDVI section requirements:
- Headline: From Data to Decisions
- Left title: Raw NDVI Map
- Right title: Actionable Vineyard Insights
- Caption: Same block, different outcome: from raw vegetation index data to specific field actions.
- Legend:
  - Orange = Irrigation Needed
  - Red = Pest/Disease Pressure
  - Blue = Irrigation Leak
- Desktop side-by-side, mobile stacked
- Toggle: Show Labels / Hide Labels
- Build reusable components:
  - NdviToActionComparison.tsx
  - ActionLegend.tsx
- Use typed overlay data schema from ndvi-overlay-data-2026-02-26.ts with percentage-based coordinates

Deliverables:
- Production-ready code
- README (setup/run/build/deploy)
- MIGRATION_NOTES (exact matches vs approximations)
- QA checklist result
