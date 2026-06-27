# BreedWise Optimization Status

Checked: 2026-06-27 KST

## Implemented

- Site/content persona system added in `docs/personas.md`.
- `/blog/` archive uses a responsive card grid with clearer scan paths and a methodology CTA.
- Article layout supports sticky table of contents on desktop and inline TOC on mobile.
- Article tables/lists are protected from overflow on small screens.
- Scheduled articles include noindex while queued, canonical URLs, Article JSON-LD, title/meta description, source links, internal links, visible table of contents, and 1-2 restrained accent colors.
- Homepage has a canonical URL and preloads the hero image used as the likely LCP asset.
- RSS is available at `/feed.xml` and `/rss.xml`, and public pages expose a feed alternate link.
- `llms.txt` is available for AI crawler context.
- GSC HTML-file verification is deployed at the site root.

## GSC

- Local GSC service-account credentials are present in `D:\env`.
- Search Console URL-prefix property `https://dogbreedcost.com/` is verified as `siteOwner`.
- `https://dogbreedcost.com/sitemap.xml` was submitted through the Search Console API.
- Latest API check: `pending=false`, `errors=0`, `warnings=0`, with `lastDownloaded` present.

## GA4

- GA4 Admin access through the available Google credentials succeeded.
- No visible GA4 property matched `dogbreedcost.com` or BreedWise.
- The site currently has no GA4 tag in the static HTML; GA4 optimization remains blocked until a property/measurement ID exists or is provided.

## AdSense

- Local AdSense credential files exist in `D:\env`.
- `ads.txt` is deployed with `google.com, pub-3050601904412736, DIRECT, f08c47fec0942fa0`.
- The default AdSense Auto Ads loader is present on public HTML pages.
- No manual ad slots are placed; Auto Ads only.
- AdSense readiness work should keep ads from obscuring the main answer and avoid policy-sensitive medical, insurance, or deceptive monetization claims.

## Not Done Without Explicit Approval

- No Vercel CLI/API/project/domain/environment mutation was run.
- No Turso DB mutation was run.
- No external API or external LLM generated article copy.
