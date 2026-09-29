"""Task 4/5: publication validation, safe batch publishing, RSS and sitemap date contract.

Covers P01-P09 and M01-M06. All file I/O happens in a temporary directory.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from _support import load_script

publish = load_script("publish_scheduled_posts")
quality = publish.content_quality
meta = publish.site_metadata
heading = load_script("audit_heading_uniqueness")


def article(title="Beagle guide", body="<p>Useful reader text.</p>", toc='<a href="#costs">Costs</a>',
            date_published="2026-07-01", jsonld=None, h1=1, canonical="https://dogbreedcost.com/blog/x.html"):
    ld = jsonld if jsonld is not None else json.dumps({"@type": "Article", "headline": title, "datePublished": date_published})
    h1s = "".join(f"<h1>{title}</h1>" for _ in range(h1))
    return (
        f'<!doctype html><html><head><title>{title}</title><meta name="description" content="d">'
        f'<link rel="canonical" href="{canonical}"><meta name="robots" content="noindex,follow">'
        f'<script type="application/ld+json">{ld}</script></head><body>'
        f'<nav><a href="../blog/index.html">Blog</a></nav><main>{h1s}{toc}'
        f'<h2 id="costs">Costs</h2>{body}</main><footer><p>Footer</p></footer></body></html>'
    )


class Validation(unittest.TestCase):
    def test_p01_visible_writer_instructions_are_blocked(self):
        html = article(body="<p>For quick answer engines: the expanded keyword area is the lens.</p>")
        types = {leak["type"] for leak in quality.scaffold_leaks(html)}
        self.assertEqual(types, {"answer-engine instruction", "keyword instruction"})
        with self.assertRaisesRegex(RuntimeError, "visible writer instructions"):
            publish.validate_published_html(publish.prepare_published_html(html, "blog/x.html"), Path("x.html"))

    def test_p01_title_rename_alone_does_not_pass(self):
        leak = article(body="<p>This article supports the site instead of competing with existing breed cost guides.</p>")
        self.assertEqual({l["type"] for l in quality.scaffold_leaks(leak)}, {"search-positioning note"})
        html = article(body="<h2>AEO summary</h2><p>The main keyword should appear early.</p>")
        prepared = publish.prepare_published_html(html, "blog/x.html")
        self.assertIn("Short answer", prepared)  # heading renamed...
        with self.assertRaises(RuntimeError):     # ...but the body instruction still blocks it
            publish.validate_published_html(prepared, Path("x.html"))

    def test_p02_normal_reader_headings_pass(self):
        html = article(body='<h2 id="s">Short answer</h2><p>Sources and next step for owners.</p>',
                       toc='<a href="#costs">Costs</a><a href="#s">Short answer</a>')
        prepared = publish.prepare_published_html(html, "blog/x.html")
        publish.validate_published_html(prepared, Path("x.html"))
        self.assertEqual(quality.scaffold_leaks(prepared), [])

    def test_scaffold_in_script_is_ignored(self):
        html = article(body="<p>ok</p><script>var mainKeyword='main keyword';</script>")
        self.assertEqual(quality.scaffold_leaks(html), [])

    def test_p03_missing_anchor_and_duplicate_id(self):
        issues = quality.structure_issues(article(toc='<a href="#nope">x</a><span id="costs"></span>'))
        self.assertTrue(any("missing: nope" in i for i in issues))
        self.assertTrue(any("duplicate id(s): costs" in i for i in issues))
        tmp = Path(tempfile.mkdtemp())
        try:
            page = tmp / "p.html"
            page.write_text(article(toc='<a href="#nope">x</a>'), encoding="utf-8")
            self.assertEqual(heading.audit_file(page)["missingAnchorTargets"], ["nope"])
        finally:
            shutil.rmtree(tmp)

    def test_p04_structure_checks(self):
        self.assertTrue(any("invalid JSON-LD" in i for i in quality.structure_issues(article(jsonld="{bad"))))
        self.assertTrue(any("empty JSON-LD" in i for i in quality.structure_issues(article(jsonld="{}"))))
        self.assertTrue(any("<h1>" in i for i in quality.structure_issues(article(h1=2))))
        self.assertTrue(any("canonical" in i for i in quality.structure_issues(article(canonical=""))))

    def test_p05_ad_tag_is_not_a_quality_requirement(self):
        prepared = publish.prepare_published_html(article(), "blog/x.html")
        prepared = prepared.replace(publish.ADSENSE_LOADER, "")
        self.assertNotIn("adsbygoogle", prepared)
        publish.validate_published_html(prepared, Path("x.html"))

    def test_p06_repeated_body_paragraph_vs_shared_nav(self):
        long = " ".join(["This long generic paragraph repeats across many different guides word"] * 3)
        pages = {f"{i}.html": article(body=f"<p>{long}</p><p>unique {i}</p>") for i in range(3)}
        groups = quality.repeated_paragraphs(pages)
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]["pages"]), 3)
        # Footer/nav text is identical on every page but is never compared.
        self.assertFalse(any("Footer" in g["paragraph"] for g in groups))


class Batch(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.orig = {k: getattr(publish, k) for k in ("ROOT", "SCHEDULE", "BLOG_DIR", "QUEUE_DIR", "COST_DIR", "RISK_DIR")}
        publish.ROOT = self.tmp
        publish.SCHEDULE = self.tmp / "content-schedule.json"
        publish.BLOG_DIR = self.tmp / "blog"
        publish.QUEUE_DIR = self.tmp / ".github" / "content-queue"
        publish.COST_DIR = self.tmp / "cost"
        publish.RISK_DIR = self.tmp / "outdoor-risk"
        publish.BLOG_DIR.mkdir(parents=True)
        publish.QUEUE_DIR.mkdir(parents=True)

    def tearDown(self):
        for k, v in self.orig.items():
            setattr(publish, k, v)
        shutil.rmtree(self.tmp)

    def queue(self, items):
        manifest = []
        for slug, html, extra in items:
            (publish.QUEUE_DIR / f"{slug}.html").write_text(html, encoding="utf-8")
            manifest.append({"slug": slug, "queue_file": f".github/content-queue/{slug}.html",
                             "target_file": f"blog/{slug}.html", "publish_at": "2026-01-01T00:00:00+09:00",
                             "status": "scheduled", **extra})
        publish.SCHEDULE.write_text(json.dumps(manifest), encoding="utf-8")

    NOW = datetime(2026, 9, 1, tzinfo=timezone.utc)

    def test_p07_unapproved_due_item_is_not_published(self):
        self.queue([("a", article(), {})])
        published, blocked = publish.publish_due_posts(self.NOW)
        self.assertEqual(published, [])
        self.assertIn("editorial_status", blocked[0]["reason"])
        self.assertFalse((publish.BLOG_DIR / "a.html").exists())

    def test_p08_failing_item_does_not_break_the_batch(self):
        bad = article(body="<p>For quick answer engines only.</p>")
        self.queue([("good", article(), {"editorial_status": "approved"}),
                    ("bad", bad, {"editorial_status": "approved"})])
        published, blocked = publish.publish_due_posts(self.NOW)
        self.assertEqual(published, ["blog/good.html"])
        self.assertEqual(blocked[0]["target_file"], "blog/bad.html")
        manifest = {i["slug"]: i for i in json.loads(publish.SCHEDULE.read_text(encoding="utf-8"))}
        self.assertEqual(manifest["good"]["status"], "published")
        self.assertEqual(manifest["bad"]["status"], "scheduled")
        self.assertTrue((publish.QUEUE_DIR / "bad.html").exists())
        self.assertFalse((publish.QUEUE_DIR / "good.html").exists())
        self.assertFalse((publish.BLOG_DIR / "bad.html").exists())

    def test_p09_rerun_and_existing_target_are_safe(self):
        self.queue([("a", article(), {"editorial_status": "approved"})])
        (publish.BLOG_DIR / "a.html").write_text("reviewed original", encoding="utf-8")
        published, blocked = publish.publish_due_posts(self.NOW)
        self.assertEqual(published, [])
        self.assertEqual(blocked[0]["reason"], "target already exists")
        self.assertEqual((publish.BLOG_DIR / "a.html").read_text(encoding="utf-8"), "reviewed original")
        self.assertTrue((publish.QUEUE_DIR / "a.html").exists())

    def test_a01_dry_run_writes_nothing(self):
        self.queue([("a", article(), {"editorial_status": "approved"})])
        before = publish.SCHEDULE.read_text(encoding="utf-8")
        published, _ = publish.publish_due_posts(self.NOW, dry_run=True)
        self.assertEqual(published, ["blog/a.html"])
        self.assertFalse((publish.BLOG_DIR / "a.html").exists())
        self.assertEqual(publish.SCHEDULE.read_text(encoding="utf-8"), before)
        self.assertEqual(publish.main(["--dry-run"]), 0)  # no git: subprocess is blocked in tests

    def test_m01_m02_feed_is_newest_first_with_own_dates(self):
        for slug, day in (("aaa-old", "2026-06-01"), ("zzz-new", "2026-08-01"), ("mmm-mid", "2026-07-01")):
            (publish.BLOG_DIR / f"{slug}.html").write_text(article(title=slug, date_published=day), encoding="utf-8")
        publish.SCHEDULE.write_text("[]", encoding="utf-8")
        publish.rebuild_feed()
        root = ET.fromstring((self.tmp / "feed.xml").read_text(encoding="utf-8"))
        items = root.findall("./channel/item")
        self.assertEqual([i.findtext("title") for i in items], ["zzz-new", "mmm-mid", "aaa-old"])
        self.assertIn("01 Aug 2026", items[0].findtext("pubDate"))
        self.assertIn("01 Jun 2026", items[2].findtext("pubDate"))
        self.assertEqual(items[0].findtext("guid"), "https://dogbreedcost.com/blog/zzz-new.html")
        first = (self.tmp / "feed.xml").read_text(encoding="utf-8")
        publish.rebuild_feed()
        self.assertEqual((self.tmp / "feed.xml").read_text(encoding="utf-8"), first)

    def test_m03_m04_sitemap_keeps_unrelated_lastmod(self):
        (publish.BLOG_DIR / "old.html").write_text(article(), encoding="utf-8")
        (self.tmp / "sitemap.xml").write_text(meta.render_sitemap([
            ("https://dogbreedcost.com/", "2026-08-07"),
            ("https://dogbreedcost.com/blog/old.html", "2026-07-01"),
        ]), encoding="utf-8")
        publish.rebuild_sitemap(today="2026-09-29")
        lastmods = meta.read_lastmods((self.tmp / "sitemap.xml").read_text(encoding="utf-8"))
        self.assertEqual(lastmods["https://dogbreedcost.com/"], "2026-08-07")
        self.assertEqual(lastmods["https://dogbreedcost.com/blog/old.html"], "2026-07-01")
        self.assertEqual(lastmods["https://dogbreedcost.com/about/"], "2026-09-29")  # newly listed URL
        (publish.BLOG_DIR / "new.html").write_text(article(), encoding="utf-8")
        publish.rebuild_sitemap(changed_urls=["https://dogbreedcost.com/blog/new.html"], today="2026-09-30")
        lastmods = meta.read_lastmods((self.tmp / "sitemap.xml").read_text(encoding="utf-8"))
        self.assertEqual(lastmods["https://dogbreedcost.com/blog/new.html"], "2026-09-30")
        self.assertEqual(lastmods["https://dogbreedcost.com/blog/old.html"], "2026-07-01")
        self.assertEqual(lastmods["https://dogbreedcost.com/about/"], "2026-09-29")

    def test_m05_generator_sitemap_bumps_only_changed_urls(self):
        sitemap = self.tmp / "sitemap.xml"
        urls = ["https://dogbreedcost.com/cost/", "https://dogbreedcost.com/cost/a.html"]
        sitemap.write_text(meta.render_sitemap([(u, "2026-01-01") for u in urls]), encoding="utf-8")
        self.assertFalse(meta.update_sitemap_for_changes(sitemap, [], urls, "2026-09-29"))
        meta.update_sitemap_for_changes(sitemap, [urls[1]], urls, "2026-09-29")
        lastmods = meta.read_lastmods(sitemap.read_text(encoding="utf-8"))
        self.assertEqual(lastmods, {urls[0]: "2026-01-01", urls[1]: "2026-09-29"})

    def test_m06_xml_escaping(self):
        feed = meta.render_feed("https://x", [{"slug": "a.html", "title": 'Dogs & "Cats" <3', "description": "é ü",
                                                "published": datetime(2026, 1, 1, tzinfo=timezone.utc)}])
        item = ET.fromstring(feed).find("./channel/item")
        self.assertEqual(item.findtext("title"), 'Dogs & "Cats" <3')
        self.assertEqual(item.findtext("description"), "é ü")


if __name__ == "__main__":
    unittest.main()
