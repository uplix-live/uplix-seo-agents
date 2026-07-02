"""
lint_post.py — Linter de contenu SEO DÉTERMINISTE (français)

Vérifie la structure et la citabilité GEO d'un article Markdown avant publication.
Inspiré des linters de contenu type easygrowth, mais ADAPTÉ AU FRANÇAIS
(notamment : les tirets cadratins em-dash sont TOLÉRÉS, simple compteur informatif).

Règles vérifiées :
  1. Hiérarchie Hn          — exactement 1 H1, pas de saut de niveau (H2→H4)      [ERREUR]
  2. Three Kings            — KW principal dans title/H1 + 1er § + ≥ 2 H2          [ERREUR]
  3. Ratio Content Capsule  — 55–75 % des H2 formulés en question                  [WARNING]
  4. 1re phrase auto-suffisante — pas de pronom de reprise après un H2-question    [WARNING]
  5. Ancres de lien 1–3 mots — pas d'ancre > 3 mots ni générique ("ici"…)          [WARNING]
  6. Phrases bannies / remplissage FR                                              [WARNING]
  7. Exclusion concurrents  — flag toute mention (--competitors)                   [WARNING]
  8. Word count             — écart > ±25 % de la cible (--target)                 [WARNING]
  9. TL;DR présent          — bloc de 3–5 puces avant le 1er H2                     [WARNING]

Usage :
    python scripts/lint_post.py article.md
    python scripts/lint_post.py article.md --keyword "agence seo"
    python scripts/lint_post.py article.md --keyword "agence seo" --competitors "eskimoz.fr,semji.com"
    python scripts/lint_post.py article.md --keyword "agence seo" --target 3000
    python scripts/lint_post.py article.md --keyword "agence seo" --json

Codes de sortie :
    0 = OK (aucun warning, aucune erreur)
    1 = warnings uniquement
    2 = au moins une erreur bloquante
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

# Fix Windows cp1252 encoding issues
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ── Constantes / regex ────────────────────────────────────────────────────────

# Hiérarchie de titres Markdown (## …) — capture le niveau et le texte
RE_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")

# Lien markdown [texte](url)
RE_MD_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

# Mots interrogatifs FR pour détecter une H2 « question » (Content Capsule)
INTERROGATIVE_WORDS = (
    "comment", "pourquoi", "quoi", "quel", "quelle", "quels", "quelles",
    "combien", "où", "quand", "qui", "qu'est-ce", "est-ce", "lequel",
    "laquelle", "lesquels", "lesquelles", "à quoi", "à quel",
)

# Pronoms / déterminants de reprise interdits en 1re phrase de section (auto-suffisance)
DEPENDENT_OPENERS = (
    "il", "elle", "ils", "elles", "cela", "ça", "ce", "cet", "cette", "ces",
    "celui", "celle", "ceux", "celles", "leur", "leurs", "y", "en",
    "ceci", "lui",
)

# Ancres génériques interdites (texte de lien non descriptif)
GENERIC_ANCHORS = (
    "ici", "cliquez ici", "cliquer ici", "clique ici", "en savoir plus",
    "ce lien", "cette page", "ce site", "lien", "page", "voir ici",
    "lire la suite", "découvrez", "voir plus", "cliquez", "ce document",
)

# Phrases bannies / remplissage (français)
BANNED_PHRASES = (
    "il est important de noter",
    "il est important de souligner",
    "il convient de noter",
    "il est à noter",
    "dans le monde d'aujourd'hui",
    "dans le monde actuel",
    "de nos jours",
    "force est de constater",
    "à l'ère du numérique",
    "à l'heure actuelle",
    "à l'heure du numérique",
    "last but not least",
    "il va sans dire",
    "comme chacun sait",
    "comme nous l'avons vu",
    "en effet, il est",
    "force est de reconnaître",
    "il n'est plus à prouver",
    "n'est plus un secret pour personne",
    "au jour d'aujourd'hui",
)

# Ratio Content Capsule (part des H2 en question)
CAPSULE_MIN = 0.55
CAPSULE_MAX = 0.75

# Écart de word count toléré
WORDCOUNT_TOLERANCE = 0.25

# Ancre de lien : nombre de mots max
ANCHOR_MAX_WORDS = 3


# ── Utilitaires ───────────────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """Minuscule + suppression des accents, pour comparaisons robustes."""
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text


def _strip_md(text: str) -> str:
    """Retire le balisage markdown inline d'une ligne (gras, italique, liens, code)."""
    text = RE_MD_LINK.sub(r"\1", text)          # [texte](url) -> texte
    text = re.sub(r"[*_`#>]", "", text)
    return text.strip()


