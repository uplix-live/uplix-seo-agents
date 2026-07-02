# Agent SEO Sémantique — `/agent-semantique`

Agent SEO **sémantique et concurrentiel** packagé et portable, prêt à être partagé à n'importe quel consultant disposant de Claude Code.

## Objectif

Donner une **vue sémantique complète** d'un domaine et la confronter à ses concurrents : cartographie des mots-clés positionnés, clustering par univers, intention de recherche, cannibalisation, et surtout le **content gap** — le champ sémantique des concurrents sur lequel le client est absent (territoires à conquérir) — puis la construction des cocons sémantiques. Voir `presentation.html` pour la liste complète des contrôles.

## Usage

```
/agent-semantique example.fr
```

L'agent pose ses questions de cadrage, collecte les données (en croisant min. 2 sources), clusterise l'univers de mots-clés, détecte la cannibalisation, révèle les territoires concurrentiels à conquérir, structure les cocons, puis produit les livrables dans `Audits/<domaine>/livrables/`.

## Contenu du répertoire (autonome)

| Dossier / fichier | Rôle |
|---|---|
| `SKILL.md` | Orchestrateur de l'agent (logique + garde-fous) |
| `presentation.html` | Page de présentation : objectif + tous les contrôles |
| `README.md` | Ce fichier |
| `skills/` | Skills SEO sémantiques embarqués (seo-plan, seo-programmatic, seo-content, geo-compare, seo-competitor-pages, maillage-systeme) |
| `references/` | Seuils de référence — **source de vérité** (thresholds, quality-gates, eeat-framework, **bvs** = Business Value Score) |
| `scripts/` | Scripts Python (fetch_page, parse_html, parse_volumes, parse_site_structure_v2) |

## Prérequis

- **Claude Code** installé.
- **Python 3.12+** + le package `seo-toolkit` du projet pour les analyses sémantiques A1-A4 (`cluster`, `cannibalization`, `content-gap`, `intent`). Embeddings FR : `dangvantuan/sentence-camembert-large`, EN : `all-MiniLM-L6-v2`.
- **MCP requis** (au moins une source FR + une source de validation) :
  - **Haloscan** (marché FR) — `get_domains_overview`, `get_domains_keywords`, `get_domains_competitors`, `get_domains_competitors_keywords_diff` (le content gap FR), `get_keywords_find/match/similar/related/questions`, `get_keywords_site_structure`.
  - **Ahrefs** (multi-pays) — `site-explorer-organic-keywords`, `site-explorer-organic-competitors`, `competitors-overview`, `keywords-explorer-matching-terms/related-terms`, `serp-overview`.
  - **GSC** (`gsc-lucky`) — requêtes réelles, opportunités, validation du trafic.
- Au moins **2 sources** doivent être disponibles pour valider un insight (cf. garde-fous). Sans MCP payant, l'agent reste utilisable sur exports CSV locaux + GSC, en mode dégradé.

## Installation chez un autre consultant

1. Copier le dossier `agent-semantique/` dans son `.claude/skills/`.
2. Configurer les MCP Haloscan / Ahrefs / GSC dans son `.mcp.json` (clés API).
3. Redémarrer Claude Code (ou recharger les skills).
4. Taper `/agent-semantique <domaine>`.

> Voir la doc de distribution globale du projet : `../../DISTRIBUTION-AGENTS.md`.

## Périmètre

Strictement sémantique et concurrentiel. Pour la technique (CWV, crawl, indexation, schema, sécurité) → `/agent-technique`, le contenu/rédaction → `/agent-redaction`, une refonte/migration → `/agent-refonte`.
