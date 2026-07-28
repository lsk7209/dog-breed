# Handoff

## Site 23 `dogbreedcost.com` release pending (2026-07-29 03:25 KST)

- User goal: improve the managed site fleet for reader experience, AdSense review readiness, and Google-facing content quality without claiming external approval or ranking.
- Exact state: the small static patch is rebased on the current remote `main` and passes local validation. It is committed locally but not yet pushed, so no Vercel/public-site state has changed.
- Current evidence: the parent dashboard snapshot generated `2026-07-28T17:57:39.607Z` reports 82 active users, 2 clicks, 202 impressions, 0.99% CTR, and position 14.04. Public collector states are healthy.
- Stack: static HTML deployed through the Git-connected Vercel project in `.vercel/project.json`; the dashboard's WordPress label is stale. This site is not an API/DB collection site in the current Vercel API-data inventory.
- Applied scope: removed the common AdSense loader from Home and the six trust/legal routes; retained it on Blog and individual article routes; constrained the 390px primary navigation to four reader-navigation links, with trust/legal links retained in the footer. Article bodies, titles, URLs, source links, schedules, and analytics remain unchanged.
- Fresh local validation: all nine sampled routes have one H1 and one canonical; Home/trust routes have no loader, Blog/representative article retain one; `git diff --check` passes; the mobile navigation rule is present. Final release still requires Git push, Vercel production completion, and a public repeat audit.
- External boundary: no AdSense submission/resubmission or Google indexing request. Technical readiness is not AdSense approval or ranking evidence.
- Single next step: push the rebased commit, confirm the Git-connected Vercel production deployment, then repeat public-route and responsive-browser checks.
