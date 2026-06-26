from __future__ import annotations

from datetime import datetime, timezone, timedelta
from html import escape
from pathlib import Path
import json
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SCHEDULE = ROOT / "content-schedule.json"
BLOG_DIR = ROOT / "blog"
BASE_URL = "https://lsk7209.github.io/dog-breed"
KST = timezone(timedelta(hours=9))


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


def publish_due_posts(now: datetime) -> list[str]:
    manifest = json.loads(SCHEDULE.read_text(encoding="utf-8"))
    published: list[str] = []
    for item in manifest:
        target = ROOT / item["target_file"]
        source = ROOT / item["queue_file"]
        if target.exists() or not source.exists():
            continue
        if parse_dt(item["publish_at"]) > now:
            continue
        html = source.read_text(encoding="utf-8")
        html = html.replace('<meta name="robots" content="noindex,follow">', '<meta name="robots" content="index,follow">')
        html = html.replace("<p class=\"kicker\">Scheduled guide</p>", "<p class=\"kicker\">BreedWise Guide</p>")
        html = html.replace("쨌", "&middot;")
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
        "<a class=\"card\" href=\"{slug}\"><span class=\"tag\">BreedWise Guide</span>"
        "<h2>{title}</h2><p>{description}</p></a>".format(
            slug=escape(post["slug"]),
            title=escape(post["title"]),
            description=escape(post["description"]),
        )
        for post in posts
    )
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>BreedWise Blog | Dog breed health-risk and cost planning guides</title><meta name="description" content="Read practical BreedWise guides about dog breed health risks, ownership costs, screening questions, and lifestyle fit."><link rel="stylesheet" href="../assets/site.css">
<link rel="canonical" href="{BASE_URL}/blog/"><meta property="og:title" content="BreedWise Blog | Dog breed health-risk and cost planning guides"><meta property="og:description" content="Read practical BreedWise guides about dog breed health risks, ownership costs, screening questions, and lifestyle fit.">
<meta property="og:type" content="website"><meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#2f6b54"></head>
<body><header class="topbar"><nav class="nav" aria-label="Primary"><a class="brand" href="../index.html"><span class="mark" aria-hidden="true"></span><span>BreedWise</span></a><div class="navlinks"><a href="../blog/index.html">Blog</a><a href="../methodology/index.html">Methodology</a><a href="../about/index.html">About</a><a href="../contact/index.html">Contact</a><a href="../privacy-policy/index.html">Privacy</a></div></nav></header><main><section class="hero"><div class="wrap"><p class="kicker">BreedWise Blog</p><h1>Dog breed planning guides built for useful decisions.</h1><p class="lead">Evidence-aware articles about breed health risks, ownership cost exposure, screening questions, and lifestyle fit. Each guide is written to help future owners ask better questions before commitment.</p></div></section><section class="wrap" style="padding:46px 0"><div class="grid">{cards}</div></section></main><footer class="footer"><div class="wrap"><span>&copy; 2026 BreedWise. Informational planning content only.</span><span><a href="../terms/index.html">Terms</a> &middot; <a href="../privacy-policy/index.html">Privacy Policy</a></span></div></footer></body></html>
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
    if git_has_changes():
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"], cwd=ROOT, check=True)
        subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], cwd=ROOT, check=True)
        subprocess.run(["git", "add", "blog", "sitemap.xml", "content-schedule.json", ".github/content-queue"], cwd=ROOT, check=True)
        subprocess.run(["git", "commit", "-m", f"Publish {len(published)} scheduled BreedWise post(s)"], cwd=ROOT, check=True)
        subprocess.run(["git", "push"], cwd=ROOT, check=True)
    print(f"Published {len(published)} scheduled post(s):")
    for path in published:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
