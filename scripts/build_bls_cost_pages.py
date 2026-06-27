from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
import json
import os
import re
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://dogbreedcost.com"
COST_DIR = ROOT / "cost"
DATA_DIR = ROOT / "data"
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
HEAD_TAGS = ADSENSE_LOADER + GA4_TAG + FEED_LINK + VERIFICATION_TAGS

SERIES = {
    "pet-food-inflation": {
        "series_id": "CUUR0000SS61031",
        "title": "Pet Food Inflation Index",
        "headline": "Pet Food Inflation Index for Dog Owners",
        "description": "Track BLS CPI changes for pet food and treats, with practical dog ownership budgeting notes.",
        "intent": "dog food budget planning",
        "owner_note": "Food is a recurring cost, so even modest CPI movement compounds when a household feeds a medium or large dog every month.",
        "breed_examples": [
            "Large and giant breeds make this signal more important because the monthly food base is already high.",
            "Food-motivated breeds such as Labrador Retrievers also need portion discipline, not only a larger food line item.",
            "Sensitive-stomach diets, prescription diets, and brand changes should be discussed with a veterinarian instead of inferred from CPI.",
        ],
        "questions": [
            "What adult weight range is realistic for the dog, not just the puppy?",
            "How many cups or calories does the current food plan require each day?",
            "Can the household absorb a 12-month food cost increase without reducing preventive care?",
        ],
    },
    "pet-supplies-inflation": {
        "series_id": "CUUR0000SS61032",
        "title": "Pet Supplies Inflation Index",
        "headline": "Pet Supplies Inflation Index for Dog Setup Costs",
        "description": "Track BLS CPI changes for pets, pet supplies, and accessories, with setup-budget notes for dog owners.",
        "intent": "dog supplies budget planning",
        "owner_note": "Supply inflation matters most in the first year, when owners buy crates, beds, leashes, grooming tools, gates, bowls, and replacement equipment.",
        "breed_examples": [
            "Puppies and rescue dogs often need extra setup spending because the owner is still learning what the dog destroys, ignores, or outgrows.",
            "Strong chewers, giant breeds, and escape-prone dogs can turn inexpensive gear into repeat purchases.",
            "Apartment owners should treat gates, crates, cleaning tools, and noise-management supplies as part of the real setup cost.",
        ],
        "questions": [
            "Which supplies are one-time purchases, and which are likely to be replaced every few months?",
            "Does the breed or individual dog need sturdier gear than the cheapest starter kit?",
            "Will the home need gates, ramps, traction mats, or crate upgrades before the dog is fully settled?",
        ],
    },
    "pet-services-inflation": {
        "series_id": "CUUR0000SS62053",
        "title": "Pet Services Inflation Index",
        "headline": "Pet Services Inflation Index for Dog Care Budgets",
        "description": "Track BLS CPI changes for pet services, with planning notes for grooming, boarding, walking, and care support.",
        "intent": "dog service cost planning",
        "owner_note": "Service inflation can affect owners who rely on grooming, boarding, daycare, walkers, or paid backup care during travel and schedule changes.",
        "breed_examples": [
            "Grooming-intensive breeds can feel affordable at adoption and then become service-heavy because coat care repeats on a calendar.",
            "High-energy dogs may need walkers, daycare, training classes, or sport outlets when the owner schedule is not enough.",
            "Brachycephalic, senior, giant, anxious, or medication-dependent dogs may need more careful boarding and sitter screening.",
        ],
        "questions": [
            "Which services are optional convenience, and which are required for this dog's health, coat, or behavior?",
            "What happens during travel, illness, long workdays, or a family emergency?",
            "Can the household pay for professional help before a behavior or grooming problem becomes harder to fix?",
        ],
    },
}


def read_key() -> str:
    key = os.environ.get("BLS_API_KEY", "").strip()
    key_file = Path("D:/env/bls_api_key.txt")
    if not key and key_file.exists():
        key = key_file.read_text(encoding="ascii").strip()
    if not key:
        raise RuntimeError("BLS_API_KEY is missing. Set it in the environment or D:/env/bls_api_key.txt.")
    return key


