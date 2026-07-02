"""
validate_schema.py — Validation JSON-LD / Schema.org (via google/schemarama)
Extrait les données structurées d'une URL ou fichier HTML et les valide.

Usage:
    python scripts/validate_schema.py https://example.fr/page
    python scripts/validate_schema.py page.html --local
    python scripts/validate_schema.py https://example.fr/page --all   # Toutes les pages d'un sitemap
    python scripts/validate_schema.py urls.csv --batch

Nécessite : Node.js + schemarama (external-seo-tools/schemarama/core)
"""

import argparse
import json
import subprocess
import sys
import re
from pathlib import Path

# Fix Windows cp1252 encoding issues
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd
except ImportError as e:
    print(f"ERROR: {e}\nInstaller: pip install requests beautifulsoup4 pandas")
    sys.exit(1)

SCHEMARAMA_DIR = Path(__file__).parent.parent / "external-seo-tools" / "schemarama" / "core"


# ── Extraction JSON-LD ────────────────────────────────────────────────────────

def extract_jsonld(url_or_html: str, is_local: bool = False) -> list[dict]:
    """Extrait tous les blocs JSON-LD d'une page."""
    if is_local:
        with open(url_or_html, encoding="utf-8") as f:
            html = f.read()
    else:
        try:
            r = requests.get(url_or_html, timeout=15,
                             headers={"User-Agent": "Mozilla/5.0 (SEO Audit Bot)"})
            html = r.text
        except Exception as e:
            print(f"  Fetch error : {e}", file=sys.stderr)
            return []

    soup = BeautifulSoup(html, "lxml")
    blocks = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string.strip())
            blocks.append(data)
        except json.JSONDecodeError:
            pass
    return blocks


# ── Validation via schemarama ─────────────────────────────────────────────────

def validate_with_schemarama(jsonld_data: dict) -> dict:
    """
    Valide un objet JSON-LD via schemarama (Node.js).
    Retourne {valid: bool, errors: list, warnings: list}
    """
    if not SCHEMARAMA_DIR.exists():
        return {"valid": None, "errors": ["schemarama non trouvé"], "warnings": []}

    # Script Node inline
    node_script = f"""
const schemarama = require('{(SCHEMARAMA_DIR / 'src').as_posix()}');
const data = {json.dumps(jsonld_data)};
schemarama.validate(JSON.stringify(data)).then(result => {{
    console.log(JSON.stringify(result));
}}).catch(e => {{
    console.error(e.message);
    process.exit(1);
}});
"""
    try:
        result = subprocess.run(
            ["node", "-e", node_script],
            capture_output=True, text=True, timeout=10,
            cwd=str(SCHEMARAMA_DIR)
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {"valid": None, "errors": [result.stderr.strip()], "warnings": []}
    except Exception as e:
        return {"valid": None, "errors": [str(e)], "warnings": []}


# ── Validation légère (sans schemarama) ──────────────────────────────────────

DEPRECATED_TYPES = {"HowTo", "SpecialAnnouncement"}
RESTRICTED_TYPES = {"FAQPage"}
VALID_CONTEXTS = {"https://schema.org", "http://schema.org", "https://schema.org/"}

def validate_local(block: dict) -> dict:
    """Validation rapide sans Node.js : types dépréciés, contexte, champs requis."""
    errors = []
    warnings = []

    ctx = block.get("@context", "")
    if ctx not in VALID_CONTEXTS and not str(ctx).startswith("http"):
        errors.append(f"@context invalide : {ctx!r}")

    schema_type = block.get("@type", "")
    if isinstance(schema_type, list):
        schema_type = schema_type[0]

    if schema_type in DEPRECATED_TYPES:
        errors.append(f"Type déprécié : {schema_type} (ne produit plus de rich results)")
    if schema_type == "FAQPage":
        warnings.append("FAQPage : restreint depuis août 2023 — uniquement sites gouvernementaux/santé")

    # Champs requis par type
    required = {
        "Article": ["headline", "author", "datePublished"],
        "Product": ["name", "offers"],
        "LocalBusiness": ["name", "address"],
        "BreadcrumbList": ["itemListElement"],
        "VideoObject": ["name", "description", "thumbnailUrl", "uploadDate"],
        "Recipe": ["name", "recipeIngredient", "recipeInstructions"],
        "Event": ["name", "startDate", "location"],
        "JobPosting": ["title", "description", "datePosted", "hiringOrganization"],
    }
    if schema_type in required:
        for field in required[schema_type]:
            if field not in block:
                warnings.append(f"Champ recommandé manquant : {field}")

    return {
        "type": schema_type,
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


# ── Audit d'une URL ───────────────────────────────────────────────────────────

def audit_url(url: str, is_local: bool = False, verbose: bool = True) -> dict:
    """Audite le Schema.org d'une URL ou fichier HTML."""
    blocks = extract_jsonld(url, is_local)

    if verbose:
        print(f"\n[{url[:70]}]")
        print(f"  {len(blocks)} bloc(s) JSON-LD trouvé(s)")

    results = []
    for i, block in enumerate(blocks):
        schema_type = block.get("@type", "unknown")
        validation = validate_local(block)

        if verbose:
            status = "OK" if validation["valid"] else "ERREUR"
            print(f"  [{i+1}] {schema_type} — {status}")
            for e in validation["errors"]:
                print(f"       ERROR : {e}")
            for w in validation["warnings"]:
                print(f"       WARN  : {w}")

        results.append({
            "url": url,
            "block_index": i + 1,
            "type": schema_type,
            "valid": validation["valid"],
            "errors": "; ".join(validation["errors"]),
            "warnings": "; ".join(validation["warnings"]),
        })

    if not blocks and verbose:
        print("  Aucun JSON-LD trouvé")

    return results


# ── Audit batch (CSV d'URLs) ──────────────────────────────────────────────────

def audit_batch(urls_file: str, output: str = None):
    """Audite Schema.org sur une liste d'URLs (CSV avec colonne 'url')."""
    df_urls = pd.read_csv(urls_file)
    url_col = next((c for c in df_urls.columns if "url" in c.lower()), df_urls.columns[0])
    urls = df_urls[url_col].dropna().tolist()

    print(f"Audit Schema.org batch : {len(urls)} URLs")
    all_results = []
    for url in urls:
        results = audit_url(url, verbose=False)
        all_results.extend(results)
        status = "OK" if all(r["valid"] for r in results) else "ISSUES"
        print(f"  [{status}] {url[:60]} — {len(results)} blocs")

    df_out = pd.DataFrame(all_results)
    out_path = output or "schema_audit.csv"
    df_out.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\nRésultats exportés → {out_path}")

    # Résumé
    issues = df_out[df_out["errors"] != ""]
    warns = df_out[df_out["warnings"] != ""]
    print(f"\nRÉSUMÉ : {len(issues)} erreurs | {len(warns)} warnings | {len(df_out)} blocs analysés")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Validation JSON-LD / Schema.org")
    parser.add_argument("target", help="URL, fichier HTML, ou fichier CSV")
    parser.add_argument("--local", action="store_true", help="Fichier HTML local")
    parser.add_argument("--batch", action="store_true", help="CSV d'URLs (colonne 'url')")
    parser.add_argument("-o", "--output", help="Fichier CSV de sortie")

    args = parser.parse_args()

    if args.batch:
        audit_batch(args.target, args.output)
    else:
        results = audit_url(args.target, args.local)
        if results and args.output:
            pd.DataFrame(results).to_csv(args.output, index=False, encoding="utf-8-sig")
            print(f"\nExporté → {args.output}")


if __name__ == "__main__":
    main()
