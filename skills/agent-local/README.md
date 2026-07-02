# Agent SEO Local — `/agent-local`

Agent **SEO local** packagé et portable, prêt à être partagé à n'importe quel consultant disposant de Claude Code.

## Objectif

Auditer la visibilité **géolocalisée** d'un domaine : cohérence NAP (Name/Address/Phone), Google Business Profile (GBP/GMB), pages locales (location pages), local pack & positions « service + ville », Schema LocalBusiness/Organization, avis & e-réputation. Voir `presentation.html` pour la liste complète des contrôles.

## Usage

```
/agent-local example.fr
```

L'agent pose ses questions de cadrage (type d'activité mono vs réseau, villes ciblées, présence GBP, accès, concurrents, objectif), collecte les données, analyse contre les seuils embarqués, priorise par impact × effort, puis produit les livrables dans `Audits/<domaine>/livrables/`.

## Contenu du répertoire (autonome)

| Dossier / fichier | Rôle |
|---|---|
| `SKILL.md` | Orchestrateur de l'agent (logique + garde-fous) |
| `presentation.html` | Page de présentation : objectif + tous les contrôles |
| `README.md` | Ce fichier |
| `skills/` | Skills SEO embarqués (seo-plan avec template **local-service**, seo-schema, seo-content, maillage-systeme, seo-page) |
| `references/` | Seuils de référence — **source de vérité** (quality-gates pour les pages locales, thresholds, schema-types, eeat-framework) |
| `scripts/` | Scripts Python (fetch_page, parse_html, validate_schema) |

## Livrables produits

- `Audits/<domaine>/livrables/md/audit-local.md` — rapport complet, recos auto-suffisantes.
- `Audits/<domaine>/livrables/<domaine>-pages-locales.xlsx` — une ligne par ville/zone (page, mots/unicité, Schema, maillage, position).
- `Audits/<domaine>/livrables/<domaine>-nap-citations.xlsx` — cohérence NAP source par source.
- Snippets JSON-LD **LocalBusiness** prêts à coller, validés.

## Prérequis

- **Claude Code** installé.
- **Python 3.12+** pour les scripts (`pip install beautifulsoup4 lxml extruct requests`).
- **MCP recommandés** :
  - **Haloscan** (marché FR) — backlinks GMB : `get_domains_gmb_backlinks`, `get_domains_gmb_backlinks_categories`, `get_domains_gmb_backlinks_map` + positions géolocalisées. ⚠️ **FR uniquement** : sur un marché hors-France (BE, CH, CA…) ces outils renvoient `NO_RESULT` → vérifier le GBP manuellement (Google Business Profile Manager) ou via un outil local du pays.
  - **gsc-lucky** (Google Search Console) — requêtes locales par device, pages locales qui rankent.
  - **Ahrefs** — concurrents locaux, SERP overview, croisement multi-pays.
- Clés API : `HALOSCAN` configuré dans `.mcp.json`. Pas de clé supplémentaire obligatoire pour les scripts.

## Installation chez un autre consultant

1. Copier le dossier `agent-local/` dans son `.claude/skills/`.
2. Redémarrer Claude Code (ou recharger les skills).
3. Taper `/agent-local <domaine>`.

> Voir la doc de distribution globale du projet : `../../DISTRIBUTION-AGENTS.md`.

## Périmètre

Strictement local (visibilité géolocalisée, GBP, NAP, pages locales, local pack). Pour le reste, renvoyer vers l'agent dédié :
- Audit technique pur (CWV, crawl, indexation, sécurité) → `/agent-technique`
- Stratégie sémantique nationale & content gap → `/agent-semantique`
- Création / refresh de contenu → `/agent-redaction`
- Refonte / migration sans perte de trafic → `/agent-refonte`
