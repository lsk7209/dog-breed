from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
import argparse
import json
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import content_quality  # noqa: E402
import site_metadata  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
SCHEDULE = ROOT / "content-schedule.json"
BLOG_DIR = ROOT / "blog"
COST_DIR = ROOT / "cost"
RISK_DIR = ROOT / "outdoor-risk"
QUEUE_DIR = ROOT / ".github" / "content-queue"
BASE_URL = "https://dogbreedcost.com"
KST = timezone(timedelta(hours=9))
ADSENSE_LOADER = (
    '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?'
    'client=ca-pub-3050601904412736" crossorigin="anonymous"></script>'
)
GA4_TAG = (
    '<script async src="https://www.googletagmanager.com/gtag/js?id=G-5FZSHME54N"></script>'
    '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}'
    "gtag('js',new Date());gtag('config','G-5FZSHME54N');</script>"
)
FEED_LINK = '<link rel="alternate" type="application/rss+xml" title="BreedWise RSS" href="https://dogbreedcost.com/feed.xml">'
VERIFICATION_TAGS = (
    '<meta name="google-site-verification" content="33-RSHdhGx_IC-b1_fpFOHyr-s0P35VSCOwIOFy6UAE">'
    '<meta name="naver-site-verification" content="d0084eb5ece035b3d7de4936181ae0dd92022175">'
)


def parse_dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=KST)
    return parsed.astimezone(timezone.utc)


