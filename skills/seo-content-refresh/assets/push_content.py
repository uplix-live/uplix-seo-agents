"""Push réutilisable d'un contenu optimisé vers WordPress via REST API.

À copier dans chaque dossier de livrable, puis personnaliser les constantes du haut.
Vérifie l'auth, fait un re-backup, push (PUT), vérifie le résultat backend + live.

Env vars requises:
    WP_USER             : login WordPress
    WP_APP_PASSWORD     : Application Password (pas le mot de passe principal)

Constantes à personnaliser (haut du fichier):
    WP_BASE      : base URL de l'API REST WordPress
    POST_ID      : ID du post à mettre à jour (ou résoudre via slug)
    POST_TYPE    : 'posts' ou 'pages'
    NEW_TITLE    : nouveau title (max 60 chars conseillé)
    NEW_EXCERPT  : nouvelle meta description (~155 chars)
    NEW_STATUS   : 'publish' (live) ou 'draft' (révision sans publier)
    CONTENT_HTML : HTML complet à pousser (inline CSS + JSON-LD + body)
    LIVE_URL     : URL publique pour vérification finale
    MARKERS      : liste de tuples (label, marker_string) à vérifier en backend ET live

Usage:
    WP_USER="damien" WP_APP_PASSWORD="xxxx xxxx ..." python push_content.py
"""
import os
import sys
import json
import base64
import time
from pathlib import Path
from typing import Iterable

import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ============= À PERSONNALISER PAR CONTENU =============
WP_BASE = "https://www.uplix.fr/wp-json/wp/v2"
POST_ID = 0  # mettre l'ID, ou laisser à 0 et utiliser SLUG ci-dessous
POST_TYPE = "posts"  # "posts" ou "pages"
SLUG = ""  # si POST_ID=0, on résoudra via ce slug

NEW_TITLE = "À remplacer"
NEW_EXCERPT = "À remplacer (max 155 chars)"
NEW_STATUS = "publish"  # ou "draft"

CONTENT_HTML = """<!-- À remplacer par le HTML complet (inline CSS + JSON-LD + body) -->"""

LIVE_URL = ""  # URL publique pour vérif (ex: "https://www.uplix.fr/ahrefs/")

MARKERS: list[tuple[str, str]] = [
    # ("Label", "marker_string_à_chercher_dans_content")
    ("Title nouveau", NEW_TITLE[:30]),
    # Ajouter les markers spécifiques au contenu
]

# ============= LOGIQUE PUSH =============
ROOT = Path(__file__).parent


def auth_header() -> dict:
    user = os.environ.get("WP_USER")
    pw = os.environ.get("WP_APP_PASSWORD")
    if not user or not pw:
        print("ERR: WP_USER et WP_APP_PASSWORD requis en env vars")
        sys.exit(1)
    cred = base64.b64encode(f"{user}:{pw}".encode()).decode()
    return {"Authorization": f"Basic {cred}", "Content-Type": "application/json"}


def resolve_post_id(headers: dict) -> int:
    """Si POST_ID n'est pas défini, le résoudre via SLUG."""
    if POST_ID:
        return POST_ID
    if not SLUG:
        print("ERR: ni POST_ID ni SLUG défini")
        sys.exit(1)

    # Essayer posts puis pages
    for ptype in ("posts", "pages"):
        r = requests.get(f"{WP_BASE}/{ptype}?slug={SLUG}", headers=headers, timeout=20)
        if r.status_code == 200 and r.json():
            items = r.json()
            print(f"  Résolu: slug={SLUG} → id={items[0]['id']} (type={ptype})")
            return items[0]["id"]
    print(f"ERR: slug '{SLUG}' introuvable en posts ni pages")
    sys.exit(1)


def fetch_post(post_id: int, headers: dict) -> dict:
    r = requests.get(f"{WP_BASE}/{POST_TYPE}/{post_id}?context=edit", headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()


def push_update(post_id: int, headers: dict) -> dict:
    payload = {
        "title": NEW_TITLE,
        "content": CONTENT_HTML,
        "excerpt": NEW_EXCERPT,
        "status": NEW_STATUS,
    }
    r = requests.post(f"{WP_BASE}/{POST_TYPE}/{post_id}", headers=headers, json=payload, timeout=90)
    if r.status_code not in (200, 201):
        print(f"  ERR push: {r.status_code} → {r.text[:1000]}")
        sys.exit(2)
    return r.json()


def check_markers(text: str, markers: Iterable[tuple[str, str]]) -> tuple[int, int]:
    ok = 0
    total = 0
    for label, m in markers:
        total += 1
        count = text.count(m)
        found = count > 0
        if found:
            ok += 1
        status = "OK" if found else "KO"
        print(f"  [{status}] {label} ({m!r}: {count}x)")
    return ok, total


def main():
    print(f"=== Push to WordPress ===")
    print(f"  WP_BASE  : {WP_BASE}")
    print(f"  POST_TYPE: {POST_TYPE}")
    print(f"  NEW_STATUS: {NEW_STATUS}")

    H = auth_header()

    # 1. Résoudre post_id si nécessaire
    post_id = resolve_post_id(H)

    # 2. Re-backup au cas où
    print()
    print(f"=== Re-backup {POST_TYPE}/{post_id} ===")
    backup = fetch_post(post_id, H)
    print(f"  Title actuel : {backup['title']['raw']}")
    print(f"  Modified     : {backup['modified']}")
    print(f"  Status       : {backup['status']}")
    print(f"  Length       : {len(backup['content']['raw'])} chars")
    backup_file = ROOT / f"backup_post_{post_id}_pre_push.json"
    backup_file.write_text(json.dumps(backup, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  → {backup_file.name}")

    # 3. PUT update
    print()
    print(f"=== Push update ===")
    print(f"  New title    : {NEW_TITLE}")
    print(f"  New content  : {len(CONTENT_HTML)} chars (avant: {len(backup['content']['raw'])})")
    print(f"  Excerpt      : {NEW_EXCERPT[:80]}...")
    updated = push_update(post_id, H)
    print(f"  Status push  : OK")
    print(f"  Title push   : {updated['title']['rendered']}")
    print(f"  Modified now : {updated['modified']}")
    print(f"  Length now   : {len(updated['content']['rendered'])} chars")
    after_file = ROOT / f"after_post_{post_id}.json"
    after_file.write_text(json.dumps(updated, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  → {after_file.name}")

    # 4. Vérif markers backend (depuis updated['content']['raw'])
    print()
    print("=== Vérif backend ===")
    raw_after = updated.get("content", {}).get("raw") or updated.get("content", {}).get("rendered", "")
    ok_b, total_b = check_markers(raw_after, MARKERS)
    print(f"  → {ok_b}/{total_b} markers OK en backend")

    # 5. Vérif live (avec cache bust)
    if LIVE_URL:
        print()
        print(f"=== Vérif live {LIVE_URL} ===")
        bypass = f"?bypass={int(time.time())}"
        rv = requests.get(
            LIVE_URL + bypass,
            headers={
                "User-Agent": "seo-content-refresh-verify/1.0",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
            },
            timeout=30,
        )
        print(f"  status: {rv.status_code}, len: {len(rv.text)}")
        ok_l, total_l = check_markers(rv.text, MARKERS)
        print(f"  → {ok_l}/{total_l} markers OK en live")
        if ok_l < total_l:
            print("  WARN : vide cache WP Rocket / FlyingPress / Cloudflare si markers manquants")

    print()
    print(f"DONE — post {post_id} mis à jour à {updated['modified']}")


if __name__ == "__main__":
    main()