def fetch_bls() -> dict[str, object]:
    key = read_key()
    now = datetime.now(KST)
    payload = {
        "seriesid": [item["series_id"] for item in SERIES.values()],
        "startyear": str(now.year - 3),
        "endyear": str(now.year),
        "catalog": True,
        "calculations": True,
        "registrationkey": key,
    }
    request = urllib.request.Request(
        "https://api.bls.gov/publicAPI/v2/timeseries/data/",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
    if result.get("status") != "REQUEST_SUCCEEDED":
        raise RuntimeError(f"BLS request failed: {result.get('message')}")
    return result


def normalize_data(raw: dict[str, object]) -> dict[str, object]:
    by_id = {item["series_id"]: slug for slug, item in SERIES.items()}
    updated = datetime.now(KST).date().isoformat()
    pages: dict[str, object] = {}
    for series in raw.get("Results", {}).get("series", []):
        slug = by_id.get(series.get("seriesID"))
        if not slug:
            continue
        data = [row for row in series.get("data", []) if row.get("period", "").startswith("M") and row.get("value") != "-"]
        latest = data[0]
        previous_year = next((row for row in data if row.get("year") == str(int(latest["year"]) - 1) and row.get("period") == latest.get("period")), None)
        yoy = None
        if previous_year:
            yoy = (float(latest["value"]) / float(previous_year["value"]) - 1) * 100
        pages[slug] = {
            **SERIES[slug],
            "catalog": series.get("catalog", {}),
            "latest": {
                "year": latest["year"],
                "period": latest["periodName"],
                "value": latest["value"],
                "pct_changes": latest.get("calculations", {}).get("pct_changes", {}),
                "year_over_year_same_month": None if yoy is None else round(yoy, 1),
            },
            "history": [
                {
                    "year": row["year"],
                    "period": row["periodName"],
                    "value": row["value"],
                }
                for row in data[:14]
            ],
        }
    return {"updated": updated, "source": "BLS Public Data API v2", "pages": pages}


def period_label(page: dict[str, object]) -> str:
    latest = page["latest"]
    return f"{latest['period']} {latest['year']}"


def pct_text(page: dict[str, object], key: str) -> str:
    value = page["latest"].get("pct_changes", {}).get(key)
    return "not available" if value in (None, "") else f"{float(value):.1f}%"


def page_head(title: str, description: str, canonical: str, kind: str = "article") -> str:
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{escape(title)}</title><meta name=\"description\" content=\"{escape(description)}\">"
        '<link rel="stylesheet" href="../assets/site.css">'
        f'<link rel="canonical" href="{canonical}"><meta name="robots" content="index,follow">'
        f'<meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(description)}">'
        f'<meta property="og:type" content="{kind}"><meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#2f6b54">'
        f"{HEAD_TAGS}</head>"
    )


def nav(prefix: str = "../") -> str:
    return (
        '<body><header class="topbar"><nav class="nav" aria-label="Primary">'
        f'<a class="brand" href="{prefix}index.html"><span class="mark" aria-hidden="true"></span><span>BreedWise</span></a>'
        '<div class="navlinks">'
        f'<a href="{prefix}blog/index.html">Blog</a><a href="{prefix}cost/index.html">Cost Data</a>'
        f'<a href="{prefix}methodology/index.html">Methodology</a><a href="{prefix}about/index.html">About</a>'
        f'<a href="{prefix}contact/index.html">Contact</a><a href="{prefix}privacy-policy/index.html">Privacy</a>'
        f'<a href="{prefix}disclosures/index.html">Disclosures</a></div></nav></header>'
    )


def footer(prefix: str = "../") -> str:
    return (
        '<footer class="footer"><div class="wrap"><span>&copy; 2026 BreedWise. Informational planning content only.</span>'
        f'<span><a href="{prefix}terms/index.html">Terms</a> &middot; <a href="{prefix}privacy-policy/index.html">Privacy Policy</a> &middot; '
        f'<a href="{prefix}disclosures/index.html">Disclosures</a> &middot; <a href="{prefix}contact/index.html">Contact</a></span></div></footer></body></html>'
    )


