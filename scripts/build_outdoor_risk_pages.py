from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
import json
import math
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_metadata  # noqa: E402


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


SECRET_QUERY_KEYS = {"api_key", "apikey", "registrationkey", "token", "key"}
# Number of NWS forecast periods that are both evaluated and displayed. Keeping one
# constant avoids a label that is driven by periods the reader cannot see.
FORECAST_PERIODS = 8
# Labels the site may emit. "incomplete" and "unavailable" are never safety claims.
RISK_LEVELS = ("low", "moderate", "high", "incomplete", "unavailable")


def redact_url(url: str) -> str:
    """Remove credential-like query values before a URL is placed in logs or errors."""
    parts = urllib.parse.urlsplit(url)
    if not parts.query:
        return url
    query = [
        (key, "REDACTED" if key.lower() in SECRET_QUERY_KEYS else value)
        for key, value in urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    ]
    return urllib.parse.urlunsplit(parts._replace(query=urllib.parse.urlencode(query)))


def read_json(url: str, headers: dict[str, str] | None = None, retries: int = 3) -> object:
    request = urllib.request.Request(url, headers=headers or {})
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except (TimeoutError, urllib.error.URLError) as error:
            last_error = error
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    # Chain only the error type name: urllib errors can embed the full request URL.
    raise RuntimeError(
        f"Failed to fetch {redact_url(url)} after {retries} attempts ({type(last_error).__name__})"
    ) from None


def fetch_nws(location: dict[str, object]) -> tuple[list[dict[str, object]], dict[str, object]]:
    point = read_json(
        f"https://api.weather.gov/points/{location['lat']},{location['lon']}",
        {"User-Agent": USER_AGENT, "Accept": "application/geo+json"},
    )
    forecast_url = point["properties"]["forecast"]
    forecast = read_json(forecast_url, {"User-Agent": USER_AGENT, "Accept": "application/geo+json"})
    properties = forecast.get("properties", {}) if isinstance(forecast, dict) else {}
    periods = properties.get("periods", []) if isinstance(properties.get("periods"), list) else []
    meta = {
        "generatedAt": properties.get("generatedAt"),
        "updateTime": properties.get("updateTime"),
    }
    return periods[:FORECAST_PERIODS], meta


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


