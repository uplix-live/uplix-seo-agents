"""Gate qualité pré-push — 14 marqueurs obligatoires avant tout push WordPress.

Valide le HTML final (02-page-optimisee.html) AVANT le push. Le push est interdit
tant que ce script ne retourne pas exit code 0 (14/14 OK).

Usage:
    python markers_check.py 02-page-optimisee.html \
        --title "Nouveau title de la page" \
        --excerpt "Nouvelle meta description" \
        --domain uplix.fr \
        [--min-words 2700] [--allow-h1]

Exit codes:
    0 = 14/14 marqueurs OK → push autorisé
    1 = au moins un marqueur KO → push INTERDIT (corriger puis relancer)
    2 = erreur d'usage (fichier introuvable, argument manquant)
"""
import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FORBIDDEN_SCHEMA_TYPES = {"HowTo", "SpecialAnnouncement", "FAQPage"}


def strip_tags(html: str) -> str:
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html).strip()


def extract_jsonld(html: str) -> list[dict]:
    blocks = re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, flags=re.S | re.I,
    )
    out = []
    for b in blocks:
        try:
            data = json.loads(b.strip())
            out.extend(data if isinstance(data, list) else [data])
        except json.JSONDecodeError:
            out.append({"__parse_error__": True})
    return out


def jsonld_types(items: list[dict]) -> set[str]:
    types: set[str] = set()
    for it in items:
        t = it.get("@type")
        if isinstance(t, str):
            types.add(t)
        elif isinstance(t, list):
            types.update(x for x in t if isinstance(x, str))
        for v in it.get("@graph", []) if isinstance(it.get("@graph"), list) else []:
            if isinstance(v, dict):
                types.update(jsonld_types([v]))
    return types