def render_index(dataset: dict[str, object]) -> str:
    cards = []
    for slug, page in dataset["pages"].items():
        cards.append(
            f'<a class="blog-card" href="{slug}.html"><span class="tag">BLS CPI</span>'
            f"<h2>{escape(page['headline'])}</h2>"
            f"<p>{escape(page['description'])}</p><span class=\"read-more\">Read data note</span></a>"
        )
    description = "BreedWise public-data cost hub using BLS CPI series for pet food, pet supplies, and pet services."
    return (
        page_head("Dog Cost Data Hub | BLS pet CPI indicators", description, f"{BASE_URL}/cost/", "website")
        + nav("../")
        + f'<main><section class="pagehead"><div class="wrap"><p class="kicker">Public Data Cost Hub</p><h1>Dog cost planning with BLS pet CPI indicators.</h1>'
        + f'<p class="lead">{escape(description)} Updated {escape(dataset["updated"])} from the BLS Public Data API.</p></div></section>'
        + '<section class="wrap" style="padding:46px 0"><div class="blog-grid">'
        + "\n".join(cards)
        + '</div><div class="note" style="margin-top:28px"><strong>How to use this:</strong> CPI movement is not a personal quote. Use it to pressure-test recurring dog budgets, then confirm local prices with veterinarians, groomers, stores, trainers, and boarding providers.</div></section></main>'
        + footer("../")
    )