def _first_word(text: str) -> str:
    text = _strip_md(text).strip()
    text = re.sub(r"^[^\wàâäéèêëïîôöùûüç']+", "", text, flags=re.IGNORECASE)
    m = re.match(r"([\wàâäéèêëïîôöùûüç']+)", text, flags=re.IGNORECASE)
    return m.group(1) if m else ""


def _is_question(heading_text: str) -> bool:
    """Une H2 est une « question » si elle se termine par ? ou commence par un interrogatif."""
    txt = _strip_md(heading_text).strip()
    if txt.endswith("?"):
        return True
    norm = _normalize(txt)
    return any(norm.startswith(w + " ") or norm == w for w in (_normalize(x) for x in INTERROGATIVE_WORDS))


def _word_count(lines: list[str]) -> int:
    """Compte les mots du corps (hors titres, hors blocs de code, hors balisage)."""
    in_code = False
    words = 0
    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if RE_HEADING.match(line):
            continue
        plain = _strip_md(line)
        words += len([w for w in re.split(r"\s+", plain) if w])
    return words


def _split_front_matter(lines: list[str]) -> tuple[dict, list[str], int]:
    """Sépare un éventuel front-matter YAML. Renvoie (meta, lignes_corps, offset)."""
    meta: dict = {}
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                for raw in lines[1:i]:
                    if ":" in raw:
                        k, v = raw.split(":", 1)
                        meta[k.strip().lower()] = v.strip().strip('"').strip("'")
                return meta, lines[i + 1:], i + 1
    return meta, lines, 0


def _make(level: str, line: int, rule: str, message: str) -> dict:
    return {"level": level, "line": line, "rule": rule, "message": message}


# ── Règle 1 : Hiérarchie Hn ───────────────────────────────────────────────────

def check_hierarchy(headings: list[tuple], findings: list[dict]) -> None:
    h1 = [h for h in headings if h[0] == 1]
    if len(h1) == 0:
        findings.append(_make("error", 0, "hierarchie", "Aucun H1 trouvé (exactement 1 requis)."))
    elif len(h1) > 1:
        for lvl, txt, ln in h1[1:]:
            findings.append(_make("error", ln, "hierarchie",
                                  f"H1 multiple détecté (« {txt[:50]} »). Un seul H1 autorisé."))

    prev = None
    for lvl, txt, ln in headings:
        if prev is not None and lvl > prev + 1:
            findings.append(_make("error", ln, "hierarchie",
                                  f"Saut de niveau H{prev}→H{lvl} (« {txt[:50]} »). "
                                  f"Ne pas sauter de niveau."))
        prev = lvl


# ── Règle 2 : Three Kings ─────────────────────────────────────────────────────

