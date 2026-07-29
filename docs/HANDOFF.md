# Handoff

## Basenji quiet-home decision guide staged (2026-07-29 11:55 KST)

- Current state: `blog/basenji-barkless-breed-reality.html` has one individually reviewed source/originality revision staged for release. It replaces the repeated generic next-step section with a normal-workday test for sound-sensitive moments, safety routine, repeatable work, and source-specific questions.
- Evidence: the guide links directly to the American Kennel Club Basenji profile and limits its claim to the documented distinction between no ordinary bark and other vocal sounds plus general activity, secure handling, and training considerations. `python scripts/audit_heading_uniqueness.py` passed all 167 pages; the article has zero generic next-step heading, one H1, one canonical, the article-route AdSense loader, and the existing no-diagnosis boundary.
- Side-effect boundary: no title, URL, schedule, indexing, AdSense application, or external Google action has been changed. The article-only release is pending remote-history reconciliation, push, Vercel readiness, and public-page verification.
- Single next step: fetch/rebase against `origin/main`, release the article-only commit, then record deployment and public verification evidence.

## Doberman record-verification revision released (2026-07-29 11:48 KST)

- Current state: `blog/doberman-heart-screening-questions.html` has one individually reviewed source/originality revision released. It replaces the generic `Practical next step` section with a record-verification sheet; it does not diagnose, prescribe, or make a health guarantee.
- Evidence: it links directly to the Orthopedic Foundation for Animals CHIC-program and cardiac-record guidance, keeps the existing AVMA/AAHA/Cornell source list and the no-diagnosis editorial boundary. `python scripts/audit_heading_uniqueness.py` passed all 167 pages; the article has zero generic next-step heading, one H1, one canonical, and one article-route AdSense loader.
- Release evidence: article commit `fc66c1b` and checkpoint commit `2aa0068` are pushed to `origin/main`. Production deployment `dpl_99XHN6UPDbyfPFiggepoucvbjuB1` (`dog-breed-qw7631yb4-limsubs-projects.vercel.app`) is Ready with the production aliases. The public article returns HTTP 200 with the new heading and both OFA links, zero generic next-step heading, one H1, one canonical, one article-route AdSense loader, and the no-diagnosis boundary.
- Side-effect boundary: no title, URL, schedule, indexing, AdSense application, or external Google action has been changed.
- Single next step: select a third non-overlapping topic cluster for one individually verified source/originality revision; do not bulk-rewrite the remaining generic sections.

## Editorial originality audit checkpoint (2026-07-29 11:25 KST)

- Fresh dashboard evidence now comes from the 103-site snapshot generated `2026-07-29T02:16:44.411Z`; `dogbreedcost` has 21 last-7-day GSC impressions, zero clicks, position 25.0, and healthy public AdSense/ads.txt collector states.
- The repository is static Vercel content, not a Vercel API/DB collection site. The first individually verified content revision is released; no schedule, title, URL, indexing, or AdSense state changed.
- The published corpus has 105 (not 101) files with the exact `Practical next step` heading. Existing review documentation is therefore stale about the count, but correct that this is an editorial originality risk.
- Do not bulk-rewrite the 105 files or alter schedules. The next safe action is a topic-cluster representative source/originality review, followed only by individually verified article revisions with evidence, originality, and medical-advice boundaries preserved.
- First individual revision: `blog/beagle-apartment-exercise-plan.html` replaces the generic next-step paragraph with a Beagle-specific seven-day apartment-readiness log. It cites the current AKC Beagle exercise/handling overview and retains the existing no-diagnosis editorial boundary. Local validation: `audit_heading_uniqueness.py` passed 165 pages; the article has one H1, one canonical, the new heading, and the cited source link.
- Released in `0ee222d` after preserving two intervening scheduled-publication commits. Vercel production deployment `dog-breed-dhptrtwpl-limsubs-projects.vercel.app` is Ready from that commit. Public verification confirms the article returns 200 with the new heading/source, zero remaining generic next-step heading, one H1, one canonical, and one article-route AdSense loader.

## Site 23 `dogbreedcost.com` production repair complete (2026-07-29 03:12 KST)

- User goal: improve the managed site fleet for reader experience, AdSense review readiness, and Google-facing content quality without claiming external approval or ranking.
- Exact state: the scoped static repair is live and verified. The repository is clean after the release commits; select any next fleet site only after a fresh dashboard snapshot.
- Current evidence: the parent dashboard snapshot generated `2026-07-28T17:57:39.607Z` reports 82 active users, 2 clicks, 202 impressions, 0.99% CTR, and position 14.04. Public collector states are healthy.
- Stack: static HTML deployed through the Git-connected Vercel project in `.vercel/project.json`; the dashboard's WordPress label is stale. This site is not an API/DB collection site in the current Vercel API-data inventory.
- Applied scope: removed the common AdSense loader from Home and the six trust/legal routes; retained it on Blog and individual article routes; constrained the 390px primary navigation to four reader-navigation links, with trust/legal links retained in the footer. Article bodies, titles, URLs, source links, schedules, and analytics remain unchanged.
- Fresh release evidence: `e4f282d` scopes the loaders and mobile navigation; `ec98d02` restores the favicon fallback. Vercel production deployment `dpl_EutSia79gXFYyF79LfrdgoXoJ7Qf` is Ready. Public routes confirm zero loaders on Home/trust pages and one on Blog/representative article; `/favicon.ico` now returns 308 to `/assets/breedwise-mark.svg`, which returns 200 `image/svg+xml`. Final 390px article capture is `D:\web\multi-dashboard\output\playwright\fleet-site23-dogbreedcost-article-final-mobile.png`.
- External boundary: no AdSense submission/resubmission or Google indexing request. Technical readiness is not AdSense approval or ranking evidence.
- Remaining risk: 101 published guides retain the repeated generic `Practical next step` section. Keep external AdSense review action on HOLD until a representative source/originality review supports individual article changes.
- Deliberately not run: article rewrite/deletion, title/URL/source/schedule mutation, analytics changes, AdSense submission/resubmission, Google indexing request, or Vercel configuration beyond the favicon redirect.
- Single next step: refresh dashboard evidence and select the next eligible non-colliding site.