def render_page(slug: str, page: dict[str, object], updated: str) -> str:
    latest = page["latest"]
    rows = "\n".join(
        f"<tr><td>{escape(row['period'])} {escape(row['year'])}</td><td>{escape(row['value'])}</td></tr>"
        for row in page["history"][:12]
    )
    title = f"{page['headline']} | BLS CPI data"
    canonical = f"{BASE_URL}/cost/{slug}.html"
    schema = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": page["headline"],
        "description": page["description"],
        "url": canonical,
        "dateModified": updated,
        "creator": {"@type": "Organization", "name": "U.S. Bureau of Labor Statistics"},
        "publisher": {"@type": "Organization", "name": "BreedWise"},
        "isBasedOn": "https://api.bls.gov/publicAPI/v2/timeseries/data/",
    }
    yoy = latest.get("year_over_year_same_month")
    yoy_text = "not available" if yoy is None else f"{yoy:.1f}%"
    examples = "".join(f"<li>{escape(item)}</li>" for item in page["breed_examples"])
    questions = "".join(f"<li>{escape(item)}</li>" for item in page["questions"])
    return (
        page_head(title, page["description"], canonical)
        .replace("</head>", f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script></head>')
        + nav("../")
        + f'<main><section class="pagehead"><div class="wrap"><p class="breadcrumbs"><a href="../cost/index.html">Cost Data</a> / BLS CPI</p><p class="kicker">BLS CPI Series {escape(page["series_id"])}</p>'
        + f"<h1>{escape(page['headline'])}</h1><p class=\"lead\">{escape(page['description'])}</p>"
        + f'<div class="meta"><span>Latest: {escape(period_label(page))}</span><span>Index value: {escape(latest["value"])}</span><span>12-month API change: {escape(pct_text(page, "12"))}</span></div></div></section>'
        + '<div class="wrap content"><article class="article">'
        + f'<div class="callout"><strong>Short answer:</strong> The latest BLS CPI reading for {escape(page["catalog"].get("item", page["title"]))} is {escape(latest["value"])} for {escape(period_label(page))}. The BLS API reports a 12-month change of {escape(pct_text(page, "12"))}; the same-month year-over-year calculation from the downloaded series is {escape(yoy_text)}.</div>'
        + f'<h2 id="what-it-means">What this means for dog owners</h2><p>{escape(page["owner_note"])}</p><p>This page is not a price quote and does not estimate a single household bill. It turns a public inflation series into a planning signal that can be paired with breed size, grooming needs, health-risk questions, and local care access.</p>'
        + f'<h2 id="budget-use">How to use this in a dog budget</h2><ul><li>Update recurring categories before choosing a breed, especially food and service-heavy breeds.</li><li>Keep a separate local quote for veterinary care, grooming, boarding, and training because CPI is a national index.</li><li>Use the <a href="../blog/five-year-dog-ownership-cost-framework.html">five-year dog ownership cost framework</a> to turn this index into a household budget review.</li></ul>'
        + f'<h2 id="breed-planning">Breed planning examples</h2><p>The value of this page is not the index number alone. The useful step is connecting the public-data trend to the kind of dog the household is considering. A small companion dog, a giant breed, a working dog, and a grooming-intensive breed can all face the same national CPI environment while creating very different household exposure.</p><ul>{examples}</ul>'
        + f'<h2 id="decision-checklist">Questions before choosing a breed</h2><p>Use these questions before expanding the shortlist. They help turn a general inflation signal into a concrete ownership plan.</p><ul>{questions}</ul>'
        + '<h2 id="what-not-to-infer">What not to infer from this data</h2><p>This CPI series does not say which breed is cheap, which owner should buy insurance, or what one local clinic, groomer, trainer, boarder, retailer, or shelter will charge. It also does not diagnose medical risk or predict an individual dog. Treat the data as a pressure test: if a budget only works when every recurring cost stays flat, the plan needs a larger reserve before adoption.</p>'
        + '<p>For stronger planning, combine this public-data page with written quotes, local rules, veterinary records, breeder or rescue documentation, and a realistic weekly care schedule. The best use of pSEO here is not to mass-produce pages; it is to make each public-data page answer one narrow cost question with enough context that a future owner can act on it.</p>'
        + f'<h2 id="recent-readings">Recent BLS readings</h2><table class="table"><thead><tr><th>Period</th><th>CPI index</th></tr></thead><tbody>{rows}</tbody></table>'
        + f'<h2 id="source">Source and limits</h2><p>Data source: U.S. Bureau of Labor Statistics Public Data API v2, CPI-U, U.S. city average, not seasonally adjusted. Series title from the API catalog: {escape(page["catalog"].get("series_title", ""))}.</p><p>BreedWise uses this as educational planning context only. It should not replace a veterinarian, insurer, groomer, trainer, retailer, landlord, or local service provider quote.</p>'
        + '</article><aside class="toc" aria-label="Article contents"><strong>Contents</strong><a href="#what-it-means">What this means</a><a href="#budget-use">Budget use</a><a href="#breed-planning">Breed planning</a><a href="#decision-checklist">Questions</a><a href="#what-not-to-infer">Limits</a><a href="#recent-readings">Recent readings</a><a href="#source">Source and limits</a><hr><strong>Next steps</strong><a href="../cost/index.html">Cost data hub</a><a href="../blog/index.html">BreedWise guides</a><a href="../methodology/index.html">Methodology</a></aside></div></main>'
        + footer("../")
    )


def update_sitemap(dataset: dict[str, object]) -> None:
    sitemap = ROOT / "sitemap.xml"
    text = sitemap.read_text(encoding="utf-8")
    today = datetime.now(KST).date().isoformat()
    urls = [f"{BASE_URL}/cost/"] + [f"{BASE_URL}/cost/{slug}.html" for slug in dataset["pages"]]
    existing = set(re.findall(r"<loc>(.*?)</loc>", text))
    additions = "\n".join(f"  <url><loc>{url}</loc><lastmod>{today}</lastmod></url>" for url in urls if url not in existing)
    if additions:
        text = text.replace("</urlset>", f"{additions}\n</urlset>")
        sitemap.write_text(text, encoding="utf-8")


def main() -> int:
    COST_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)
    dataset = normalize_data(fetch_bls())
    (DATA_DIR / "bls_pet_cost_cpi.json").write_text(json.dumps(dataset, indent=2, ensure_ascii=False), encoding="utf-8")
    (COST_DIR / "index.html").write_text(render_index(dataset), encoding="utf-8")
    for slug, page in dataset["pages"].items():
        (COST_DIR / f"{slug}.html").write_text(render_page(slug, page, dataset["updated"]), encoding="utf-8")
    update_sitemap(dataset)
    print(json.dumps({"ok": True, "updated": dataset["updated"], "pages": list(dataset["pages"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
