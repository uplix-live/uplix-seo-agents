"""GSC query helper — utilise les OAuth credentials de `.mcp.json` (gsc-lucky)
quand le MCP server n'est pas disponible.

Usage :
    python scripts/gsc_query.py search_analytics SITE_URL DATE_FROM DATE_TO [DIMENSIONS] [ROW_LIMIT]
    python scripts/gsc_query.py sitemaps SITE_URL
    python scripts/gsc_query.py inspect SITE_URL PAGE_URL
    python scripts/gsc_query.py list_sites

Exemples :
    python scripts/gsc_query.py search_analytics https://www.laboutiqueafricavivre.com/ 2026-02-13 2026-05-12 query 500
    python scripts/gsc_query.py search_analytics https://www.laboutiqueafricavivre.com/ 2026-02-13 2026-05-12 page,query 1000
    python scripts/gsc_query.py inspect https://www.laboutiqueafricavivre.com/ https://www.laboutiqueafricavivre.com/livres/205-l-enfant-noir-9782266178945

Output : JSON sur stdout. Rediriger vers fichier avec `> data/gsc/foo.json`.
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from typing import Any

import os

CLIENT_ID = os.environ.get("GSC_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GSC_CLIENT_SECRET", "")
REFRESH_TOKEN = os.environ.get("GSC_REFRESH_TOKEN", "")

if not (CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN):
    sys.exit("Erreur : definir GSC_CLIENT_ID, GSC_CLIENT_SECRET et GSC_REFRESH_TOKEN dans l'environnement (ou .env). Voir README.")


def get_access_token() -> str:
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["access_token"]


def gsc_request(method: str, url: str, token: str, body: dict[str, Any] | None = None) -> Any:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def list_sites(token: str) -> Any:
    return gsc_request("GET", "https://www.googleapis.com/webmasters/v3/sites", token)


def search_analytics(token: str, site: str, date_from: str, date_to: str, dimensions: list[str], row_limit: int = 1000) -> Any:
    site_enc = urllib.parse.quote(site, safe="")
    url = f"https://www.googleapis.com/webmasters/v3/sites/{site_enc}/searchAnalytics/query"
    body: dict[str, Any] = {
        "startDate": date_from,
        "endDate": date_to,
        "dimensions": dimensions,
        "rowLimit": row_limit,
    }
    return gsc_request("POST", url, token, body)


def list_sitemaps(token: str, site: str) -> Any:
    site_enc = urllib.parse.quote(site, safe="")
    return gsc_request("GET", f"https://www.googleapis.com/webmasters/v3/sites/{site_enc}/sitemaps", token)


def inspect_url(token: str, site: str, page_url: str) -> Any:
    url = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
    body = {"inspectionUrl": page_url, "siteUrl": site, "languageCode": "fr-FR"}
    return gsc_request("POST", url, token, body)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    token = get_access_token()
    if cmd == "list_sites":
        print(json.dumps(list_sites(token), indent=2, ensure_ascii=False))
    elif cmd == "search_analytics":
        site, date_from, date_to = argv[2], argv[3], argv[4]
        dims = argv[5].split(",") if len(argv) > 5 else ["query"]
        row_limit = int(argv[6]) if len(argv) > 6 else 1000
        print(json.dumps(search_analytics(token, site, date_from, date_to, dims, row_limit), indent=2, ensure_ascii=False))
    elif cmd == "sitemaps":
        print(json.dumps(list_sitemaps(token, argv[2]), indent=2, ensure_ascii=False))
    elif cmd == "inspect":
        print(json.dumps(inspect_url(token, argv[2], argv[3]), indent=2, ensure_ascii=False))
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