def finite_number(value: object) -> float | None:
    """Return a finite real number, or None. Booleans and non-finite values are rejected."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def temperature_f(period: dict[str, object]) -> float | None:
    value = finite_number(period.get("temperature"))
    if value is None:
        return None
    unit = str(period.get("temperatureUnit") or "F").upper()
    if unit == "F":
        return value
    if unit == "C":
        return value * 9 / 5 + 32
    return None  # Unknown unit: do not guess.


def precip_value(period: dict[str, object]) -> float | None:
    raw = period.get("probabilityOfPrecipitation")
    if isinstance(raw, dict):
        raw = raw.get("value")
    return finite_number(raw)


def aqi_value(item: dict[str, object]) -> float | None:
    raw = item.get("AQI", item.get("aqi"))
    value = finite_number(raw)
    # AirNow uses negative sentinels (for example -1) for missing values.
    return value if value is not None and value >= 0 else None


def source_status(periods: list[dict[str, object]], air: list[dict[str, object]]) -> dict[str, str]:
    weather_ok = any(temperature_f(p) is not None for p in periods)
    air_ok = any(aqi_value(item) is not None for item in air)
    if weather_ok and air_ok:
        overall = "available"
    elif weather_ok or air_ok:
        overall = "partial"
    else:
        overall = "unavailable"
    return {
        "weather": "available" if weather_ok else "unavailable",
        "air_quality": "available" if air_ok else "unavailable",
        "overall": overall,
    }


def fmt_number(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else f"{value:.1f}"


def risk_score(periods: list[dict[str, object]], air: list[dict[str, object]]) -> tuple[str, list[str]]:
    """Return the site's planning label and the reasons behind it.

    The label is a BreedWise planning aid, not an official classification. Missing inputs
    never default to a benign value: without usable forecast temperatures the result is
    "unavailable"; without a usable AQI observation it is "incomplete".
    """
    reasons: list[str] = []
    status = source_status(periods, air)
    if status["weather"] == "unavailable":
        reasons.append("no usable NWS forecast temperature in this snapshot")
        if status["air_quality"] == "unavailable":
            reasons.append("no usable AirNow AQI observation in this snapshot")
        return "unavailable", reasons

    temps = [t for t in (temperature_f(p) for p in periods) if t is not None]
    max_temp = max(temps)
    min_temp = min(temps)
    max_wind = max((wind_mph(str(p.get("windSpeed") or "")) for p in periods), default=0)
    precips = [v for v in (precip_value(p) for p in periods) if v is not None]
    precip = max(precips) if precips else None
    aqis = [v for v in (aqi_value(item) for item in air) if v is not None]
    max_aqi = max(aqis) if aqis else None

    score = 0
    if max_temp >= 95:
        score += 3
        reasons.append(f"forecast high near {fmt_number(max_temp)}F")
    elif max_temp >= 88:
        score += 2
        reasons.append(f"warm forecast near {fmt_number(max_temp)}F")
    if min_temp <= 20:
        score += 3
        reasons.append(f"cold low near {fmt_number(min_temp)}F")
    elif min_temp <= 34:
        score += 2
        reasons.append(f"cold conditions near {fmt_number(min_temp)}F")
    if max_wind >= 25:
        score += 1
        reasons.append(f"wind up to {max_wind} mph")
    if precip is not None and precip >= 55:
        score += 1
        reasons.append(f"precipitation chance up to {fmt_number(precip)}%")
    if max_aqi is not None and max_aqi >= 151:
        score += 3
        reasons.append(f"AQI up to {fmt_number(max_aqi)}")
    elif max_aqi is not None and max_aqi >= 101:
        score += 2
        reasons.append(f"AQI up to {fmt_number(max_aqi)}")

    if max_aqi is None:
        # Weather reasons are still reported, but no overall label is implied.
        reasons.append("no usable AirNow AQI observation in this snapshot")
        return "incomplete", reasons
    if score >= 5:
        return "high", reasons or ["multiple planning thresholds crossed"]
    if score >= 2:
        return "moderate", reasons or ["some planning thresholds crossed"]
    return "low", reasons or ["no listed input crossed the site's planning thresholds"]


def normalize_period(p: dict[str, object]) -> dict[str, object]:
    return {
        "name": p.get("name"),
        "startTime": p.get("startTime"),
        "endTime": p.get("endTime"),
        "temperature": p.get("temperature"),
        "temperatureUnit": p.get("temperatureUnit"),
        "windSpeed": p.get("windSpeed"),
        "shortForecast": p.get("shortForecast"),
        "probabilityOfPrecipitation": precip_value(p),
    }


def normalize_air(item: dict[str, object]) -> dict[str, object]:
    category = item.get("Category")
    return {
        "reportingArea": item.get("ReportingArea"),
        "parameter": item.get("ParameterName"),
        "aqi": aqi_value(item),
        "category": category.get("Name") if isinstance(category, dict) else None,
        "dateObserved": item.get("DateObserved"),
        "hourObserved": item.get("HourObserved"),
        "localTimeZone": item.get("LocalTimeZone"),
    }


def build_page(slug: str, location: dict[str, object], periods: list[dict[str, object]],
               forecast_meta: dict[str, object], air: list[dict[str, object]]) -> dict[str, object]:
    level, reasons = risk_score(periods, air)
    return {
        **location,
        "slug": slug,
        "risk_level": level,
        "reasons": reasons,
        "data_status": source_status(periods, air),
        "forecast_generated_at": forecast_meta.get("generatedAt"),
        "forecast_updated_at": forecast_meta.get("updateTime"),
        "nws_periods": [normalize_period(p) for p in periods],
        "airnow": [normalize_air(item) for item in air],
    }


def normalize() -> dict[str, object]:
    updated = datetime.now(KST).isoformat(timespec="seconds")
    pages: dict[str, object] = {}
    for slug, location in LOCATIONS.items():
        periods, forecast_meta = fetch_nws(location)
        air = fetch_airnow(location)
        pages[slug] = build_page(slug, location, periods, forecast_meta, air)
    return {
        "updated": updated,
        "sources": ["NWS API", "AirNow API"],
        "pages": pages,
    }


def page_data_status(page: dict[str, object]) -> dict[str, str]:
    """Status stored at collection time, or derived from normalized rows for older snapshots."""
    stored = page.get("data_status")
    if isinstance(stored, dict) and stored.get("overall"):
        return stored
    periods = [{"temperature": p.get("temperature"), "temperatureUnit": p.get("temperatureUnit")} for p in page.get("nws_periods", [])]
    air = [{"AQI": item.get("aqi")} for item in page.get("airnow", [])]
    return source_status(periods, air)


def validate_dataset(dataset: dict[str, object]) -> None:
    """Semantic checks that must pass before any generated file is written."""
    pages = dataset.get("pages")
    if not isinstance(pages, dict) or not pages:
        raise RuntimeError("outdoor dataset has no pages")
    missing = sorted(set(LOCATIONS) - set(pages))
    if missing:
        raise RuntimeError(f"outdoor dataset is missing pages: {', '.join(missing)}")
    for slug, page in pages.items():
        level = page.get("risk_level")
        if level not in RISK_LEVELS:
            raise RuntimeError(f"{slug}: unexpected risk_level {level!r}")
        status = page_data_status(page)
        if level == "low" and status["overall"] != "available":
            raise RuntimeError(f"{slug}: low label with {status['overall']} source data")


LEVEL_LABELS = {
    "low": "Low",
    "moderate": "Moderate",
    "high": "High",
    "incomplete": "Incomplete data",
    "unavailable": "Data unavailable",
}


def level_label(level: str) -> str:
    return LEVEL_LABELS.get(level, level.title())


def display_value(value: object) -> str:
    """Render a value for HTML text; 0 is a real value, only None/blank is missing."""
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def period_label(p: dict[str, object]) -> str:
    name = display_value(p.get("name"))
    start = p.get("startTime")
    if isinstance(start, str) and start:
        try:
            moment = datetime.fromisoformat(start)
            return f"{name} ({moment.strftime('%b %d, %H:%M')} local, UTC{moment.strftime('%z')[:3]}:{moment.strftime('%z')[3:]})"
        except ValueError:
            return f"{name} ({start})"
    return name


def observed_label(item: dict[str, object]) -> str:
    date = display_value(item.get("dateObserved")).strip()
    hour = item.get("hourObserved")
    zone = display_value(item.get("localTimeZone")).strip()
    if not date:
        return "not listed"
    text = date
    if finite_number(hour) is not None:
        text += f" {int(hour):02d}:00"
    if zone:
        text += f" {zone}"
    return text


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
    place = f"{page['city']}, {page['state']}"
    level = page["risk_level"]
    if level == "unavailable":
        return f"The recorded snapshot for {place} has no usable forecast temperature, so BreedWise shows no planning label ({reasons}). Check the official services directly."
    if level == "incomplete":
        return f"The recorded snapshot for {place} is incomplete, so BreedWise shows no overall planning label. Recorded inputs: {reasons}."
    return f"The recorded planning label for {place} is {level} because of {reasons}. This is a BreedWise threshold label, not an official warning or safety rating."


def render_index(dataset: dict[str, object]) -> str:
    description = "BreedWise outdoor-risk hub using NWS forecasts and AirNow AQI snapshots for dog walk planning."
    cards = []
    for slug, page in dataset["pages"].items():
        cards.append(
            f'<a class="blog-card" href="{slug}.html"><span class="tag">{escape(level_label(page["risk_level"]))}{"" if page["risk_level"] in ("incomplete", "unavailable") else " label"}</span>'
            f'<h2>{escape(page["city"])} dog outdoor risk</h2>'
            f'<p>{escape(risk_sentence(page))}</p><span class="read-more">Read snapshot</span></a>'
        )
    return (
        page_head("Dog Outdoor Risk Hub | Weather and AQI planning", description, f"{BASE_URL}/outdoor-risk/", "website")
        + nav("../")
        + f'<main><section class="pagehead"><div class="wrap"><p class="kicker">Outdoor Risk Data</p><h1>Weather and air-quality snapshots for safer dog walks.</h1><p class="lead">{escape(description)} Snapshot collected {escape(dataset["updated"])} (KST); each city page lists the forecast period times and AQI observation times reported by the sources.</p></div></section>'
        + '<section class="wrap" style="padding:46px 0"><div class="blog-grid">'
        + "\n".join(cards)
        + '</div><div class="note" style="margin-top:28px"><strong>Use this as a planning signal:</strong> forecast and AQI snapshots change. For urgent weather, smoke, heat, or health decisions, check local authorities and your veterinarian.</div><article class="article" style="margin-top:38px"><h2>What each city snapshot contains</h2><p>Each city page combines a short National Weather Service forecast with AirNow observations available for the chosen ZIP-code area when the snapshot was collected. The page displays forecast periods, temperatures, wind text, precipitation chance, air-quality parameter, AQI value, category, reporting area, and observation date or hour when supplied by the source. The hub is a record of those inputs at a point in time; it is not a live monitoring service.</p><p>BreedWise assigns the visible low, moderate, or high label by a published local rule in the page generator. The rule adds points for forecast heat or cold, stronger wind, higher precipitation chance, and AQI thresholds, then lists the triggering reason. When the forecast returned no usable temperature, the page is marked data unavailable; when AirNow returned no usable AQI observation, the page is marked incomplete and no overall label is shown. Missing inputs are never counted as good conditions. That label is a navigation aid for comparing recorded inputs across the selected cities. It is not a medical assessment, public warning, or instruction that one dog can safely tolerate a particular condition.</p><h2>How to use the snapshot responsibly</h2><ol><li>Open the city page and check when its data was recorded; do not treat an older snapshot as a present condition.</li><li>Use the listed forecast and AQI fields to decide what to verify on the official service before leaving home.</li><li>Separate the weather question from the dog-specific question. Age, coat, fitness, past concerns, and current symptoms are not measured by this hub.</li><li>Keep a fallback routine such as indoor enrichment, a shorter route, shade, drying space, or a rescheduled walk when verified conditions make the ordinary plan impractical.</li></ol><h2>Why there is no universal walk rule</h2><p>The same recorded weather can create different planning questions for different households. A forecast, AQI observation, and route surface are only part of the decision; they do not include the individual dog, local alerts, supervision, access to water or shade, or current veterinary guidance. For urgent weather, smoke, heat, cold, breathing, or health decisions, check local authorities and consult a veterinarian. This page deliberately avoids diagnosis, treatment advice, and universal time-or-temperature prescriptions.</p><h2>How the recorded label is calculated</h2><p>The generator checks the highest and lowest forecast temperature, strongest listed wind, highest precipitation chance, and highest returned AQI. It records which inputs crossed its planning thresholds. A label can flag the reason to look closer, but it cannot determine route shade, pavement heat, smoke movement, or an individual dog\'s comfort. If the official services and the site snapshot differ, the official service is the current reference.</p><h2>Primary sources and corrections</h2><p>Forecast data comes from the <a href="https://www.weather.gov/documentation/services-web-api" rel="nofollow noopener">National Weather Service web API</a>. Air-quality observations come from the <a href="https://docs.airnowapi.org/" rel="nofollow noopener">AirNow API documentation and data service</a>. If a source link fails, a reported field is missing, or a city page no longer reflects the stated snapshot, send the URL and source detail through <a href="../contact/index.html">Corrections</a>.</p><h2>Editorial boundary</h2><p>BreedWise is educational planning content. It does not replace emergency alerts, public-health guidance, or veterinary advice, and it does not diagnose pets or recommend treatment. Read the <a href="../methodology/index.html">methodology</a> for site-wide source and correction rules.</p></article></section></main>'
        + footer("../")
    )


def render_page(slug: str, page: dict[str, object], updated: str) -> str:
    title = f"{page['city']} Dog Outdoor Risk | Weather and AQI planning"
    description = f"{page['city']} dog outdoor risk snapshot using NWS forecast and AirNow AQI data for {page['angle']}."
    forecast_rows = "\n".join(
        "<tr><td>{name}</td><td>{temp}</td><td>{wind}</td><td>{precip}</td><td>{forecast}</td></tr>".format(
            name=escape(period_label(p)),
            temp=escape("not listed" if finite_number(p.get("temperature")) is None else f"{display_value(p.get('temperature'))}{display_value(p.get('temperatureUnit'))}"),
            wind=escape(display_value(p.get("windSpeed"))),
            precip=escape("not listed" if p.get("probabilityOfPrecipitation") is None else f"{display_value(p.get('probabilityOfPrecipitation'))}%"),
            forecast=escape(display_value(p.get("shortForecast"))),
        )
        for p in page["nws_periods"][:FORECAST_PERIODS]
    ) or '<tr><td colspan="5">No NWS forecast period returned for this snapshot.</td></tr>'
    aqi_rows = "\n".join(
        f"<tr><td>{escape(display_value(item.get('parameter')) or 'AQI')}</td><td>{escape('not listed' if item.get('aqi') is None else display_value(item.get('aqi')))}</td><td>{escape(display_value(item.get('category')))}</td><td>{escape(display_value(item.get('reportingArea')))}</td><td>{escape(observed_label(item))}</td></tr>"
        for item in page["airnow"]
    ) or '<tr><td colspan="5">No AirNow observation returned for this ZIP snapshot.</td></tr>'
    status = page_data_status(page)
    status_text = {
        "available": "Forecast and AQI inputs were both returned.",
        "partial": "Only part of the source data was returned; no overall label is shown.",
        "unavailable": "No usable forecast or AQI input was returned; no label is shown.",
    }[status["overall"]]
    forecast_time = page.get("forecast_generated_at") or page.get("forecast_updated_at")
    forecast_time_text = f" NWS forecast generated {forecast_time}." if forecast_time else ""
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
        + f'<main><section class="pagehead"><div class="wrap"><p class="breadcrumbs"><a href="../outdoor-risk/index.html">Outdoor Risk</a> / {escape(page["city"])}</p><p class="kicker">NWS + AirNow Snapshot</p><h1>{escape(page["city"])} dog outdoor risk</h1><p class="lead">{escape(description)}</p><div class="meta"><span>Planning label: {escape(level_label(page["risk_level"]))}</span><span>Snapshot collected: {escape(updated)} (KST)</span><span>Focus: {escape(page["angle"])}</span></div></div></section>'
        + '<div class="wrap content"><article class="article">'
        + f'<div class="callout"><strong>Short answer:</strong> {escape(risk_sentence(page))} This is a recorded snapshot, not a live reading. Check the current NWS forecast, local alerts, and AirNow before a walk, and use shorter outings, shade, water, paw checks, and schedule changes when conditions are demanding.</div>'
        + f'<p class="note"><strong>Data status:</strong> {escape(status_text)}{escape(forecast_time_text)} Forecast periods below show the source start time in the city\'s local offset; AQI rows show the reported observation time.</p>'
        + f'<h2 id="who-needs-care">Dogs that need extra care in {escape(page["city"])}</h2><p>This page is most useful for {escape(page["sensitive"])}. The forecast is not a medical rule, but it helps owners decide whether a normal walk should become a shorter potty break, an indoor enrichment session, or a cooler-time outing.</p>'
        + '<h2 id="walk-plan">How to use the snapshot before a walk</h2><ul><li>Check the warmest or coldest forecast period before choosing the route.</li><li>Watch air quality for dogs with breathing, heart, age, or stamina limits.</li><li>Use pavement, wind, rain, and visibility as practical constraints, not just the headline temperature.</li><li>Bring water and choose a route that lets the dog stop early without forcing a long return.</li></ul>'
        + f'<h2 id="breed-planning">Breed and cost planning angle</h2><p>Outdoor constraints can become ownership costs. A household may need cooling gear, paw protection, indoor enrichment, paid walkers at safer hours, grooming support, or training help when weather blocks normal exercise. That matters before choosing a breed, especially for high-energy dogs or dogs with heat, cold, or breathing limits.</p>'
        + f'<h2 id="local-planning">Local planning notes for {escape(page["city"])}</h2><p>The same forecast can mean different things for different dogs. A young athletic dog, a senior toy breed, a flat-faced companion breed, and a thick-coated working breed do not use the same outdoor plan. Use the local notes below to translate the public data into a practical owner decision.</p><ul>{local_notes}</ul>'
        + '<h2 id="budget-check">Budget checks this weather can create</h2><p>Weather rarely appears as a single line item in a dog budget, but it changes the support system around the dog. Heat can create cooling and indoor-enrichment costs. Cold can create coat, boot, traction, and joint-comfort costs. Rain can create grooming and drying costs. Bad air quality can create more indoor activity needs and stricter walk timing. These are not reasons to avoid a breed automatically; they are reasons to include the environment in the ownership plan before adoption.</p>'
        + '<h2 id="mistakes">Common owner mistakes to avoid</h2><ul><li>Do not treat the forecast high as the only risk; pavement, humidity, wind, and AQI can matter more during the actual walk.</li><li>Do not assume a tired dog is safely exercised. Heat, smoke, cold, or slick surfaces can create stress without providing healthy enrichment.</li><li>Do not buy a high-energy breed unless the household has indoor work, training games, or safe-time exercise options for difficult weather days.</li><li>Do not wait for a problem before pricing backup care, grooming support, paw gear, or cooling equipment.</li></ul>'
        + f'<h2 id="forecast">NWS forecast snapshot</h2><table class="table"><thead><tr><th>Period</th><th>Temp</th><th>Wind</th><th>Rain/snow chance</th><th>Forecast</th></tr></thead><tbody>{forecast_rows}</tbody></table>'
        + f'<h2 id="air">AirNow AQI snapshot</h2><table class="table"><thead><tr><th>Parameter</th><th>AQI</th><th>Category</th><th>Area</th><th>Observed</th></tr></thead><tbody>{aqi_rows}</tbody></table>'
        + '<h2 id="limits">Source limits</h2><p>Data comes from the National Weather Service API and AirNow API. Forecasts and AQI observations can change quickly, and this page is educational planning content only. It does not replace emergency weather warnings, public-health guidance, or veterinary advice.</p>'
        + '</article><aside class="toc" aria-label="Article contents"><strong>Contents</strong><a href="#who-needs-care">Dogs needing care</a><a href="#walk-plan">Walk plan</a><a href="#breed-planning">Breed planning</a><a href="#local-planning">Local notes</a><a href="#budget-check">Budget checks</a><a href="#mistakes">Mistakes</a><a href="#forecast">Forecast</a><a href="#air">AQI</a><a href="#limits">Limits</a><hr><strong>Next steps</strong><a href="../outdoor-risk/index.html">Outdoor hub</a><a href="../cost/index.html">Cost data</a><a href="../blog/index.html">BreedWise guides</a></aside></div></main>'
        + footer("../")
    )


def update_sitemap(dataset: dict[str, object], changed_files: list[str] | None = None) -> None:
    """Bump lastmod only for pages whose HTML actually changed in this run."""
    urls = [f"{BASE_URL}/outdoor-risk/"] + [f"{BASE_URL}/outdoor-risk/{slug}.html" for slug in dataset["pages"]]
    changed = [
        f"{BASE_URL}/outdoor-risk/" if name == "index.html" else f"{BASE_URL}/outdoor-risk/{name}"
        for name in (changed_files or [])
    ]
    site_metadata.update_sitemap_for_changes(ROOT / "sitemap.xml", changed, urls, site_metadata.today_kst())


def main() -> int:
    RISK_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)
    dataset = json.loads((DATA_DIR / "dog_outdoor_risk.json").read_text(encoding="utf-8")) if os.environ.get("BREEDWISE_USE_CACHED_DATA") == "1" else normalize()
    # Validate before writing anything so a bad fetch keeps the last good snapshot.
    validate_dataset(dataset)
    rendered = {"index.html": render_index(dataset)}
    for slug, page in dataset["pages"].items():
        rendered[f"{slug}.html"] = render_page(slug, page, dataset["updated"])
    site_metadata.write_if_changed(DATA_DIR / "dog_outdoor_risk.json", json.dumps(dataset, indent=2, ensure_ascii=False))
    changed = [name for name, html in rendered.items() if site_metadata.write_if_changed(RISK_DIR / name, html)]
    update_sitemap(dataset, changed)
    print(json.dumps({"ok": True, "updated": dataset["updated"], "pages": list(dataset["pages"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
