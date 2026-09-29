"""Shared date, sitemap, and RSS helpers.

Contract (DBC-06/07):
- A blog post's publish time comes from content-schedule.json ``published_at`` (first
  publication), else from the page's Article JSON-LD ``datePublished``. Build time is never used.
- Sitemap ``lastmod`` changes only for a URL whose content actually changed; unchanged URLs
  keep their existing value. Re-running a generator on identical input changes nothing.
- RSS lists the newest posts by publish time with per-item ``pubDate`` and a stable GUID.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path

KST = timezone(timedelta(hours=9))
LOC_RE = re.compile(r"<url><loc>(.*?)</loc><lastmod>([^<]*)</lastmod></url>")
JSONLD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def parse_when(value: str) -> datetime | None:
    """Parse an ISO date or datetime; date-only values are treated as 00:00 KST."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=KST)
    return parsed


def schedule_publish_times(schedule_path: Path) -> dict[str, datetime]:
    """Map blog file name -> first publication time recorded in the schedule manifest."""
    if not schedule_path.exists():
        return {}
    times = {}
    for item in json.loads(schedule_path.read_text(encoding="utf-8")):
        when = parse_when(item.get("published_at") or "")
        if when and item.get("target_file"):
            times[Path(item["target_file"]).name] = when
    return times


def article_date_published(html: str) -> datetime | None:
    for raw in JSONLD_RE.findall(html):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("@type") == "Article":
            return parse_when(str(data.get("datePublished") or ""))
    return None


def post_publish_time(path: Path, schedule_times: dict[str, datetime]) -> datetime | None:
    return schedule_times.get(path.name) or article_date_published(path.read_text(encoding="utf-8"))


def read_lastmods(sitemap_text: str) -> dict[str, str]:
    return {loc: lastmod for loc, lastmod in LOC_RE.findall(sitemap_text)}


def render_sitemap(entries: list[tuple[str, str]]) -> str:
    body = "\n".join(f"  <url><loc>{escape(loc)}</loc><lastmod>{lastmod}</lastmod></url>" for loc, lastmod in entries)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'


def set_lastmod(sitemap_text: str, url: str, day: str) -> str:
    """Set one URL's lastmod (appending the URL if absent)."""
    pattern = re.compile(rf"(<url><loc>{re.escape(url)}</loc><lastmod>)([^<]*)(</lastmod></url>)")
    if pattern.search(sitemap_text):
        return pattern.sub(lambda m: m.group(1) + day + m.group(3), sitemap_text, count=1)
    return sitemap_text.replace("</urlset>", f"  <url><loc>{url}</loc><lastmod>{day}</lastmod></url>\n</urlset>")


def write_if_changed(path: Path, text: str) -> bool:
    """Write text only when it differs from the file on disk. Returns True if written."""
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def update_sitemap_for_changes(sitemap: Path, changed_urls: list[str], all_urls: list[str], day: str) -> bool:
    """Bump lastmod only for changed URLs; add any missing URLs with ``day``."""
    text = sitemap.read_text(encoding="utf-8")
    existing = read_lastmods(text)
    for url in all_urls:
        if url in changed_urls or url not in existing:
            text = set_lastmod(text, url, day)
    return write_if_changed(sitemap, text)


def rss_date(moment: datetime) -> str:
    return format_datetime(moment.astimezone(KST))


def render_feed(base_url: str, posts: list[dict[str, object]], limit: int = 20) -> str:
    """posts: dicts with slug, title, description, published (datetime). Newest first, stable GUIDs."""
    dated = sorted((p for p in posts if p.get("published")), key=lambda p: (p["published"], p["slug"]), reverse=True)[:limit]
    items = "\n".join(
        "  <item>"
        f"<title>{escape(str(p['title']))}</title>"
        f"<link>{base_url}/blog/{escape(str(p['slug']))}</link>"
        f"<guid isPermaLink=\"true\">{base_url}/blog/{escape(str(p['slug']))}</guid>"
        f"<description>{escape(str(p['description']))}</description>"
        f"<pubDate>{rss_date(p['published'])}</pubDate>"
        "</item>"
        for p in dated
    )
    last_build = rss_date(dated[0]["published"]) if dated else ""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        "<channel>\n"
        "  <title>BreedWise Dog Breed Planning Guides</title>\n"
        f"  <link>{base_url}/blog/</link>\n"
        "  <description>Evidence-aware dog breed health-risk, ownership cost, and lifestyle fit guides.</description>\n"
        f"  <lastBuildDate>{last_build}</lastBuildDate>\n"
        f"{items}\n"
        "</channel>\n"
        "</rss>\n"
    )


def today_kst() -> str:
    return datetime.now(KST).date().isoformat()


def as_day(moment: datetime | date | None, fallback: str) -> str:
    if moment is None:
        return fallback
    if isinstance(moment, datetime):
        return moment.astimezone(KST).date().isoformat()
    return moment.isoformat()