def check_three_kings(keyword: str, title: str, first_para: str,
                      headings: list[tuple], findings: list[dict]) -> None:
    if not keyword:
        findings.append(_make("warning", 0, "three-kings",
                              "Aucun --keyword fourni : Three Kings non vérifié."))
        return
    kw = _normalize(keyword)

    if kw not in _normalize(title):
        findings.append(_make("error", 0, "three-kings",
                              f"KW principal « {keyword} » absent du title/H1."))

    if kw not in _normalize(first_para):
        findings.append(_make("error", 0, "three-kings",
                              f"KW principal « {keyword} » absent du 1er paragraphe."))

    h2_with_kw = [h for h in headings if h[0] == 2 and kw in _normalize(h[1])]
    if len(h2_with_kw) < 2:
        findings.append(_make("error", 0, "three-kings",
                              f"KW principal « {keyword} » présent dans seulement "
                              f"{len(h2_with_kw)} H2 (≥ 2 requis)."))


# ── Règle 3 : Ratio Content Capsule ───────────────────────────────────────────

def check_capsule_ratio(headings: list[tuple], findings: list[dict]) -> None:
    h2 = [h for h in headings if h[0] == 2]
    if not h2:
        findings.append(_make("warning", 0, "content-capsule", "Aucune H2 trouvée."))
        return
    questions = [h for h in h2 if _is_question(h[1])]
    ratio = len(questions) / len(h2)
    if not (CAPSULE_MIN <= ratio <= CAPSULE_MAX):
        findings.append(_make("warning", 0, "content-capsule",
                              f"{len(questions)}/{len(h2)} H2 en question "
                              f"({ratio:.0%}) — hors plage cible {CAPSULE_MIN:.0%}–{CAPSULE_MAX:.0%}."))


# ── Règle 4 : 1re phrase de section auto-suffisante ───────────────────────────

def check_self_sufficient(sections: list[dict], findings: list[dict]) -> None:
    for sec in sections:
        if sec["level"] != 2 or not _is_question(sec["heading"]):
            continue
        first = sec["first_sentence"]
        if not first:
            findings.append(_make("warning", sec["line"], "auto-suffisance",
                                  f"H2-question « {sec['heading'][:40]} » sans phrase de réponse."))
            continue
        fw = _normalize(_first_word(first))
        if fw in (_normalize(x) for x in DEPENDENT_OPENERS):
            findings.append(_make("warning", sec["first_line"], "auto-suffisance",
                                  f"1re phrase de « {sec['heading'][:40]} » commence par un pronom "
                                  f"de reprise (« {_first_word(first)} ») — la rendre auto-suffisante."))


# ── Règle 5 : Ancres de lien 1–3 mots ─────────────────────────────────────────

def check_anchors(body_lines: list[str], offset: int, findings: list[dict]) -> None:
    for idx, line in enumerate(body_lines, start=offset + 1):
        for m in RE_MD_LINK.finditer(line):
            anchor = m.group(1).strip()
            norm = _normalize(anchor)
            if norm in (_normalize(x) for x in GENERIC_ANCHORS):
                findings.append(_make("warning", idx, "ancre",
                                      f"Ancre générique « {anchor} » — utiliser une ancre descriptive 1–3 mots."))
                continue
            n_words = len([w for w in re.split(r"\s+", anchor) if w])
            if n_words > ANCHOR_MAX_WORDS:
                findings.append(_make("warning", idx, "ancre",
                                      f"Ancre « {anchor[:40]} » fait {n_words} mots (max {ANCHOR_MAX_WORDS})."))


# ── Règle 6 : Phrases bannies / remplissage ───────────────────────────────────

def check_banned_phrases(body_lines: list[str], offset: int, findings: list[dict]) -> None:
    for idx, line in enumerate(body_lines, start=offset + 1):
        norm = _normalize(line)
        for phrase in BANNED_PHRASES:
            if _normalize(phrase) in norm:
                findings.append(_make("warning", idx, "remplissage",
                                      f"Phrase de remplissage : « {phrase} »."))


# ── Règle 7 : Exclusion concurrents ───────────────────────────────────────────

