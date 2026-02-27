# Lovable Prompt Pack — AeroSpect Website (2026-02-26)

## 1) Faithful Conversion Prompt

Recreate my current website https://www.aerospectinc.com/ as a standard coded website (not Google Sites), preserving visual style and layout as closely as possible.

### Objective
Build a production-ready website that matches the current look/feel, branding, section order, and messaging.

### Tech stack
- Next.js (App Router)
- React
- TypeScript
- Tailwind CSS

### Requirements
- Recreate homepage structure and styling with high fidelity:
  - Hero section with current headline style
  - Services grid/cards
  - “Why Choose Us” section
  - Pricing / deliverable-focused section
  - Final CTA/contact area
- Preserve existing copy, links, and call-to-action intent
- Fully responsive (mobile/tablet/desktop)
- SEO + accessibility baseline:
  - semantic HTML
  - metadata/OpenGraph
  - heading hierarchy
  - alt text
  - keyboard focus states
- Clean component architecture and readable code

### Deliverables
1. Full codebase
2. README.md with setup/run/build/deploy instructions
3. MIGRATION_NOTES.md including exact matches, approximations, and recommended improvements

### Important
Do not redesign from scratch. Prioritize fidelity to the current site.

---

## 2) Light Modernization Prompt

Use https://www.aerospectinc.com/ as the source and rebuild it in Next.js + TypeScript + Tailwind, keeping the same brand voice and section flow, but applying a subtle modern polish.

### Keep
- Core messaging and positioning (aerial intelligence for vineyards)
- Existing service categories and CTA intent
- Brand tone (technical + premium + practical)

### Improve slightly
- Typography scale and spacing consistency
- Visual hierarchy and card design polish
- Better section rhythm and whitespace
- Cleaner CTA styling and trust signals
- Performance and accessibility enhancements

### Tech + quality bar
- Next.js App Router, React, TypeScript, Tailwind
- Reusable components
- Responsive, accessible, SEO-ready
- Fast load and clean architecture

### Deliverables
- Production-ready codebase
- README.md
- DESIGN_DIFF.md explaining what changed and why (small, tasteful improvements only)

### Constraints
- Do not over-redesign
- Keep it recognizably the same site

---

## 3) NDVI → Action Side-by-Side Section Prompt

Design and implement a side-by-side comparison visual section for my website that communicates:
“We turn confusing NDVI maps into easy, actionable vineyard decisions.”

### Section Goal
- Left image: NDVI map
- Right image: RGB map of same block with labels:
  - Irrigation Needed
  - Pest/Disease Pressure
  - Irrigation Leak

### UX / Design
- Side-by-side desktop, stacked mobile
- Left title: Raw NDVI Map
- Right title: Actionable Vineyard Insights
- Caption: Same block, different outcome: from raw vegetation index data to specific field actions.
- Visual flow from left → right
- Color legend chips:
  - Orange = Irrigation Needed
  - Red = Pest/Disease Pressure
  - Blue = Irrigation Leak

### Optional interaction
- hover highlight corresponding zones
- Show Labels / Hide Labels toggle

### Copy block
Headline: From Data to Decisions
Body: NDVI maps are powerful, but often difficult to interpret in the field. We translate complex aerial data into row-level action zones so your team knows exactly where to irrigate, scout for pests/disease, and fix leaks.
CTA: See How It Works

### Implementation
- Reusable React + TS + Tailwind component
- Props for images + action labels + coordinates
- Accessible and responsive

---

## 4) NDVI Component (typed schema) Prompt

Use the typed schema from this pack's `ndvi-overlay-data-2026-02-26.ts` and build:
- NdviToActionComparison.tsx
- ActionLegend.tsx
- action color mapping helper
- example usage with placeholder images

Include toggles for labels and row highlights, with keyboard accessibility and percentage-based overlay coordinates.

---

## 5) Combined A/B Prompt (side-by-side + slider)

Build NdviInsightComparison with mode switch:
- mode="sideBySide"
- mode="slider"

Include:
- accessible drag handle in slider mode
- query param mode support (?mode=sideBySide|slider)
- small demo page for A/B testing
- clean TS types + README_NDVI_COMPARISON.md
