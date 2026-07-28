# Site 23 reader/trust patch plan

Date: 2026-07-29 KST

## Verified defects

1. The AdSense Auto Ads loader appears on Home and all six trust/legal routes: About, Contact, Privacy Policy, Terms, Methodology, and Disclosures.
2. At a 390px viewport, the primary navigation wraps the single `Disclosures` link onto its own row before article content.
3. The published breed-guide corpus repeats a generic `Practical next step` section in 101 files. This is an editorial originality risk, not a safe sitewide template edit.

## Scoped repair

- Remove only the common AdSense loader from Home and the six trust/legal HTML documents.
- Keep the loader on Blog, individual articles, Cost Data, and Outdoor Risk content routes.
- Adjust only the mobile shared navigation to retain four reader-navigation links in one row; About, Contact, Privacy, Terms, and Disclosures remain available in the footer.
- Do not modify article bodies, titles, source links, schedules, analytics, ads.txt, sitemap URLs, or search-console state.

## Validation

- Confirm local and public route H1/canonical/status behavior.
- Confirm zero loader on Home/trust routes and one on Blog/article.
- Capture final 1440px Home and 390px article views with no first-party console errors.
- Run static HTML/CSS integrity checks, inspect the focused diff, then deploy through the existing Git-connected Vercel flow and repeat the public audit.

## External decision

Keep AdSense submission/resubmission and Google indexing requests on HOLD. The recurring article template needs representative source/originality review before any external action.
