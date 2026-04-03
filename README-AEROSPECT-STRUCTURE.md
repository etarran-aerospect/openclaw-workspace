# AeroSpect Site Structure

## Production (IONOS)
- **`aerospect-deployed-live/`** — PRODUCTION BASELINE
  - Built dist from port 8000
  - Synced to git (protected)
  - Deployed to aerospectinc.com

## BVLOS (Vercel)
- Separate app at bvlos.aerospectinc.com
- Linked from homepage, not bundled
- Leave as-is on Vercel

## Drafts & Archives
- **`aerospect-drafts/archive/`** — Old versions (for reference only)
  - aerospect-old (5173 candidate)
  - aerospect-deployed-site-old (5174 candidate)
  - aerospect-simplified-old
  - aerospect-website-old
  - aerospect-website-new-manus-old

## Workflow
1. Edit/test in `aerospect-deployed-live/`
2. Build locally
3. Deploy to IONOS
4. Commit to git
