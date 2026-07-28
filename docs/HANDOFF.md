# Handoff

## Site 23 `dogbreedcost.com` release pending (2026-07-29 03:25 KST)

- User goal: improve the managed site fleet for reader experience, AdSense review readiness, and Google-facing content quality without claiming external approval or ranking.
- Exact state: the small static patch is rebased on the current remote `main` and passes local validation. It is committed locally but not yet pushed, so no Vercel/public-site state has changed.
- Current evidence: the parent dashboard snapshot generated `2026-07-28T17:57:39.607Z` reports 82 active users, 2 clicks, 202 impressions, 0.99% CTR, and position 14.04. Public collector states are healthy.
- Stack: static HTML deployed through the Git-connected Vercel project in `.vercel/project.json`; the dashboard's WordPress label is stale. This site is not an API/DB collection site in the current Vercel API-data inventory.
- Applied scope: removed the common AdSense loader from Home and the six trust/legal routes; retained it on Blog and individual article routes; constrained the 390px primary navigation to four reader-navigation links, with trust/legal links retained in the footer. Article bodies, titles, URLs, source links, schedules, and analytics remain unchanged.
- Fresh release evidence: `e4f282d` is pushed and Vercel production deployment `dpl_BQB8V4xFw1qqhQwxNsjGqxbpzsZq` is Ready. Public routes confirm zero loaders on Home/trust pages and one on Blog/representative article. Mobile browser review has no first-party error, but exposed a missing `/favicon.ico` fallback; the current small follow-up adds a shared SVG redirect before final verification.
- External boundary: no AdSense submission/resubmission or Google indexing request. Technical readiness is not AdSense approval or ranking evidence.
- Single next step: deploy and verify the favicon redirect, then record final public browser and crawl evidence.
