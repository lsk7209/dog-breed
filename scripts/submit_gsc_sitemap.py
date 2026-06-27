from __future__ import annotations

import json
import os
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


ROOT = Path(__file__).resolve().parents[1]
SITE_URL = os.environ.get("GSC_SITE_URL", "https://dogbreedcost.com/")
SITEMAP_URL = os.environ.get("GSC_SITEMAP_URL", "https://dogbreedcost.com/sitemap.xml")
DEFAULT_CREDENTIALS = Path("D:/env/gsc_credentials.json")
SCOPES = [
    "https://www.googleapis.com/auth/webmasters",
    "https://www.googleapis.com/auth/siteverification",
]


def credentials_path() -> Path:
    env_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if env_path:
        return Path(env_path)
    return DEFAULT_CREDENTIALS


def ensure_site_verification_file(credentials_file: Path) -> str:
    creds = service_account.Credentials.from_service_account_file(str(credentials_file), scopes=SCOPES)
    service = build("siteVerification", "v1", credentials=creds, cache_discovery=False)
    body = {"site": {"type": "SITE", "identifier": SITE_URL}, "verificationMethod": "FILE"}
    token = service.webResource().getToken(body=body).execute()["token"]
    token_path = ROOT / token
    expected = "google-site-verification: " + token
    if not token_path.exists() or token_path.read_text(encoding="utf-8").strip() != expected:
        token_path.write_text(expected, encoding="utf-8")
    return token


def submit_sitemap(credentials_file: Path) -> dict[str, object]:
    creds = service_account.Credentials.from_service_account_file(str(credentials_file), scopes=SCOPES)
    service = build("searchconsole", "v1", credentials=creds, cache_discovery=False)
    try:
        service.sitemaps().submit(siteUrl=SITE_URL, feedpath=SITEMAP_URL).execute()
    except HttpError as exc:
        return {"submitted": False, "status": exc.resp.status, "reason": exc.reason}
    try:
        sitemaps = service.sitemaps().list(siteUrl=SITE_URL).execute().get("sitemap", [])
    except HttpError as exc:
        return {"submitted": True, "listed": False, "status": exc.resp.status, "reason": exc.reason}
    match = next((item for item in sitemaps if item.get("path") == SITEMAP_URL), None)
    return {"submitted": True, "listed": bool(match), "sitemap": match}


def main() -> int:
    credentials_file = credentials_path()
    if not credentials_file.exists():
        print(json.dumps({"ok": False, "error": "missing_credentials", "path": str(credentials_file)}))
        return 1
    token = ensure_site_verification_file(credentials_file)
    result = submit_sitemap(credentials_file)
    print(json.dumps({"ok": bool(result.get("submitted")), "site": SITE_URL, "sitemap": SITEMAP_URL, "verification_file": token, "result": result}, ensure_ascii=False))
    return 0 if result.get("submitted") else 2


if __name__ == "__main__":
    raise SystemExit(main())
