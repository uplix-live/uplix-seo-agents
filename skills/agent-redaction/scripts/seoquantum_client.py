"""Client Python pour l'API SEOQuantum.

API : http://api.seoquantum.com/api (HTTP only, pas HTTPS valide)
Auth : header `API-Key: <key>`
Cout : Semantic Analysis = 5 tokens, Content Brief = 10 tokens, Advisor = 0 tokens

Usage en CLI :
    python seoquantum_client.py credits
    python seoquantum_client.py analyze "agence seo"
    python seoquantum_client.py wait <analysis_id>
    python seoquantum_client.py result <analysis_id>
    python seoquantum_client.py optimize <analysis_id> --url https://example.com/page
    python seoquantum_client.py audit-page <url> <target_keyword>

Workflow integre `audit-page` :
    1. Lance une Semantic Analysis sur le keyword
    2. Polle jusqu'a completion
    3. Lance un advisor sur l'URL avec ce keyword
    4. Recupere le score SEO + recommandations
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "http://api.seoquantum.com/api"
DEFAULT_KEY = os.environ.get("SEOQUANTUM_API_KEY", "")
CACHE_DIR = Path(__file__).resolve().parents[1] / "data" / "seoquantum_cache"


class SEOQuantumClient:
    """Client minimal pour l'API SEOQuantum."""

    def __init__(self, api_key: str = DEFAULT_KEY, base: str = BASE):
        self.key = api_key
        self.base = base
        self.s = requests.Session()
        self.s.headers.update({"API-Key": self.key, "Accept": "application/json"})

    # ----------- USER -----------
    def user(self) -> dict:
        r = self.s.get(f"{self.base}/user/", timeout=20)
        r.raise_for_status()
        return r.json()

    def credits(self) -> int:
        return self.user().get("tokens", 0)

    def pending(self) -> list:
        return self.user().get("pending_tasks", [])

    # ----------- ANALYSIS -----------
    def analyze(self, target_keyword: str, lang: str = "fr-FR") -> dict:
        """Launch a Semantic Analysis (5 tokens). Returns dict with analysis_id."""
        body = {"target_keyword": target_keyword, "lang": lang}
        r = self.s.post(f"{self.base}/task/analysis/", json=body, timeout=60)
        r.raise_for_status()
        return r.json()

    def content_brief(self, target_keyword: str, lang: str = "fr-FR") -> dict:
        """Launch a full Content Brief (10 tokens)."""
        body = {"target_keyword": target_keyword, "lang": lang}
        r = self.s.post(f"{self.base}/task/analysis/content_brief", json=body, timeout=60)
        r.raise_for_status()
        return r.json()

    def get_analysis(self, analysis_id: str) -> dict:
        r = self.s.get(f"{self.base}/task/analysis/{analysis_id}", timeout=60)
        r.raise_for_status()
        return r.json()

    def wait_analysis(self, analysis_id: str, max_wait: int = 600, poll: int = 5) -> dict:
        """Polle l'analyse jusqu'a completion (status != PENDING/RUNNING/QUEUED)."""
        start = time.time()
        WAIT_STATES = {"pending", "running", "queued", "processing"}
        while time.time() - start < max_wait:
            data = self.get_analysis(analysis_id)
            status = str(data.get("status", "?")).lower()
            print(f"  [{int(time.time()-start)}s] status={status}", flush=True)
            if status not in WAIT_STATES:
                return data
            time.sleep(poll)
        raise TimeoutError(f"Analysis {analysis_id} not completed after {max_wait}s")

    # ----------- ADVISOR (OPTIMIZE) -----------
    def optimize_from_url(self, analysis_id: str, url: str) -> dict:
        """Lance un advisor sur l'URL (0 tokens). Compare le contenu de l'URL a l'analyse semantique."""
        body = {"from_url": url}
        r = self.s.post(f"{self.base}/task/analysis/{analysis_id}/optimize", json=body, timeout=120)
        r.raise_for_status()
        return r.json()

    def optimize_from_text(self, analysis_id: str, text: str) -> dict:
        body = {"from_text": text}
        r = self.s.post(f"{self.base}/task/analysis/{analysis_id}/optimize", json=body, timeout=120)
        r.raise_for_status()
        return r.json()

    def get_optimize(self, analysis_id: str) -> dict:
        r = self.s.get(f"{self.base}/task/analysis/{analysis_id}/optimize", timeout=60)
        r.raise_for_status()
        return r.json()

    # ----------- WORKFLOW INTEGRE -----------
    def audit_page(self, url: str, target_keyword: str, lang: str = "fr-FR",
                   cache: bool = True) -> dict:
        """Workflow integre : analyse semantique + advisor sur l'URL.

        Si une analyse pour ce keyword existe en cache, la reutilise (0 tokens).
        """
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = CACHE_DIR / f"kw_{target_keyword.lower().replace(' ', '_').replace('/', '_')}.json"

        if cache and cache_file.exists():
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            analysis_id = data.get("analysis_id")
            print(f"  Cache hit : analysis_id={analysis_id}")
        else:
            print(f"  Lancement analyse semantique '{target_keyword}' (5 tokens)...")
            res = self.analyze(target_keyword, lang)
            analysis_id = res.get("analysis_id") or res.get("id") or res.get("task_id")
            if not analysis_id:
                print(f"  Reponse inattendue : {res}")
                return {"error": "no_analysis_id", "raw": res}
            print(f"  analysis_id : {analysis_id}, attente...")
            analysis_result = self.wait_analysis(analysis_id)
            cache_file.write_text(json.dumps(
                {"analysis_id": analysis_id, "target_keyword": target_keyword,
                 "lang": lang, "result": analysis_result},
                indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  Cache : {cache_file.name}")

        # Lancer l'advisor sur l'URL
        print(f"  Advisor sur {url} (0 tokens)...")
        try:
            advisor = self.optimize_from_url(analysis_id, url)
        except requests.HTTPError as e:
            return {"analysis_id": analysis_id, "error": f"advisor_failed: {e}"}

        # Attendre l'advisor (lui aussi est async)
        print(f"  Attente advisor...")
        time.sleep(3)
        WAIT_STATES = {"pending", "running", "queued", "processing"}
        for i in range(60):  # max 5 min
            adv_data = self.get_optimize(analysis_id)
            status = str(adv_data.get("status", "?")).lower()
            print(f"    [{i*5}s] status={status}", flush=True)
            if status not in WAIT_STATES:
                break
            time.sleep(5)

        return {"analysis_id": analysis_id, "url": url, "target_keyword": target_keyword,
                "advisor": adv_data}


# ============== CLI ==============

def cmd_credits(args):
    c = SEOQuantumClient(args.key)
    u = c.user()
    print(f"User ID  : {u['user_id']}")
    print(f"Tokens   : {u['tokens']}")
    print(f"Pending  : {len(u.get('pending_tasks', []))}")


def cmd_analyze(args):
    c = SEOQuantumClient(args.key)
    res = c.analyze(args.keyword, args.lang)
    print(json.dumps(res, indent=2, ensure_ascii=False))


def cmd_wait(args):
    c = SEOQuantumClient(args.key)
    res = c.wait_analysis(args.analysis_id, max_wait=args.timeout)
    print(json.dumps(res, indent=2, ensure_ascii=False)[:2000])


def cmd_result(args):
    c = SEOQuantumClient(args.key)
    res = c.get_analysis(args.analysis_id)
    print(json.dumps(res, indent=2, ensure_ascii=False))


def cmd_optimize(args):
    c = SEOQuantumClient(args.key)
    res = c.optimize_from_url(args.analysis_id, args.url)
    print(json.dumps(res, indent=2, ensure_ascii=False))


def cmd_audit_page(args):
    c = SEOQuantumClient(args.key)
    res = c.audit_page(args.url, args.keyword, args.lang, cache=not args.no_cache)
    print("\n=== AUDIT PAGE ===")
    if "error" in res:
        print(f"  ERROR : {res['error']}")
        return
    print(f"  URL     : {res['url']}")
    print(f"  Keyword : {res['target_keyword']}")
    adv = res.get("advisor", {})
    print(f"\n  Status advisor : {adv.get('status', '?')}")
    # Champs typiques d'un advisor SEOQuantum
    for k in ("score", "score_global", "global_score", "quality_score", "semantic_score"):
        if k in adv:
            print(f"  {k}: {adv[k]}")
    # Save full result
    out = CACHE_DIR / f"audit_{args.keyword.lower().replace(' ','_')}_{int(time.time())}.json"
    out.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Result complet : {out}")


def main():
    ap = argparse.ArgumentParser(description="SEOQuantum API CLI")
    ap.add_argument("--key", default=DEFAULT_KEY, help="API-Key (default: env SEOQUANTUM_API_KEY)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("credits", help="Show user info + tokens"); sp.set_defaults(func=cmd_credits)

    sp = sub.add_parser("analyze", help="Launch semantic analysis (5 tokens)")
    sp.add_argument("keyword"); sp.add_argument("--lang", default="fr-FR"); sp.set_defaults(func=cmd_analyze)

    sp = sub.add_parser("wait", help="Wait analysis completion")
    sp.add_argument("analysis_id"); sp.add_argument("--timeout", type=int, default=600); sp.set_defaults(func=cmd_wait)

    sp = sub.add_parser("result", help="Get analysis result")
    sp.add_argument("analysis_id"); sp.set_defaults(func=cmd_result)

    sp = sub.add_parser("optimize", help="Launch advisor on URL (0 tokens)")
    sp.add_argument("analysis_id"); sp.add_argument("--url", required=True); sp.set_defaults(func=cmd_optimize)

    sp = sub.add_parser("audit-page", help="Full audit : analyze + advisor on URL")
    sp.add_argument("url"); sp.add_argument("keyword"); sp.add_argument("--lang", default="fr-FR")
    sp.add_argument("--no-cache", action="store_true")
    sp.set_defaults(func=cmd_audit_page)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
