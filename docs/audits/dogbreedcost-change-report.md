# DogBreedCost change report — 2026-09-29

Base: `main` @ `601e7dc` → local branch `improve/dbc-plan-2026-09-29` (not committed, not pushed, not deployed).
Plan: `dogbreedcost_codex_improvement_plan_2026-09-29.md` (DBC-01~18).

## Issue status

| ID | Status | Change |
|---|---|---|
| DBC-01/02/03 | fixed | Missing forecast → `unavailable`, missing AQI (incl. AirNow `-1`) → `incomplete`; never `low`. 0°F / AQI 0 shown. All 8 evaluated periods displayed with start time + offset; AQI observed time + zone shown. Label described as a BreedWise threshold label, not an official rating. `risk_level` stays NOT NULL text (Turso-compatible) and a `data_status` field is added. |
| DBC-08 | fixed | BLS: only M01–M12, positive finite values, dedupe, sort by (year, month); empty/all-missing → `BLSDataError` (no empty hub); partial response keeps previous page marked `stale`; footnotes and month gaps shown; YoY `unavailable` without a valid denominator; `updated` kept when data unchanged. |
| DBC-09/10 | fixed | `assets/breedwise-tools.js`: $160 × 60 = $9,600 regardless of size; invalid input shows an error and no numbers; the reserve is separate from projected spending; no 1.24/1.34 multiplier. Fixed score dial removed. Finder shows all 4 breeds with met/unmet conditions; lower ≠ moderate. Insurance/allergy claims removed from the cards. |
| DBC-04/05 | fixed | `scripts/content_quality.py` checks visible writer instructions, H1/canonical/JSON-LD, duplicate ids, missing anchors, and repeated body paragraphs. The publisher uses it, and the AdSense requirement was removed. Heading audit now reports `missingAnchorTargets`. |
| DBC-14 | fixed | Publisher: `editorial_status == "approved"` required; all due items validated before any write; failed items stay queued; `--dry-run`; Git commit/push only with `--commit-and-push` (workflow updated). |
| DBC-06/07 | fixed | `scripts/site_metadata.py`: RSS newest-first by `published_at`/`datePublished` with per-item pubDate; sitemap lastmod only for changed URLs; generators write files only when content differs. |
| DBC-12/13 | fixed | `site.css` ≤520px: links wrap (nth-child hiding removed); header static on mobile. Home: nav wraps ≤920px; hero offset adjusted. |
| DBC-11 | partially fixed | Privacy policy now states GA4 is in use (purpose, opt-out) and where the AdSense script loads. Operator identity, data retention, and a consent/CMP setup are not addressed (owner decision). |
| DBC-15 | partially fixed | The outdoor and BLS generators validate data before writing. Workflow concurrency, deploy-then-GSC ordering, and Turso snapshot checks were not changed. |
| DBC-16 | not fixed (inventory only) | 122/210 blog pages show visible writer instructions ("quick answer engines", "expanded keyword"); 33 repeated-paragraph groups (largest: 100 pages). Not bulk-rewritten, per plan. The "pSEO" sentence was removed from the 3 cost pages (generator). |
| DBC-17/18 | not run | Hero image optimization and analytics events are out of scope for this pass. |

## Verification (actual runs)

- `cd tests && python -m unittest discover -s . -p "test_*.py"` → 39 passed (W01–W09, B01–B08, P01–P09, M01–M06, A01, A06). Socket/subprocess access is blocked inside the tests.
- `node --test tests/js/tools.test.js` → 8 passed (C01–C06, C08).
- `python scripts/audit_heading_uniqueness.py` → 211 pages checked, 0 failures.
- `content_quality.py --no-article` on cost/ and outdoor-risk/ → 0 structure issues, 0 leaks.
- Cached rebuild (`BREEDWISE_USE_CACHED_DATA=1`) run twice → identical diff; sitemap unchanged by generators.
- `publish_scheduled_posts.py --dry-run` → 0 due, 0 blocked.
- feed.xml / rss.xml / sitemap.xml parsed as XML.
- Browser (headless Chrome on a local server with ad/GA tags stripped): home, blog index, article, privacy, cost, and outdoor pages at 320/360/390/768/1024/1440 px → scrollWidth equals viewport width and no nav link is clipped. Home hero does not overlap the header. TOC anchor target visible below the header. Calculator error and recovery paths checked at 390 px.
- NOT_RUN: live BLS/NWS/AirNow fetch, Turso sync, GSC, production deploy, 200% zoom, a screen reader.

## Owner decisions / notes before release

1. Future queue entries need `"editorial_status": "approved"` or they will be blocked (currently none are queued).
2. AdSense loads on Home, Methodology, and Disclosures, which contradicts HANDOFF (2026-07-29). This was left unchanged.
3. Pushing changes to `sitemap.xml`/`feed.xml` triggers `submit-gsc-sitemap.yml`.
4. Sitemap lastmod was bumped to 2026-09-29 only for the 11 URLs whose HTML changed (`/`, `/privacy-policy/`, 3 cost pages, 6 outdoor pages); all other URLs keep their dates.
5. Blog scaffold leaks: fix a few representative guides individually (Task 8), not in bulk.

Rollback: discard the branch; there are no remote side effects.