def check_competitors(body_lines: list[str], offset: int,
                      competitors: list[str], findings: list[dict]) -> None:
    if not competitors:
        return
    comps = [(_normalize(c.strip()), c.strip()) for c in competitors if c.strip()]
    for idx, line in enumerate(body_lines, start=offset + 1):
        norm = _normalize(line)
        for cn, cd in comps:
            if cn and cn in norm:
                findings.append(_make("warning", idx, "concurrent",
                                      f"Mention d'un concurrent exclu : « {cd} »."))


# ── Règle 8 : Word count ──────────────────────────────────────────────────────

def check_word_count(wc: int, target: int, findings: list[dict]) -> None:
    if not target:
        return
    low = target * (1 - WORDCOUNT_TOLERANCE)
    high = target * (1 + WORDCOUNT_TOLERANCE)
    if wc < low or wc > high:
        findings.append(_make("warning", 0, "word-count",
                              f"Word count {wc} hors plage ±{WORDCOUNT_TOLERANCE:.0%} "
                              f"de la cible {target} ({int(low)}–{int(high)})."))


# ── Règle 9 : TL;DR présent ───────────────────────────────────────────────────

def check_tldr(body_lines: list[str], headings: list[tuple],
               offset: int, findings: list[dict]) -> None:
    # Ligne du 1er H2 (limite de recherche du TL;DR)
    first_h2_line = None
    for lvl, _txt, ln in headings:
        if lvl == 2:
            first_h2_line = ln
            break

    bullets = 0
    has_tldr_marker = False
    for idx, line in enumerate(body_lines, start=offset + 1):
        if first_h2_line is not None and idx >= first_h2_line:
            break
        norm = _normalize(line)
        if "tl;dr" in norm or "en résumé" in line.lower() or "a retenir" in norm or "l'essentiel" in line.lower():
            has_tldr_marker = True
        if re.match(r"^\s*([-*+]|\d+\.)\s+\S", line):
            bullets += 1

    if not (3 <= bullets <= 5) and not has_tldr_marker:
        findings.append(_make("warning", 0, "tldr",
                              f"TL;DR absent ou mal formé avant le 1er H2 "
                              f"({bullets} puces trouvées, 3–5 attendues)."))


# ── Analyse du document ───────────────────────────────────────────────────────

