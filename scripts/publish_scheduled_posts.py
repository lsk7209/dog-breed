from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
import json
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SCHEDULE = ROOT / "content-schedule.json"
BLOG_DIR = ROOT / "blog"
QUEUE_DIR = ROOT / ".github" / "content-queue"
BASE_URL = "https://dogbreedcost.com"
KST = timezone(timedelta(hours=9))
ADSENSE_LOADER = (
    '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?'
    'client=ca-pub-3050601904412736" crossorigin="anonymous"></script>'
)
FEED_LINK = '<link rel="alternate" type="application/rss+xml" title="BreedWise RSS" href="https://dogbreedcost.com/feed.xml">'


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
    html = html.replace("Pre-publish quality check", "Why this guide is useful")
    html = html.replace("AEO summary", "Short answer")
    html = html.replace("Why this keyword deserves its own guide", "Why this guide is useful")
    if "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" not in html:
        html = html.replace("</head>", f"{ADSENSE_LOADER}</head>")
    if FEED_LINK not in html:
        html = html.replace("</head>", f"{FEED_LINK}</head>")
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
    html = ensure_article_main_entity(html, canonical)
    html = ensure_tag(html, f'<meta property="og:type" content="article">')
    return html


def validate_published_html(html: str, target: Path) -> None:
    required = [
        "<title>",
        'name="description"',
        'rel="canonical"',
        'property="og:title"',
        'property="og:description"',
        'application/ld+json',
        'name="robots" content="index,follow"',
        "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js",
    ]
    missing = [item for item in required if item not in html]
    scaffold = ["Pre-publish quality check", "Quality score:", "Quality target:", "AEO summary"]
    leaked = [item for item in scaffold if item in html]
    if missing or leaked:
        details = []
        if missing:
            details.append(f"missing {', '.join(missing)}")
        if leaked:
            details.append(f"leaked scaffold {', '.join(leaked)}")
        raise RuntimeError(f"{target.relative_to(ROOT)} failed publish validation: {'; '.join(details)}")


def publish_due_posts(now: datetime) -> list[str]:
    manifest = json.loads(SCHEDULE.read_text(encoding="utf-8"))
    published: list[str] = []
    for item in manifest:
        target = safe_child_path(BLOG_DIR, item["target_file"])
        source = safe_child_path(QUEUE_DIR, item["queue_file"])
        if target.exists() or not source.exists():
            continue
        if parse_dt(item["publish_at"]) > now:
            continue
        html = prepare_published_html(source.read_text(encoding="utf-8"), item["target_file"])
        validate_published_html(html, target)
        target.write_text(html, encoding="utf-8")
        source.unlink()
        item["status"] = "published"
        item["published_at"] = now.astimezone(KST).isoformat()
        published.append(item["target_file"])
    SCHEDULE.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return published


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
<meta name="robots" content="index,follow"><meta property="og:type" content="website"><meta property="og:image" content="{BASE_URL}/assets/hero-dog-risk.png"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{BASE_URL}/assets/hero-dog-risk.png"><meta name="theme-color" content="#2f6b54">{ADSENSE_LOADER}{FEED_LINK}</head>
<body><header class="topbar"><nav class="nav" aria-label="Primary"><a class="brand" href="../index.html"><span class="mark" aria-hidden="true"></span><span>BreedWise</span></a><div class="navlinks"><a href="../blog/index.html">Blog</a><a href="../methodology/index.html">Methodology</a><a href="../about/index.html">About</a><a href="../contact/index.html">Contact</a><a href="../privacy-policy/index.html">Privacy</a><a href="../disclosures/index.html">Disclosures</a></div></nav></header><main><section class="hero"><div class="wrap"><p class="kicker">BreedWise Blog</p><h1>Dog breed planning guides built for useful decisions.</h1><p class="lead">Evidence-aware articles about breed health risks, ownership cost exposure, screening questions, and lifestyle fit. Each guide is written to help future owners ask better questions before commitment.</p></div></section><section class="wrap" style="padding:46px 0"><div class="blog-tools"><p class="blog-count">{len(posts)} published guides</p><a class="button" href="../methodology/index.html">Review methodology</a></div><div class="blog-grid">{cards}</div></section></main><footer class="footer"><div class="wrap"><span>&copy; 2026 BreedWise. Informational planning content only.</span><span><a href="../terms/index.html">Terms</a> &middot; <a href="../privacy-policy/index.html">Privacy Policy</a> &middot; <a href="../disclosures/index.html">Disclosures</a> &middot; <a href="../contact/index.html">Contact</a></span></div></footer></body></html>
"""
    (BLOG_DIR / "index.html").write_text(html, encoding="utf-8")


def rebuild_sitemap() -> None:
    today = datetime.now(KST).date().isoformat()
    urls = [
        "",
        "blog/",
        "about/",
        "contact/",
        "privacy-policy/",
        "terms/",
        "methodology/",
        "disclosures/",
    ]
    urls.extend(f"blog/{path.name}" for path in sorted(BLOG_DIR.glob("*.html")) if path.name != "index.html")
    body = "\n".join(f"  <url><loc>{BASE_URL}/{url}</loc><lastmod>{today}</lastmod></url>" for url in urls)
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def rebuild_feed() -> None:
    posts = [read_meta(path) for path in sorted(BLOG_DIR.glob("*.html")) if path.name != "index.html"]
    latest = datetime.now(KST).strftime("%a, %d %b %Y %H:%M:%S %z")
    items = "\n".join(
        "  <item>"
        f"<title>{escape(post['title'])}</title>"
        f"<link>{BASE_URL}/blog/{escape(post['slug'])}</link>"
        f"<guid>{BASE_URL}/blog/{escape(post['slug'])}</guid>"
        f"<description>{escape(post['description'])}</description>"
        f"<pubDate>{latest}</pubDate>"
        "</item>"
        for post in posts[:20]
    )
    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        "<channel>\n"
        "  <title>BreedWise Dog Breed Planning Guides</title>\n"
        f"  <link>{BASE_URL}/blog/</link>\n"
        "  <description>Evidence-aware dog breed health-risk, ownership cost, and lifestyle fit guides.</description>\n"
        f"  <lastBuildDate>{latest}</lastBuildDate>\n"
        f"{items}\n"
        "</channel>\n"
        "</rss>\n"
    )
    (ROOT / "feed.xml").write_text(feed, encoding="utf-8")
    (ROOT / "rss.xml").write_text(feed, encoding="utf-8")


def git_has_changes() -> bool:
    result = subprocess.run(["git", "status", "--short"], cwd=ROOT, text=True, capture_output=True, check=True)
    return bool(result.stdout.strip())


def main() -> int:
    now = datetime.now(timezone.utc)
    published = publish_due_posts(now)
    if not published:
        print("No scheduled posts are due.")
        return 0
    rebuild_blog_index()
    rebuild_sitemap()
    rebuild_feed()
    if git_has_changes():
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"], cwd=ROOT, check=True)
        subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], cwd=ROOT, check=True)
        subprocess.run(["git", "add", "blog", "sitemap.xml", "feed.xml", "rss.xml", "content-schedule.json", ".github/content-queue"], cwd=ROOT, check=True)
        subprocess.run(["git", "commit", "-m", f"Publish {len(published)} scheduled BreedWise post(s)"], cwd=ROOT, check=True)
        subprocess.run(["git", "push"], cwd=ROOT, check=True)
    print(f"Published {len(published)} scheduled post(s):")
    for path in published:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
