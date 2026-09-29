#!/usr/bin/env python3
"""Fail when published blog pages contain duplicate H2s, stale scaffold labels, or broken in-page links.

This is a structural heading check only. It does not measure originality or content quality;
use scripts/content_quality.py for visible writer-instruction leaks and repeated paragraphs.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


H2_RE = re.compile(r"<h2\b(?P<attrs>[^>]*)>(?P<content>.*?)</h2>", re.IGNORECASE | re.DOTALL)
ID_RE = re.compile(r"\bid\s*=\s*['\"](?P<id>[^'\"]+)['\"]", re.IGNORECASE)
ANCHOR_RE = re.compile(
    r"<a\b[^>]*\bhref\s*=\s*['\"]#(?P<target>[^'\"]+)['\"][^>]*>(?P<content>.*?)</a>",
    re.IGNORECASE | re.DOTALL,
)
TAG_RE = re.compile(r"<[^>]+>")
SCAFFOLD_LABELS = (
    "Pre-publish quality check",
    "Why this keyword deserves its own guide",
)


def normalize_heading(value: str) -> str:
    text = TAG_RE.sub(" ", value)
    return re.sub(r"\s+", " ", text).strip().casefold()


def audit_file(path: Path) -> dict[str, object] | None:
    html = path.read_text(encoding="utf-8")
    h2_matches = list(H2_RE.finditer(html))
    h2_by_id = {
        id_match.group("id"): normalize_heading(match.group("content"))
        for match in h2_matches
        if (id_match := ID_RE.search(match.group("attrs")))
    }
    headings = [normalize_heading(match.group("content")) for match in h2_matches]
    duplicates = sorted(heading for heading, count in Counter(headings).items() if count > 1)
    stale_labels = [label for label in SCAFFOLD_LABELS if label.casefold() in html.casefold()]
    toc_mismatches = [
        {"target": match.group("target"), "label": normalize_heading(match.group("content")), "heading": h2_by_id[match.group("target")]}
        for match in ANCHOR_RE.finditer(html)
        if match.group("target") in h2_by_id
        and normalize_heading(match.group("content")) != h2_by_id[match.group("target")]
    ]
    all_ids = {m.group("id") for m in ID_RE.finditer(html)}
    missing_targets = sorted({m.group("target") for m in ANCHOR_RE.finditer(html)} - all_ids)
    if not duplicates and not stale_labels and not toc_mismatches and not missing_targets:
        return None
    return {
        "path": path.as_posix(),
        "duplicateH2": duplicates,
        "staleScaffoldLabels": stale_labels,
        "tocLabelMismatches": toc_mismatches,
        "missingAnchorTargets": missing_targets,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content-dir", default="blog", type=Path)
    args = parser.parse_args()

    pages = sorted(args.content_dir.glob("*.html"))
    failures = [result for path in pages if (result := audit_file(path))]
    report = {"pagesChecked": len(pages), "failures": failures}
    print(json.dumps(report, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