def parse_document(body_lines: list[str], offset: int, meta: dict) -> dict:
    """Extrait titres, sections, title, 1er paragraphe, em-dash count."""
    headings: list[tuple] = []          # (level, text, line_no)
    in_code = False
    for idx, line in enumerate(body_lines, start=offset + 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = RE_HEADING.match(line)
        if m:
            headings.append((len(m.group(1)), _strip_md(m.group(2)), idx))

    # Title = front-matter "title" sinon premier H1
    title = meta.get("title", "")
    if not title:
        for lvl, txt, _ln in headings:
            if lvl == 1:
                title = txt
                break

    # 1er paragraphe = première ligne de texte non vide après le H1 (hors titres/code)
    first_para = ""
    in_code = False
    h1_seen = not any(h[0] == 1 for h in headings)
    for line in body_lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = RE_HEADING.match(line)
        if m:
            if len(m.group(1)) == 1:
                h1_seen = True
            continue
        if h1_seen and line.strip():
            first_para = _strip_md(line)
            break

    # Sections : 1re phrase après chaque H2
    sections = _build_sections(body_lines, offset)

    # Compteur informatif em-dash (toléré en FR)
    emdash = sum(line.count("—") for line in body_lines)

    return {
        "headings": headings,
        "title": title,
        "first_para": first_para,
        "sections": sections,
        "emdash": emdash,
        "word_count": _word_count(body_lines),
    }


def _build_sections(body_lines: list[str], offset: int) -> list[dict]:
    sections: list[dict] = []
    current = None
    in_code = False
    for idx, line in enumerate(body_lines, start=offset + 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = RE_HEADING.match(line)
        if m:
            if current is not None:
                sections.append(current)
            current = {"level": len(m.group(1)), "heading": _strip_md(m.group(2)),
                       "line": idx, "first_sentence": "", "first_line": idx}
            continue
        if current is not None and not current["first_sentence"] and line.strip():
            plain = _strip_md(line)
            if plain:
                # 1re phrase = jusqu'au premier . ! ? (ou ligne entière)
                m2 = re.match(r"(.+?[.!?])(\s|$)", plain)
                current["first_sentence"] = m2.group(1) if m2 else plain
                current["first_line"] = idx
    if current is not None:
        sections.append(current)
    return sections


# ── Orchestration ─────────────────────────────────────────────────────────────

def lint(path: Path, keyword: str = "", competitors: list[str] | None = None,
         target: int = 0) -> tuple[list[dict], dict]:
    raw = path.read_text(encoding="utf-8", errors="replace").splitlines()
    meta, body, offset = _split_front_matter(raw)
    doc = parse_document(body, offset, meta)

    findings: list[dict] = []
    check_hierarchy(doc["headings"], findings)
    check_three_kings(keyword, doc["title"], doc["first_para"], doc["headings"], findings)
    check_capsule_ratio(doc["headings"], findings)
    check_self_sufficient(doc["sections"], findings)
    check_anchors(body, offset, findings)
    check_banned_phrases(body, offset, findings)
    check_competitors(body, offset, competitors or [], findings)
    check_word_count(doc["word_count"], target, findings)
    check_tldr(body, doc["headings"], offset, findings)

    stats = {
        "file": str(path),
        "word_count": doc["word_count"],
        "headings": len(doc["headings"]),
        "h2": len([h for h in doc["headings"] if h[0] == 2]),
        "emdash": doc["emdash"],
        "errors": sum(1 for f in findings if f["level"] == "error"),
        "warnings": sum(1 for f in findings if f["level"] == "warning"),
    }
    findings.sort(key=lambda f: (f["line"], 0 if f["level"] == "error" else 1))
    return findings, stats


def _print_human(findings: list[dict], stats: dict) -> None:
    print(f"\nLinter de contenu — {stats['file']}")
    print("─" * 60)
    for f in findings:
        loc = f"L{f['line']}" if f["line"] else "—"
        tag = "ERREUR " if f["level"] == "error" else "warning"
        print(f"  [{tag}] {loc:>5}  ({f['rule']}) {f['message']}")
    if not findings:
        print("  Aucun problème détecté.")
    print("─" * 60)
    print(f"  Mots : {stats['word_count']} · H2 : {stats['h2']} · "
          f"em-dash (toléré, info) : {stats['emdash']}")
    print(f"  Résultat : {stats['errors']} erreur(s) / {stats['warnings']} warning(s)")
    if stats["errors"]:
        print("  -> ERREURS BLOQUANTES : corriger avant publication.")
    elif stats["warnings"]:
        print("  -> Warnings : à revoir, non bloquant.")
    else:
        print("  -> OK.")
    print()


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Linter de contenu SEO déterministe (français).")
    ap.add_argument("file", help="Fichier Markdown à analyser")
    ap.add_argument("--keyword", default="", help="Mot-clé principal (Three Kings)")
    ap.add_argument("--competitors", default="",
                    help="Domaines concurrents à exclure, séparés par des virgules")
    ap.add_argument("--target", type=int, default=0,
                    help="Word count cible (flag si écart > ±25 %)")
    ap.add_argument("--json", action="store_true", help="Sortie JSON")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.is_file():
        print(f"ERROR: fichier introuvable : {path}", file=sys.stderr)
        return 2

    competitors = [c for c in args.competitors.split(",") if c.strip()]
    findings, stats = lint(path, args.keyword, competitors, args.target)

    if args.json:
        print(json.dumps({"stats": stats, "findings": findings},
                         ensure_ascii=False, indent=2))
    else:
        _print_human(findings, stats)

    if stats["errors"]:
        return 2
    if stats["warnings"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