def main() -> int:
    p = argparse.ArgumentParser(description="Gate qualité pré-push (14 marqueurs)")
    p.add_argument("html_file", help="Fichier HTML final à valider (content WP)")
    p.add_argument("--title", required=True, help="Title prévu pour le push")
    p.add_argument("--excerpt", required=True, help="Meta description prévue")
    p.add_argument("--domain", required=True, help="Domaine cible (ex: uplix.fr)")
    p.add_argument("--min-words", type=int, default=2700)
    p.add_argument("--allow-h1", action="store_true",
                   help="Autoriser un <h1> dans le content (si le thème ne rend pas le title en H1)")
    args = p.parse_args()

    path = Path(args.html_file)
    if not path.exists():
        print(f"ERR: fichier introuvable: {path}")
        return 2
    html = path.read_text(encoding="utf-8", errors="replace")

    results: list[tuple[str, bool, str]] = []

    def check(label: str, ok: bool, detail: str):
        results.append((label, ok, detail))

    # 1. Title 50-60 caractères (tolérance 45-65)
    tlen = len(args.title)
    check("01 Title 50-60 car", 45 <= tlen <= 65, f"{tlen} car : {args.title!r}")

    # 2. Meta description 145-160 caractères (tolérance 120-165)
    elen = len(args.excerpt)
    check("02 Meta desc 145-160 car", 120 <= elen <= 165, f"{elen} car")

    # 3. Pas de double H1 (le thème WP rend le title en H1)
    h1s = re.findall(r"<h1[\s>]", html, flags=re.I)
    ok_h1 = (len(h1s) == 1) if args.allow_h1 else (len(h1s) == 0)
    check("03 H1 unique (0 dans content, thème rend le title)" if not args.allow_h1
          else "03 H1 unique (1 dans content)", ok_h1, f"{len(h1s)} <h1> trouvés")

    # 4. Structure: >= 6 H2 avec anchors id
    h2s = re.findall(r"<h2[\s>]", html, flags=re.I)
    h2_ids = re.findall(r"<h2[^>]*\sid=", html, flags=re.I)
    check("04 >= 6 H2 avec id (anchors)", len(h2s) >= 6 and len(h2_ids) >= len(h2s) - 1,
          f"{len(h2s)} H2 dont {len(h2_ids)} avec id")

    # 5. >= 3 H3
    h3s = re.findall(r"<h3[\s>]", html, flags=re.I)
    check("05 >= 3 H3", len(h3s) >= 3, f"{len(h3s)} H3")

    # 6. Word count
    words = len(strip_tags(html).split())
    check(f"06 Word count >= {args.min_words}", words >= args.min_words, f"{words} mots")

    # 7. TL;DR / résumé en tête
    has_tldr = bool(re.search(r"(tl\s*;?\s*dr|l['’]essentiel|en\s+bref|à\s+retenir|resume|résumé)",
                              html[:6000], flags=re.I))
    check("07 TL;DR / encadré résumé en tête", has_tldr, "détecté" if has_tldr else "absent des 6000 premiers car")

    # 8. FAQ accordéon >= 8 <details><summary>
    details = re.findall(r"<details[\s>]", html, flags=re.I)
    summaries = re.findall(r"<summary[\s>]", html, flags=re.I)
    check("08 FAQ >= 8 <details><summary>", len(details) >= 8 and len(summaries) >= 8,
          f"{len(details)} <details>, {len(summaries)} <summary>")

    # 9. >= 1 tableau comparatif (idéal 2)
    tables = re.findall(r"<table[\s>]", html, flags=re.I)
    check("09 >= 1 tableau (idéal 2)", len(tables) >= 1, f"{len(tables)} <table>")

    # 10. Images : >= 3 inline, alt non vide partout, loading=lazy, pas de Supabase
    imgs = re.findall(r"<img[^>]*>", html, flags=re.I)
    missing_alt = [i for i in imgs if not re.search(r'alt=["\'][^"\']+["\']', i, flags=re.I)]
    missing_lazy = [i for i in imgs if "loading=" not in i.lower()]
    supabase = [i for i in imgs if "supabase" in i.lower()]
    ok_img = len(imgs) >= 3 and not missing_alt and not missing_lazy and not supabase
    check("10 >= 3 images inline (alt + lazy, pas d'URL Supabase)", ok_img,
          f"{len(imgs)} img, {len(missing_alt)} sans alt, {len(missing_lazy)} sans lazy, {len(supabase)} Supabase")

    # 11. JSON-LD valide, sans types interdits
    ld = extract_jsonld(html)
    parse_errors = any(it.get("__parse_error__") for it in ld)
    types = jsonld_types([it for it in ld if not it.get("__parse_error__")])
    forbidden = types & FORBIDDEN_SCHEMA_TYPES
    ok_ld = bool(ld) and not parse_errors and not forbidden
    check("11 JSON-LD présent, parseable, sans HowTo/FAQPage/SpecialAnnouncement", ok_ld,
          f"types={sorted(types) or 'aucun'}, parse_errors={parse_errors}, interdits={sorted(forbidden) or 'aucun'}")

    # 12. Maillage : >= 5 liens internes avec >= 4 ancres distinctes
    domain = args.domain.lower().removeprefix("www.")
    links = re.findall(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, flags=re.S | re.I)
    internal = [(h, strip_tags(a)) for h, a in links if domain in h.lower()]
    anchors = {a.lower().strip() for _, a in internal if a.strip()}
    check("12 >= 5 liens internes, ancres variées (>= 4 distinctes)",
          len(internal) >= 5 and len(anchors) >= 4,
          f"{len(internal)} liens internes, {len(anchors)} ancres distinctes")

    # 13. >= 1 lien externe sortant (source officielle)
    external = [h for h, _ in links
                if h.lower().startswith("http") and domain not in h.lower()]
    check("13 >= 1 lien externe (source officielle)", len(external) >= 1, f"{len(external)} liens externes")

    # 14. Fraîcheur + auteur : date "Mis à jour" + mention auteur/équipe
    has_date = bool(re.search(r"mis\s+à\s+jour\s+le", html, flags=re.I))
    has_author = bool(re.search(r"(par\s+l['’]équipe|auteur|rédigé\s+par|écrit\s+par)", html, flags=re.I))
    check("14 Date 'Mis à jour le' + auteur visibles", has_date and has_author,
          f"date={'OK' if has_date else 'KO'}, auteur={'OK' if has_author else 'KO'}")

    print("=== GATE QUALITÉ PRÉ-PUSH — 14 marqueurs obligatoires ===\n")
    ok_count = 0
    for label, ok, detail in results:
        ok_count += ok
        print(f"  [{'OK' if ok else 'KO'}] {label} — {detail}")
    print(f"\n  → {ok_count}/14 marqueurs OK")
    if ok_count == 14:
        print("  ✓ GATE PASSÉE — push autorisé")
        return 0
    print("  ✗ GATE BLOQUÉE — push INTERDIT. Corriger les marqueurs KO puis relancer.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
