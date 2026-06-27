from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import os
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
USER_AGENT = "dogbreedcost.com public-data-check contact@dogbreedcost.com"


def secret(name: str, fallback: str | None = None) -> str:
    value = os.environ.get(name, "").strip()
    if not value and fallback:
        path = Path(fallback)
        if path.exists():
            value = path.read_text(encoding="ascii").strip()
    if not value:
        raise RuntimeError(f"{name} is missing")
    return value


def read_json(url: str, headers: dict[str, str] | None = None) -> object:
    request = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))


def check_noaa() -> dict[str, object]:
    token = secret("NOAA_CDO_TOKEN", "D:/env/noaa_cdo_token.txt")
    data = read_json("https://www.ncei.noaa.gov/cdo-web/api/v2/datasets?limit=1", {"token": token})
    results = data.get("results", []) if isinstance(data, dict) else []
    return {"ok": bool(results), "sample": results[0].get("id") if results else None}


def check_fred() -> dict[str, object]:
    key = secret("FRED_API_KEY", "D:/env/fred_api_key.txt")
    query = urllib.parse.urlencode(
        {
            "series_id": "CPIAUCSL",
            "api_key": key,
            "file_type": "json",
            "limit": 1,
            "sort_order": "desc",
        }
    )
    data = read_json(f"https://api.stlouisfed.org/fred/series/observations?{query}")
    observations = data.get("observations", []) if isinstance(data, dict) else []
    latest = observations[0] if observations else {}
    return {"ok": bool(observations), "sample_date": latest.get("date"), "series_id": "CPIAUCSL"}


def check_data_gov() -> dict[str, object]:
    key = secret("DATA_GOV_API_KEY", "D:/env/data_gov_api_key.txt")
    query = urllib.parse.urlencode({"q": "pet", "rows": 1})
    data = read_json(
        f"https://api.gsa.gov/technology/datagov/v4/search?{query}",
        {"X-Api-Key": key},
    )
    results = data.get("result", {}).get("results", []) if isinstance(data, dict) else []
    return {"ok": isinstance(results, list), "checked_endpoint": "Data.gov Catalog API", "sample_count": len(results)}


def check_airnow() -> dict[str, object]:
    key = secret("AIRNOW_API_KEY", "D:/env/airnow_api_key.txt")
    query = urllib.parse.urlencode(
        {
            "format": "application/json",
            "zipCode": "20001",
            "distance": 25,
            "API_KEY": key,
        }
    )
    data = read_json(f"https://www.airnowapi.org/aq/observation/zipCode/current/?{query}")
    return {"ok": isinstance(data, list), "sample_count": len(data) if isinstance(data, list) else None}


def check_nws() -> dict[str, object]:
    data = read_json("https://api.weather.gov/points/38.8977,-77.0365", {"User-Agent": USER_AGENT})
    properties = data.get("properties", {}) if isinstance(data, dict) else {}
    return {"ok": bool(properties.get("forecast")), "key_required": False}


def main() -> int:
    checks = {
        "noaa_cdo": check_noaa,
        "fred": check_fred,
        "data_gov": check_data_gov,
        "airnow": check_airnow,
        "nws": check_nws,
    }
    status: dict[str, object] = {"checked_at": datetime.now(timezone.utc).isoformat(), "checks": {}}
    failed: list[str] = []
    for name, fn in checks.items():
        try:
            result = fn()
        except Exception as exc:
            result = {"ok": False, "error": type(exc).__name__}
        status["checks"][name] = result
        if not result.get("ok"):
            failed.append(name)
    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / "public_api_status.json").write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"ok": not failed, "failed": failed, "checks": list(checks)}, ensure_ascii=False))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
