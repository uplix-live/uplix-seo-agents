# Agent SEO Technique — `/agent-technique`

Agent SEO **technique pur** packagé et portable, prêt à être partagé à n'importe quel consultant disposant de Claude Code.

## Objectif

Auditer les aspects strictement techniques d'un domaine : performance / temps de chargement (Core Web Vitals, INP, LCP, CLS), Schema.org, crawlabilité, indexabilité, rendu JS, sécurité, robots/sitemap, structure d'URL. Voir `presentation.html` pour la liste complète des contrôles.

## Usage

```
/agent-technique example.fr
```

L'agent pose ses questions de cadrage, collecte les données, analyse contre les seuils embarqués, priorise par impact × effort, puis produit les livrables dans `Audits/<domaine>/livrables/`.

## Contenu du répertoire (autonome)

| Dossier / fichier | Rôle |
|---|---|
| `SKILL.md` | Orchestrateur de l'agent (logique + garde-fous) |
| `presentation.html` | Page de présentation : objectif + tous les contrôles |
| `README.md` | Ce fichier |
| `skills/` | Skills SEO techniques embarqués (seo-technical, seo-schema, seo-images, seo-sitemap) |
| `references/` | Seuils de référence — **source de vérité** (cwv-thresholds, schema-types, thresholds, quality-gates) |
| `scripts/` | Scripts Python (fetch_page, parse_html, validate_schema, capture_screenshot, analyze_visual, advertools_utils) |

## Prérequis

- **Claude Code** installé.
- **Python 3.12+** pour les scripts (`pip install advertools beautifulsoup4 lxml extruct playwright requests`).
- **MCP recommandés** (facultatifs mais améliorent l'audit) : `chrome-devtools` (Lighthouse, traces perf), `screaming-frog` (crawl gros sites), `gsc-lucky` (CWV terrain + indexation), `playwright` (rendu mobile).
- Pas de clé API payante obligatoire pour cet agent.

## Installation chez un autre consultant

1. Copier le dossier `agent-technique/` dans son `.claude/skills/`.
2. Redémarrer Claude Code (ou recharger les skills).
3. Taper `/agent-technique <domaine>`.

> Voir la doc de distribution globale du projet : `../../DISTRIBUTION-AGENTS.md`.

## Périmètre

Strictement technique. Pour la sémantique → `/agent-semantique`, le contenu → `/agent-redaction`, une refonte/migration → `/agent-refonte`.
