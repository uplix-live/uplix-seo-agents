# Agent SEO Refonte & Migration — `/agent-refonte`

Agent SEO de **refonte et migration** packagé et portable, prêt à être partagé à n'importe quel consultant disposant de Claude Code.

## Objectif

Piloter une refonte ou une migration de site **sans perte de trafic**. Le cœur du livrable est un **plan de redirection 301 complet** (mapping `ancienne URL → nouvelle URL`, 1:1 prioritaire), accompagné du snapshot de l'état avant, de la préservation du link equity et du maillage, du plan de bascule et du protocole de contrôle post-migration. Voir `presentation.html` pour la liste complète des contrôles.

## Usage

```
/agent-refonte example.fr
```

L'agent pose ses questions de cadrage (type de refonte, périmètre, préprod, accès, date de bascule), fige l'état actuel, construit le mapping de redirection, génère les règles serveur prêtes à coller, planifie la bascule, puis produit les livrables dans `Audits/<domaine>/livrables/`.

## Contenu du répertoire (autonome)

| Dossier / fichier | Rôle |
|---|---|
| `SKILL.md` | Orchestrateur de l'agent (logique + garde-fous) |
| `presentation.html` | Page de présentation : objectif + tous les contrôles |
| `README.md` | Ce fichier |
| `skills/` | Skills SEO embarqués (seo-technical, seo-sitemap, seo-schema, maillage-systeme, seo-page) |
| `references/` | Seuils de référence — **source de vérité** (thresholds, quality-gates, schema-types, cwv-thresholds) |
| `scripts/` | Scripts Python (fetch_page, parse_html, advertools_utils, validate_schema) |

## Livrables produits

| Fichier | Contenu |
|---|---|
| `Audits/<domaine>/livrables/md/plan-refonte.md` | Plan complet (type, snapshot, mapping, préservation, bascule, post-migration) |
| `Audits/<domaine>/livrables/<domaine>-redirections.csv` | Mapping `ancienne URL → nouvelle URL` (type 301/410, raison, trafic, backlinks, priorité) |
| Règles serveur prêtes à coller | `.htaccess` / nginx / import CMS selon la stack — **livrées, jamais poussées live** |
| Page HTML de restitution (optionnelle) | Design tokens OKLCH du projet, passée à `/polish` |

## Prérequis

- **Claude Code** installé.
- **Python 3.12+** pour les scripts (`pip install advertools beautifulsoup4 lxml extruct requests`).
- **MCP recommandés** (facultatifs mais améliorent la migration) :
  - `screaming-frog` — crawl complet de l'existant et re-crawl post-bascule (préféré pour gros sites).
  - `gsc-lucky` — inventaire des URLs indexées, top pages, inspection d'URL, comparaison de positions avant/après.
  - `ahrefs` — top pages par trafic et **par backlinks** (link equity à préserver), suivi des positions.
  - `chrome-devtools` — CWV labo (Lighthouse) sur la nouvelle version.
- Données Ahrefs/GSC payantes recommandées pour identifier les pages à protéger en priorité, mais non strictement obligatoires (le crawl + sitemap suffisent à un mapping de base).

## Installation chez un autre consultant

1. Copier le dossier `agent-refonte/` dans son `.claude/skills/`.
2. Redémarrer Claude Code (ou recharger les skills).
3. Taper `/agent-refonte <domaine>`.

> Voir la doc de distribution globale du projet : `../../DISTRIBUTION-AGENTS.md`.

## Périmètre

Centré sur la **refonte / migration** : snapshot avant, mapping 301, préservation, bascule, contrôle après. Pour un audit technique pur (CWV, rendu, sécurité) → `/agent-technique` ; pour la stratégie sémantique / mots-clés → `/agent-semantique` ; pour la rédaction de contenu neuf → `/agent-redaction`.

## Garde-fou principal

L'agent **génère** les redirections et les règles serveur ; il ne les **déploie jamais** sans confirmation explicite. Mapping **1:1 obligatoire** sur toute page à trafic/backlinks, **jamais de redirection en masse vers la home** (signal soft-404), et **aucune chaîne ni boucle** de redirection.
