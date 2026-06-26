# BreedWise Optimization Status

Checked: 2026-06-26 KST

## Implemented

- Site/content persona system added in `docs/personas.md`.
- `/blog/` archive uses a responsive card grid with clearer scan paths and a methodology CTA.
- Article layout supports sticky table of contents on desktop and inline TOC on mobile.
- Article tables/lists are protected from overflow on small screens.
- Scheduled articles include noindex while queued, canonical URLs, Article JSON-LD, title/meta description, source links, internal links, visible table of contents, and 1-2 restrained accent colors.
- Homepage has a canonical URL and preloads the hero image used as the likely LCP asset.

## GSC

- Local GSC token and credentials are present in `D:\env`.
- Read-only Search Console site listing succeeded.
- No visible property matched `dog-breed`, `BreedWise`, `lsk7209.github.io`, or `github.io` for this site.
- Data-based GSC query/page optimization requires adding or granting access to the correct property, likely `https://lsk7209.github.io/dog-breed/` or the deployed custom domain if one is later used.

## GA4

- Local GA4 token is present in `D:\env`.
- GA4 Admin account summary read succeeded.
- No visible property matched `dog-breed`, `BreedWise`, `lsk7209.github.io`, or `github.io`.
- The site currently has no GA4 tag in the static HTML.

## AdSense

- Local AdSense credential files exist in `D:\env`.
- The site currently has no AdSense script or ad slots.
- AdSense readiness work should keep ad slots below the main answer, reserve slot dimensions to avoid CLS, and avoid policy-sensitive medical, insurance, or deceptive monetization claims.

## Not Done Without Explicit Approval

- No Vercel CLI/API/project/domain/environment mutation was run.
- No Turso DB mutation was run.
- No external API or external LLM generated article copy.
