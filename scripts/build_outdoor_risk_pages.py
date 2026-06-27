from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
import json
import os
import re
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://dogbreedcost.com"
RISK_DIR = ROOT / "outdoor-risk"
DATA_DIR = ROOT / "data"
KST = timezone(timedelta(hours=9))
USER_AGENT = "dogbreedcost.com outdoor-risk contact@dogbreedcost.com"

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

LOCATIONS = {
    "phoenix-dog-heat-risk": {
        "city": "Phoenix",
        "state": "Arizona",
        "zip": "85004",
        "lat": 33.4484,
        "lon": -112.0740,
        "angle": "desert heat and pavement timing",
        "sensitive": "flat-faced dogs, senior dogs, dark-coated dogs, overweight dogs, and giant breeds",
        "local_notes": [
            "Phoenix heat can turn a normal afternoon walk into a paw and breathing-risk decision, especially when pavement stores heat after sunset.",
            "Owners should budget for early-morning routines, shade breaks, cooling mats, indoor enrichment, and backup exercise plans during hot stretches.",
            "High-energy breeds may still need work, but the work often has to move indoors or into short structured sessions instead of long exposed walks.",
        ],
    },
    "miami-dog-heat-humidity-risk": {
        "city": "Miami",
        "state": "Florida",
        "zip": "33130",
        "lat": 25.7617,
        "lon": -80.1918,
        "angle": "heat, humidity, storms, and air quality",
        "sensitive": "brachycephalic dogs, toy breeds on hot pavement, senior dogs, and dogs with breathing limits",
        "local_notes": [
            "Miami planning is not only about the high temperature. Humidity, storms, and air quality can make recovery harder after a walk.",
            "Owners should budget for towel drying, skin-fold care conversations, indoor play, shaded routes, and flexible walk timing.",
            "Flat-faced breeds may need a stricter stop rule because warm humid air can make ordinary exertion feel harder.",
        ],
    },
    "minneapolis-dog-cold-weather-risk": {
        "city": "Minneapolis",
        "state": "Minnesota",
        "zip": "55401",
        "lat": 44.9778,
        "lon": -93.2650,
        "angle": "cold exposure, ice, wind, and paw care",
        "sensitive": "toy breeds, thin-coated breeds, puppies, senior dogs, and dogs with joint stiffness",
        "local_notes": [
            "Minneapolis cold-weather planning often moves the cost from exercise time into gear, paw protection, traction, and indoor training.",
            "Small and thin-coated dogs may need shorter outings even when a larger double-coated breed is comfortable.",
            "Ice and wind matter for senior dogs because slipping or stiffness can turn a simple walk into a mobility problem.",
        ],
    },
    "denver-dog-outdoor-air-risk": {
        "city": "Denver",
        "state": "Colorado",
        "zip": "80202",
        "lat": 39.7392,
        "lon": -104.9903,
        "angle": "temperature swings, altitude, wind, and air quality",
        "sensitive": "high-drive sporting dogs, brachycephalic dogs, senior dogs, and dogs new to altitude",
        "local_notes": [
            "Denver owners should treat altitude, wind, temperature swings, and smoke episodes as part of the outdoor plan.",
            "A dog that handles a cool morning may still need a different plan later in the day when sun, wind, or AQI changes.",
            "Sporting and working breeds may need structured alternatives when outdoor intensity is not appropriate.",
        ],
    },
    "seattle-dog-rain-walk-risk": {
        "city": "Seattle",
        "state": "Washington",
        "zip": "98101",
        "lat": 47.6062,
        "lon": -122.3321,
        "angle": "rain routines, slick surfaces, and low-light walks",
        "sensitive": "long-coated dogs, low-clearance dogs, anxious dogs, and dogs needing consistent exercise",
        "local_notes": [
            "Seattle outdoor planning is often about consistency: rain, slick paths, darkness, and coat drying can quietly reduce exercise.",
            "Owners should budget for towels, drying space, reflective gear, paw checks, and enrichment that prevents rainy-day under-exercise.",
            "Low-clearance and long-coated dogs may need more cleanup and grooming support even when temperatures are mild.",
        ],
    },
}


def read_airnow_key() -> str:
    value = os.environ.get("AIRNOW_API_KEY", "").strip()
    key_file = Path("D:/env/airnow_api_key.txt")
    if not value and key_file.exists():
        value = key_file.read_text(encoding="ascii").strip()
    if not value:
        raise RuntimeError("AIRNOW_API_KEY is missing.")
    return value