def read_meta(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    title = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
    description = re.search(r'<meta name="description" content="(.*?)"', text, re.I | re.S)
    return {
        "title": re.sub(r"\s+", " ", title.group(1)).strip() if title else path.stem,
        "description": re.sub(r"\s+", " ", description.group(1)).strip() if description else "",
        "slug": path.name,
    }


def safe_child_path(base: Path, value: str) -> Path:
    path = (ROOT / value).resolve()
    expected = base.resolve()
    if expected != path and expected not in path.parents:
        raise RuntimeError(f"path escapes expected directory: {value}")
    if path.suffix != ".html":
        raise RuntimeError(f"scheduled content must be an HTML file: {value}")
    return path


def normalize_published_html(html: str) -> str:
    html = html.replace('<meta name="robots" content="noindex,follow">', '<meta name="robots" content="index,follow">')
    html = html.replace("<p class=\"kicker\">Scheduled guide</p>", "<p class=\"kicker\">BreedWise Guide</p>")
    html = html.replace("Main keyword:", "Planning topic:")
    html = html.replace("Expanded keywords:", "Decision focus:")
    html = re.sub(r"Scheduled:\s*[^<]+", lambda match: "Updated: " + match.group(0).split("T", 1)[0].replace("Scheduled:", "").strip(), html)
    html = html.replace("Quality score: 94", "Educational planning guide")
    html = html.replace("Quality target: 90+", "Educational planning guide")
    html = html.replace("Pre-publish quality check", "Decision boundary and next step")
    html = html.replace("AEO summary", "Short answer")
    html = html.replace("Why this keyword deserves its own guide", "Why this topic needs its own guide")
    if "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" not in html:
        html = html.replace("</head>", f"{ADSENSE_LOADER}</head>")
    if "googletagmanager.com/gtag/js?id=G-5FZSHME54N" not in html:
        html = html.replace("</head>", f"{GA4_TAG}</head>")
    if FEED_LINK not in html:
        html = html.replace("</head>", f"{FEED_LINK}</head>")
    if 'name="google-site-verification"' not in html:
        html = html.replace("</head>", f"{VERIFICATION_TAGS}</head>")
    return html


def ensure_tag(html: str, tag: str) -> str:
    return html if tag in html else html.replace("</head>", f"{tag}</head>")


def ensure_canonical(html: str, canonical: str) -> str:
    tag = f'<link rel="canonical" href="{canonical}">'
    if 'rel="canonical"' in html:
        html = re.sub(r'<link rel="canonical" href="[^"]*">', tag, html, count=1)
    else:
        html = html.replace("</title>", f"</title>{tag}", 1)
    return html


def ensure_open_graph(html: str) -> str:
    meta = read_meta_from_html(html)
    if 'property="og:title"' not in html:
        html = html.replace("</head>", f'<meta property="og:title" content="{escape(meta["title"])}"></head>')
    if 'property="og:description"' not in html:
        html = html.replace("</head>", f'<meta property="og:description" content="{escape(meta["description"])}"></head>')
    return html


def read_meta_from_html(html: str) -> dict[str, str]:
    title = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    description = re.search(r'<meta name="description" content="(.*?)"', html, re.I | re.S)
    return {
        "title": re.sub(r"\s+", " ", title.group(1)).strip() if title else "BreedWise Guide",
        "description": re.sub(r"\s+", " ", description.group(1)).strip() if description else "BreedWise dog breed planning guide.",
    }


def ensure_article_main_entity(html: str, canonical: str) -> str:
    if "mainEntityOfPage" in html:
        return html
    pattern = r'(<script type="application/ld\+json">)(.*?)(</script>)'
    match = re.search(pattern, html, re.S)
    if not match:
        return html
    try:
        payload = json.loads(match.group(2))
    except json.JSONDecodeError:
        return html
    if payload.get("@type") == "Article":
        payload["mainEntityOfPage"] = canonical
        replacement = match.group(1) + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + match.group(3)
        html = html[: match.start()] + replacement + html[match.end() :]
    return html


def prepare_published_html(html: str, target_file: str) -> str:
    normalized_target = target_file.replace("\\", "/")
    canonical = f"{BASE_URL}/{normalized_target}"
    html = normalize_published_html(html)
    html = ensure_canonical(html, canonical)
    html = ensure_open_graph(html)
    html = ensure_article_main_entity(html, canonical)
    html = ensure_tag(html, f'<meta property="og:type" content="article">')
    return html


def validate_published_html(html: str, target: Path) -> None:
    """Block publication on missing metadata, broken structure, or visible writer instructions.

    Ad tags are intentionally not required here: ad placement is a route policy, not content quality.
    """
    required = [
        "<title>",
        'name="description"',
        'rel="canonical"',
        'property="og:title"',
        'property="og:description"',
        'application/ld+json',
        'name="robots" content="index,follow"',
    ]
    missing = [item for item in required if item not in html]
    result = content_quality.check_page(html)
    details = []
    if missing:
        details.append(f"missing {', '.join(missing)}")
    if result["structure"]:
        details.append("structure: " + "; ".join(result["structure"]))
    if result["scaffold"]:
        details.append("visible writer instructions: " + "; ".join(sorted({leak["type"] for leak in result["scaffold"]})))
    if details:
        raise RuntimeError(f"{target.name} failed publish validation: {' | '.join(details)}")


def is_approved(item: dict[str, object]) -> bool:
    return str(item.get("editorial_status") or "").lower() == "approved"


def publish_due_posts(now: datetime, dry_run: bool = False) -> tuple[list[str], list[dict[str, str]]]:
    """Publish due, approved queue items.

    Every due item is prepared and validated before any file is written. Items that fail are
    reported and left untouched (queue file kept, manifest entry unchanged), so a later failure
    cannot leave the manifest, queue, and blog directory out of sync.
    Returns (published target files, blocked items with reasons).
    """
    manifest = json.loads(SCHEDULE.read_text(encoding="utf-8"))
    staged: list[tuple[dict[str, object], Path, Path, str]] = []
    blocked: list[dict[str, str]] = []
    for item in manifest:
        if item.get("status") == "published":
            continue
        target = safe_child_path(BLOG_DIR, item["target_file"])
        source = safe_child_path(QUEUE_DIR, item["queue_file"])
        if parse_dt(item["publish_at"]) > now:
            continue
        reason = None
        if target.exists():
            reason = "target already exists"
        elif not source.exists():
            reason = "queue file missing"
        elif not is_approved(item):
            reason = "editorial_status is not 'approved'"
        if reason is None:
            try:
                html = prepare_published_html(source.read_text(encoding="utf-8"), item["target_file"])
                validate_published_html(html, target)
            except RuntimeError as error:
                reason = str(error)
        if reason:
            blocked.append({"target_file": item["target_file"], "reason": reason})
            continue
        staged.append((item, target, source, html))
    if dry_run or not staged:
        return [item["target_file"] for item, *_ in staged], blocked
    published_at = now.astimezone(KST).isoformat()
    for item, target, source, html in staged:
        target.write_text(html, encoding="utf-8")
    for item, target, source, html in staged:
        source.unlink()
        item["status"] = "published"
        item["published_at"] = published_at
    SCHEDULE.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return [item["target_file"] for item, *_ in staged], blocked


def rebuild_blog_index() -> None:
    posts = [read_meta(path) for path in sorted(BLOG_DIR.glob("*.html")) if path.name != "index.html"]
    cards = "\n".join(
        "<a class=\"blog-card\" href=\"{slug}\"><span class=\"tag\">BreedWise Guide</span>"
        "<h2>{title}</h2><p>{description}</p><span class=\"read-more\">Read guide</span></a>".format(
            slug=escape(post["slug"]),
            title=escape(post["title"]),
            description=escape(post["description"]),
        )
        for post in posts
    )
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>BreedWise Blog | Dog breed health-risk and cost planning guides</title><meta name="description" content="Read practical BreedWise guides about dog breed health risks, ownership costs, screening questions, and lifestyle fit."><link rel="stylesheet" href="../assets/site.css">
<link rel="canonical" href="{BASE_URL}/blog/"><meta property="og:title" content="BreedWise Blog | Dog breed health-risk and cost planning guides"><meta property="og:description" content="Read practical BreedWise guides about dog breed health risks, ownership costs, screening questions, and lifestyle fit.">
<meta name="robots" content="index,follow"><meta property="og:type" content="website"><meta property="og:image" content="{BASE_URL}/assets/hero-dog-risk.png"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{BASE_URL}/assets/hero-dog-risk.png"><meta name="theme-color" content="#2f6b54">{ADSENSE_LOADER}{GA4_TAG}{FEED_LINK}{VERIFICATION_TAGS}</head>
<body><header class="topbar"><nav class="nav" aria-label="Primary"><a class="brand" href="../index.html"><span class="mark" aria-hidden="true"></span><span>BreedWise</span></a><div class="navlinks"><a href="../blog/index.html">Blog</a><a href="../cost/index.html">Cost Data</a><a href="../outdoor-risk/index.html">Outdoor Risk</a><a href="../methodology/index.html">Methodology</a><a href="../about/index.html">About</a><a href="../contact/index.html">Contact</a><a href="../privacy-policy/index.html">Privacy</a><a href="../disclosures/index.html">Disclosures</a></div></nav></header><main><section class="hero"><div class="wrap"><p class="kicker">BreedWise Blog</p><h1>Dog breed planning guides built for useful decisions.</h1><p class="lead">Evidence-aware articles about breed health risks, ownership cost exposure, screening questions, and lifestyle fit. Each guide is written to help future owners ask better questions before commitment.</p></div></section><section class="wrap" style="padding:46px 0"><div class="blog-tools"><p class="blog-count">{len(posts)} published guides</p><a class="button" href="../methodology/index.html">Review methodology</a></div><div class="blog-grid">{cards}</div></section></main><footer class="footer"><div class="wrap"><span>&copy; 2026 BreedWise. Informational planning content only.</span><span><a href="../terms/index.html">Terms</a> &middot; <a href="../privacy-policy/index.html">Privacy Policy</a> &middot; <a href="../disclosures/index.html">Disclosures</a> &middot; <a href="../contact/index.html">Contact</a></span></div></footer></body></html>
"""
    (BLOG_DIR / "index.html").write_text(html, encoding="utf-8")


def site_urls() -> list[str]:
    urls = [
        "",
        "blog/",
        "cost/",
        "outdoor-risk/",
        "about/",
        "contact/",
        "privacy-policy/",
        "terms/",
        "methodology/",
        "disclosures/",
    ]
    urls.extend(f"blog/{path.name}" for path in sorted(BLOG_DIR.glob("*.html")) if path.name != "index.html")
    if COST_DIR.exists():
        urls.extend(f"cost/{path.name}" for path in sorted(COST_DIR.glob("*.html")) if path.name != "index.html")
    if RISK_DIR.exists():
        urls.extend(f"outdoor-risk/{path.name}" for path in sorted(RISK_DIR.glob("*.html")) if path.name != "index.html")
    return [f"{BASE_URL}/{url}" for url in urls]


def rebuild_sitemap(changed_urls: list[str] | None = None, today: str | None = None) -> None:
    """Rebuild the URL list while keeping each existing URL's lastmod.

    Only URLs in ``changed_urls`` (and newly added URLs) get ``today``. Unchanged pages keep
    their previous lastmod instead of all being stamped with the build date.
    """
    today = today or site_metadata.today_kst()
    changed = set(changed_urls or [])
    sitemap = ROOT / "sitemap.xml"
    existing = site_metadata.read_lastmods(sitemap.read_text(encoding="utf-8")) if sitemap.exists() else {}
    entries = [(url, today if url in changed or url not in existing else existing[url]) for url in site_urls()]
    site_metadata.write_if_changed(sitemap, site_metadata.render_sitemap(entries))


def rebuild_feed() -> None:
    """RSS of the 20 most recently published guides, each with its own publication date."""
    times = site_metadata.schedule_publish_times(SCHEDULE)
    posts = []
    for path in sorted(BLOG_DIR.glob("*.html")):
        if path.name == "index.html":
            continue
        meta = read_meta(path)
        meta["published"] = site_metadata.post_publish_time(path, times)
        posts.append(meta)
    feed = site_metadata.render_feed(BASE_URL, posts)
    site_metadata.write_if_changed(ROOT / "feed.xml", feed)
    site_metadata.write_if_changed(ROOT / "rss.xml", feed)


def git_has_changes() -> bool:
    result = subprocess.run(["git", "status", "--short"], cwd=ROOT, text=True, capture_output=True, check=True)
    return bool(result.stdout.strip())


def commit_and_push(count: int) -> None:
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], cwd=ROOT, check=True)
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], cwd=ROOT, check=True)
    subprocess.run(["git", "add", "blog", "sitemap.xml", "feed.xml", "rss.xml", "content-schedule.json", ".github/content-queue"], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-m", f"Publish {count} scheduled BreedWise post(s)"], cwd=ROOT, check=True)
    subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=ROOT, check=True)
    subprocess.run(["git", "push"], cwd=ROOT, check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publish due, approved BreedWise posts.")
    parser.add_argument("--dry-run", action="store_true", help="validate and report only; write nothing")
    parser.add_argument("--commit-and-push", action="store_true", help="commit and push after publishing (CI only)")
    args = parser.parse_args(argv)
    now = datetime.now(timezone.utc)
    published, blocked = publish_due_posts(now, dry_run=args.dry_run)
    for item in blocked:
        print(f"BLOCKED {item['target_file']}: {item['reason']}")
    if args.dry_run:
        print(f"Dry run: {len(published)} post(s) would be published, {len(blocked)} blocked.")
        for path in published:
            print(f"- {path}")
        return 0
    if not published:
        print("No scheduled posts are due.")
        return 0
    rebuild_blog_index()
    rebuild_sitemap(changed_urls=[f"{BASE_URL}/{path}" for path in published] + [f"{BASE_URL}/blog/"])
    rebuild_feed()
    if args.commit_and_push and git_has_changes():
        commit_and_push(len(published))
    print(f"Published {len(published)} scheduled post(s):")
    for path in published:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
