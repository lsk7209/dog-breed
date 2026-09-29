#!/usr/bin/env python3
"""Content quality checks for BreedWise HTML pages.

These checks find review candidates. They are not a Google quality score and do not
prove originality or policy compliance. Ad tags are deliberately not a quality check.

CLI:
    python scripts/content_quality.py --content-dir blog          # per-file issues
    python scripts/content_quality.py --content-dir blog --json   # machine-readable
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

# Writer/SEO instructions that should never reach readers. Matched case-insensitively
# against visible body text only (script/style/head excluded).
SCAFFOLD_PATTERNS = {
    "answer-engine instruction": re.compile(r"\b(quick\s+)?answer engines?\b", re.I),
    "keyword instruction": re.compile(r"\b(main|expanded|target|focus)\s+keywords?\b", re.I),
    "keyword guide heading": re.compile(r"why this keyword deserves", re.I),
    "AEO label": re.compile(r"\bAEO\b"),
    "quality score label": re.compile(r"\bquality (score|target)\b", re.I),
    "pre-publish label": re.compile(r"pre-publish quality check", re.I),
    "pSEO label": re.compile(r"\bp?SEO\b(?! -)", re.I),
    "search-positioning note": re.compile(r"instead of competing with existing|searchers are not looking|planning query for", re.I),
}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.anchors: list[str] = []
        self.h1 = 0
        self.canonicals: list[str] = []
        self.jsonld: list[str] = []
        self.paragraphs: list[str] = []
        self.visible: list[str] = []
        self._skip = 0  # inside script/style/head/nav/footer
        self._in_jsonld = False
        self._in_p = False
        self._p_buf: list[str] = []
        self._buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "a" and (a.get("href") or "").startswith("#") and len(a["href"]) > 1:
            self.anchors.append(a["href"][1:])
        if tag == "h1":
            self.h1 += 1
        if tag == "link" and a.get("rel") == "canonical":
            self.canonicals.append(a.get("href") or "")
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_jsonld = True
            self._buf = []
        if tag in ("script", "style", "head", "nav", "footer") and tag not in VOID_TAGS:
            self._skip += 1
        if tag == "p" and not self._skip:
            self._in_p = True
            self._p_buf = []

    def handle_endtag(self, tag):
        if tag == "script" and self._in_jsonld:
            self.jsonld.append("".join(self._buf))
            self._in_jsonld = False
        if tag in ("script", "style", "head", "nav", "footer") and self._skip:
            self._skip -= 1
        if tag == "p" and self._in_p:
            text = normalize_text("".join(self._p_buf))
            if text:
                self.paragraphs.append(text)
            self._in_p = False

    def handle_data(self, data):
        if self._in_jsonld:
            self._buf.append(data)
            return
        if self._skip:
            return
        self.visible.append(data)
        if self._in_p:
            self._p_buf.append(data)


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_page(html: str) -> _PageParser:
    parser = _PageParser()
    parser.feed(html)
    parser.close()
    return parser


def scaffold_leaks(html: str) -> list[dict[str, str]]:
    """Writer-instruction phrases in visible body text, with a short excerpt."""
    text = normalize_text(" ".join(parse_page(html).visible))
    leaks = []
    for label, pattern in SCAFFOLD_PATTERNS.items():
        for match in pattern.finditer(text):
            start = max(0, match.start() - 50)
            leaks.append({"type": label, "excerpt": text[start:match.end() + 50]})
    return leaks


def structure_issues(html: str, require_article: bool = True) -> list[str]:
    page = parse_page(html)
    issues = []
    if page.h1 != 1:
        issues.append(f"expected exactly one <h1>, found {page.h1}")
    if len(page.canonicals) != 1:
        issues.append(f"expected one canonical link, found {len(page.canonicals)}")
    elif not page.canonicals[0].startswith("https://"):
        issues.append("canonical href is empty or not absolute")
    if not re.search(r"<title>\s*\S", html):
        issues.append("empty or missing <title>")
    if not re.search(r'<meta name="description" content="[^"]+"', html):
        issues.append("empty or missing meta description")
    types = []
    for raw in page.jsonld:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as error:
            issues.append(f"invalid JSON-LD: {error.msg}")
            continue
        if not data:
            issues.append("empty JSON-LD block")
            continue
        types.append(data.get("@type") if isinstance(data, dict) else None)
    if require_article and "Article" not in types:
        issues.append("no Article JSON-LD")
    duplicates = sorted({i for i in page.ids if page.ids.count(i) > 1})
    if duplicates:
        issues.append("duplicate id(s): " + ", ".join(duplicates))
    missing = sorted(set(page.anchors) - set(page.ids))
    if missing:
        issues.append("in-page link target(s) missing: " + ", ".join(missing))
    return issues


def check_page(html: str, require_article: bool = True) -> dict[str, list]:
    return {"structure": structure_issues(html, require_article), "scaffold": scaffold_leaks(html)}


def repeated_paragraphs(pages: dict[str, str], min_words: int = 25, min_pages: int = 3) -> list[dict[str, object]]:
    """Long body paragraphs that appear verbatim (after normalizing proper nouns lightly) on many pages.

    Only <p> text outside nav/footer/head is compared, so shared navigation and footers
    do not count. This finds review candidates; it is not a plagiarism or quality score.
    """
    seen: dict[str, set[str]] = defaultdict(set)
    for name, html in pages.items():
        for paragraph in parse_page(html).paragraphs:
            if len(paragraph.split()) >= min_words:
                seen[paragraph.casefold()].add(name)
    return sorted(
        ({"paragraph": text[:160], "pages": sorted(names)} for text, names in seen.items() if len(names) >= min_pages),
        key=lambda item: -len(item["pages"]),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--content-dir", default="blog", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-article", action="store_true", help="do not require Article JSON-LD (Dataset/hub pages)")
    args = parser.parse_args()
    pages = {p.name: p.read_text(encoding="utf-8") for p in sorted(args.content_dir.glob("*.html")) if p.name != "index.html"}
    report = {"pagesChecked": len(pages), "pages": {}, "repeatedParagraphs": repeated_paragraphs(pages)}
    for name, html in pages.items():
        result = check_page(html, require_article=not args.no_article)
        if result["structure"] or result["scaffold"]:
            report["pages"][name] = result
    summary = {
        "pagesChecked": report["pagesChecked"],
        "pagesWithStructureIssues": sum(1 for r in report["pages"].values() if r["structure"]),
        "pagesWithScaffoldLeaks": sum(1 for r in report["pages"].values() if r["scaffold"]),
        "repeatedParagraphGroups": len(report["repeatedParagraphs"]),
    }
    print(json.dumps(report if args.json else summary, indent=2, ensure_ascii=False))
    return 1 if report["pages"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