def read_json(url: str, headers: dict[str, str] | None = None) -> object:
    request = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_nws(location: dict[str, object]) -> list[dict[str, object]]:
    point = read_json(
        f"https://api.weather.gov/points/{location['lat']},{location['lon']}",
        {"User-Agent": USER_AGENT, "Accept": "application/geo+json"},
    )
    forecast_url = point["properties"]["forecast"]
    forecast = read_json(forecast_url, {"User-Agent": USER_AGENT, "Accept": "application/geo+json"})
    periods = forecast.get("properties", {}).get("periods", [])
    return periods[:8]


def fetch_airnow(location: dict[str, object]) -> list[dict[str, object]]:
    key = read_airnow_key()
    query = urllib.parse.urlencode(
        {
            "format": "application/json",
            "zipCode": location["zip"],
            "distance": 25,
            "API_KEY": key,
        }
    )
    data = read_json(f"https://www.airnowapi.org/aq/observation/zipCode/current/?{query}")
    return data if isinstance(data, list) else []


def wind_mph(text: str) -> int:
    numbers = [int(value) for value in re.findall(r"\d+", text or "")]
    return max(numbers) if numbers else 0


def risk_score(periods: list[dict[str, object]], air: list[dict[str, object]]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    temps = [int(p.get("temperature", 0)) for p in periods if isinstance(p.get("temperature"), int)]
    max_temp = max(temps) if temps else 0
    min_temp = min(temps) if temps else 99
    max_wind = max((wind_mph(p.get("windSpeed", "")) for p in periods), default=0)
    precip = max((int(p.get("probabilityOfPrecipitation", {}).get("value") or 0) for p in periods), default=0)
    max_aqi = max((int(item.get("AQI", 0) or 0) for item in air), default=0)

    score = 0
    if max_temp >= 95:
        score += 3
        reasons.append(f"forecast high near {max_temp}F")
    elif max_temp >= 88:
        score += 2
        reasons.append(f"warm forecast near {max_temp}F")
    if min_temp <= 20:
        score += 3
        reasons.append(f"cold low near {min_temp}F")
    elif min_temp <= 34:
        score += 2
        reasons.append(f"cold conditions near {min_temp}F")
    if max_wind >= 25:
        score += 1
        reasons.append(f"wind up to {max_wind} mph")
    if precip >= 55:
        score += 1
        reasons.append(f"precipitation chance up to {precip}%")
    if max_aqi >= 151:
        score += 3
        reasons.append(f"AQI up to {max_aqi}")
    elif max_aqi >= 101:
        score += 2
        reasons.append(f"AQI up to {max_aqi}")

    if score >= 5:
        return "high", reasons or ["multiple outdoor stressors"]
    if score >= 2:
        return "moderate", reasons or ["some outdoor stressors"]
    return "low", reasons or ["no major stressor in the snapshot"]


def normalize() -> dict[str, object]:
    updated = datetime.now(KST).isoformat(timespec="seconds")
    pages: dict[str, object] = {}
    for slug, location in LOCATIONS.items():
        periods = fetch_nws(location)
        air = fetch_airnow(location)
        level, reasons = risk_score(periods, air)
        pages[slug] = {
            **location,
            "slug": slug,
            "risk_level": level,
            "reasons": reasons,
            "nws_periods": [
                {
                    "name": p.get("name"),
                    "temperature": p.get("temperature"),
                    "temperatureUnit": p.get("temperatureUnit"),
                    "windSpeed": p.get("windSpeed"),
                    "shortForecast": p.get("shortForecast"),
                    "probabilityOfPrecipitation": p.get("probabilityOfPrecipitation", {}).get("value"),
                }
                for p in periods
            ],
            "airnow": [
                {
                    "reportingArea": item.get("ReportingArea"),
                    "parameter": item.get("ParameterName"),
                    "aqi": item.get("AQI"),
                    "category": item.get("Category", {}).get("Name"),
                    "dateObserved": item.get("DateObserved"),
                    "hourObserved": item.get("HourObserved"),
                }
                for item in air
            ],
        }
    return {
        "updated": updated,
        "sources": ["NWS API", "AirNow API"],
        "pages": pages,
    }


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
        f'<a href="{prefix}blog/index.html">Blog</a><a href="{prefix}cost/index.html">Cost Data</a><a href="{prefix}outdoor-risk/index.html">Outdoor Risk</a>'
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


def risk_sentence(page: dict[str, object]) -> str:
    reasons = ", ".join(page["reasons"][:3])
    return f"The current outdoor risk snapshot for {page['city']}, {page['state']} is {page['risk_level']} because of {reasons}."


def render_index(dataset: dict[str, object]) -> str:
    description = "BreedWise outdoor-risk hub using NWS forecasts and AirNow AQI snapshots for dog walk planning."
    cards = []
    for slug, page in dataset["pages"].items():
        cards.append(
            f'<a class="blog-card" href="{slug}.html"><span class="tag">{escape(page["risk_level"].title())} risk</span>'
            f'<h2>{escape(page["city"])} dog outdoor risk</h2>'
            f'<p>{escape(risk_sentence(page))}</p><span class="read-more">Read snapshot</span></a>'
        )
    return (
        page_head("Dog Outdoor Risk Hub | Weather and AQI planning", description, f"{BASE_URL}/outdoor-risk/", "website")
        + nav("../")
        + f'<main><section class="pagehead"><div class="wrap"><p class="kicker">Outdoor Risk Data</p><h1>Weather and air-quality snapshots for safer dog walks.</h1><p class="lead">{escape(description)} Updated {escape(dataset["updated"])}.</p></div></section>'
        + '<section class="wrap" style="padding:46px 0"><div class="blog-grid">'
        + "\n".join(cards)
        + '</div><div class="note" style="margin-top:28px"><strong>Use this as a planning signal:</strong> forecast and AQI snapshots change. For urgent weather, smoke, heat, or health decisions, check local authorities and your veterinarian.</div></section></main>'
        + footer("../")
    )


def render_page(slug: str, page: dict[str, object], updated: str) -> str:
    title = f"{page['city']} Dog Outdoor Risk | Weather and AQI planning"
    description = f"{page['city']} dog outdoor risk snapshot using NWS forecast and AirNow AQI data for {page['angle']}."
    forecast_rows = "\n".join(
        "<tr><td>{name}</td><td>{temp}{unit}</td><td>{wind}</td><td>{precip}</td><td>{forecast}</td></tr>".format(
            name=escape(str(p.get("name") or "")),
            temp=escape(str(p.get("temperature") or "")),
            unit=escape(str(p.get("temperatureUnit") or "")),
            wind=escape(str(p.get("windSpeed") or "")),
            precip=escape("not listed" if p.get("probabilityOfPrecipitation") is None else f"{p.get('probabilityOfPrecipitation')}%"),
            forecast=escape(str(p.get("shortForecast") or "")),
        )
        for p in page["nws_periods"][:6]
    )
    aqi_rows = "\n".join(
        f"<tr><td>{escape(str(item.get('parameter') or 'AQI'))}</td><td>{escape(str(item.get('aqi') or ''))}</td><td>{escape(str(item.get('category') or ''))}</td><td>{escape(str(item.get('reportingArea') or ''))}</td></tr>"
        for item in page["airnow"]
    ) or '<tr><td colspan="4">No AirNow observation returned for this ZIP snapshot.</td></tr>'
    schema = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": title,
        "description": description,
        "url": f"{BASE_URL}/outdoor-risk/{slug}.html",
        "dateModified": updated,
        "creator": [{"@type": "Organization", "name": "National Weather Service"}, {"@type": "Organization", "name": "AirNow"}],
        "publisher": {"@type": "Organization", "name": "BreedWise"},
    }
    local_notes = "".join(f"<li>{escape(note)}</li>" for note in page["local_notes"])
    return (
        page_head(title, description, f"{BASE_URL}/outdoor-risk/{slug}.html")
        .replace("</head>", f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script></head>')
        + nav("../")
        + f'<main><section class="pagehead"><div class="wrap"><p class="breadcrumbs"><a href="../outdoor-risk/index.html">Outdoor Risk</a> / {escape(page["city"])}</p><p class="kicker">NWS + AirNow Snapshot</p><h1>{escape(page["city"])} dog outdoor risk</h1><p class="lead">{escape(description)}</p><div class="meta"><span>Risk: {escape(page["risk_level"].title())}</span><span>Updated: {escape(updated)}</span><span>Focus: {escape(page["angle"])}</span></div></div></section>'
        + '<div class="wrap content"><article class="article">'
        + f'<div class="callout"><strong>Short answer:</strong> {escape(risk_sentence(page))} Use shorter outings, shade, water, paw checks, and schedule changes when the signal is moderate or high.</div>'
        + f'<h2 id="who-needs-care">Dogs that need extra care in {escape(page["city"])}</h2><p>This page is most useful for {escape(page["sensitive"])}. The forecast is not a medical rule, but it helps owners decide whether a normal walk should become a shorter potty break, an indoor enrichment session, or a cooler-time outing.</p>'
        + '<h2 id="walk-plan">How to use the snapshot before a walk</h2><ul><li>Check the warmest or coldest forecast period before choosing the route.</li><li>Watch air quality for dogs with breathing, heart, age, or stamina limits.</li><li>Use pavement, wind, rain, and visibility as practical constraints, not just the headline temperature.</li><li>Bring water and choose a route that lets the dog stop early without forcing a long return.</li></ul>'
        + f'<h2 id="breed-planning">Breed and cost planning angle</h2><p>Outdoor constraints can become ownership costs. A household may need cooling gear, paw protection, indoor enrichment, paid walkers at safer hours, grooming support, or training help when weather blocks normal exercise. That matters before choosing a breed, especially for high-energy dogs or dogs with heat, cold, or breathing limits.</p>'
        + f'<h2 id="local-planning">Local planning notes for {escape(page["city"])}</h2><p>The same forecast can mean different things for different dogs. A young athletic dog, a senior toy breed, a flat-faced companion breed, and a thick-coated working breed do not use the same outdoor plan. Use the local notes below to translate the public data into a practical owner decision.</p><ul>{local_notes}</ul>'
        + '<h2 id="budget-check">Budget checks this weather can create</h2><p>Weather rarely appears as a single line item in a dog budget, but it changes the support system around the dog. Heat can create cooling and indoor-enrichment costs. Cold can create coat, boot, traction, and joint-comfort costs. Rain can create grooming and drying costs. Bad air quality can create more indoor activity needs and stricter walk timing. These are not reasons to avoid a breed automatically; they are reasons to include the environment in the ownership plan before adoption.</p>'
        + '<h2 id="mistakes">Common owner mistakes to avoid</h2><ul><li>Do not treat the forecast high as the only risk; pavement, humidity, wind, and AQI can matter more during the actual walk.</li><li>Do not assume a tired dog is safely exercised. Heat, smoke, cold, or slick surfaces can create stress without providing healthy enrichment.</li><li>Do not buy a high-energy breed unless the household has indoor work, training games, or safe-time exercise options for difficult weather days.</li><li>Do not wait for a problem before pricing backup care, grooming support, paw gear, or cooling equipment.</li></ul>'
        + f'<h2 id="forecast">NWS forecast snapshot</h2><table class="table"><thead><tr><th>Period</th><th>Temp</th><th>Wind</th><th>Rain/snow chance</th><th>Forecast</th></tr></thead><tbody>{forecast_rows}</tbody></table>'
        + f'<h2 id="air">AirNow AQI snapshot</h2><table class="table"><thead><tr><th>Parameter</th><th>AQI</th><th>Category</th><th>Area</th></tr></thead><tbody>{aqi_rows}</tbody></table>'
        + '<h2 id="limits">Source limits</h2><p>Data comes from the National Weather Service API and AirNow API. Forecasts and AQI observations can change quickly, and this page is educational planning content only. It does not replace emergency weather warnings, public-health guidance, or veterinary advice.</p>'
        + '</article><aside class="toc" aria-label="Article contents"><strong>Contents</strong><a href="#who-needs-care">Dogs needing care</a><a href="#walk-plan">Walk plan</a><a href="#breed-planning">Breed planning</a><a href="#local-planning">Local notes</a><a href="#budget-check">Budget checks</a><a href="#mistakes">Mistakes</a><a href="#forecast">Forecast</a><a href="#air">AQI</a><a href="#limits">Limits</a><hr><strong>Next steps</strong><a href="../outdoor-risk/index.html">Outdoor hub</a><a href="../cost/index.html">Cost data</a><a href="../blog/index.html">BreedWise guides</a></aside></div></main>'
        + footer("../")
    )


def update_sitemap(dataset: dict[str, object]) -> None:
    sitemap = ROOT / "sitemap.xml"
    text = sitemap.read_text(encoding="utf-8")
    today = datetime.now(KST).date().isoformat()
    urls = [f"{BASE_URL}/outdoor-risk/"] + [f"{BASE_URL}/outdoor-risk/{slug}.html" for slug in dataset["pages"]]
    existing = set(re.findall(r"<loc>(.*?)</loc>", text))
    for url in urls:
        pattern = rf"(<url><loc>{re.escape(url)}</loc><lastmod>)([^<]+)(</lastmod></url>)"
        text = re.sub(pattern, rf"\g<1>{today}\g<3>", text)
    additions = "\n".join(f"  <url><loc>{url}</loc><lastmod>{today}</lastmod></url>" for url in urls if url not in existing)
    if additions:
        text = text.replace("</urlset>", f"{additions}\n</urlset>")
    sitemap.write_text(text, encoding="utf-8")


def main() -> int:
    RISK_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)
    dataset = normalize()
    (DATA_DIR / "dog_outdoor_risk.json").write_text(json.dumps(dataset, indent=2, ensure_ascii=False), encoding="utf-8")
    (RISK_DIR / "index.html").write_text(render_index(dataset), encoding="utf-8")
    for slug, page in dataset["pages"].items():
        (RISK_DIR / f"{slug}.html").write_text(render_page(slug, page, dataset["updated"]), encoding="utf-8")
    update_sitemap(dataset)
    print(json.dumps({"ok": True, "updated": dataset["updated"], "pages": list(dataset["pages"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
