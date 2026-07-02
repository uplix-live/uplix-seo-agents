# Agents SEO Uplix — pour Claude Code

Agents SEO autonomes et portables pour [Claude Code](https://claude.com/claude-code). Chaque agent pose ses questions de cadrage, exécute son audit en croisant plusieurs sources (Haloscan, Ahrefs, GSC…), puis produit des livrables (`.md`, HTML, Excel) dans `Audits/<domaine>/`.

## Agents (orchestrateurs)

| Commande | Spécialité |
|---|---|
| `/agent-technique example.fr` | Audit technique : performance/CWV, Schema.org, crawl, indexation, rendu JS, sécurité |
| `/agent-semantique example.fr` | Cartographie sémantique, clustering, cannibalisation, content gap concurrents, cocons |
| `/agent-redaction example.fr` | Mots-clés GSC par URL, URLs entrantes/sortantes du ranking, content refresh, rédaction E-E-A-T |
| `/agent-refonte example.fr` | Refonte/migration : plan de redirection 301, préservation du link equity, contrôle post-migration |
| `/agent-local example.fr` | SEO local : NAP, Google Business Profile, pages locales, local pack, Schema LocalBusiness, avis |
| `/agent-monitoring example.fr` | Suivi récurrent : positions, indexation, trafic GSC, CWV, alertes sur dérives |

## Skills complémentaires

| Commande | Usage |
|---|---|
| `/seo-audit-setup example.fr` | Prépare et lance un audit complet à partir d'un nom de domaine |
| `/seo-content-refresh <url>` | Optimise et republie un contenu existant (analyse, brief, rédaction, push WordPress) |
| `/seo-weak-content example.fr` | Diagnostique les pages/requêtes GSC qui sous-performent, cause racine cas par cas |
| `/seo-audit` | Audit rapide sans APIs payantes, SEO Health Score 0-100 |
| `/seo-page <url>` | Analyse profonde d'une page unique |
| `/seo-technical` | Audit technique 8 catégories |
| `/seo-plan` | Planification stratégique SEO (templates par industrie) |
| `/seo-programmatic` | SEO programmatique (quality gates, thin content, index bloat) |
| `/seo-competitor-pages` | Pages comparaison X vs Y / alternatives |

Chaque `agent-*` embarque ses propres skills, références de seuils (`references/thresholds.md` = source de vérité) et scripts Python : les dossiers sont **self-contained**.

## Installation

Prérequis : **Claude Code** installé + **Python 3.12+**.

### Automatique

```powershell
# Windows (PowerShell)
git clone https://github.com/uplix-live/uplix-seo-agents.git
cd uplix-seo-agents
.\install.ps1          # installe dans ~/.claude/skills (global)
.\install.ps1 -Project # ou dans .claude/skills du dossier courant
```

```bash
# macOS / Linux
git clone https://github.com/uplix-live/uplix-seo-agents.git
cd uplix-seo-agents
./install.sh           # global (~/.claude/skills)
./install.sh --project # ou projet courant
```

Le script copie les skills, installe les dépendances Python (`requirements.txt`) et le navigateur Playwright (Chromium).

### Manuelle

1. Copier le contenu de `skills/` dans `~/.claude/skills/` (global) ou `.claude/skills/` à la racine de votre projet.
2. `pip install -r requirements.txt`
3. `python -m playwright install chromium`
4. Relancer Claude Code, vérifier que `/agent-technique` apparaît dans l'autocomplétion.

## Configuration MCP & clés API

Les agents fonctionnent en mode dégradé sans APIs, mais sont bien plus puissants avec. **Chaque consultant utilise ses propres clés** — aucune clé n'est fournie dans ce dépôt.

1. Copier `.mcp.json.example` → `.mcp.json` à la racine de votre projet et renseigner vos clés.
2. Copier `.env.example` → `.env` pour les scripts Python.

| Besoin | Agent(s) | Serveur MCP |
|---|---|---|
| Google Search Console | redaction (**impératif**), technique, sémantique, monitoring | MCP GSC (OAuth) — demander le build `mcp-gsc-lucky` à Emmanuel, ou tout MCP GSC équivalent |
| Haloscan (FR) | sémantique, refonte, local | `@occirank/haloscan-server` + `HALOSCAN_API_KEY` |
| Ahrefs (multi-pays) | sémantique, refonte, redaction, monitoring | MCP distant `https://api.ahrefs.com/mcp/mcp` + clé |
| Chrome DevTools (Lighthouse) | technique, refonte | `chrome-devtools-mcp` (sans clé) |
| Screaming Frog (gros crawls) | technique, refonte | MCP screaming-frog local |
| WiseWand (génération contenu) | redaction | `@wisewandtools/mcp-server` + clé |

## Garde-fous (communs à tous les agents)

- **Cadrage d'abord** : l'agent pose ses questions avant d'exécuter, puis enchaîne jusqu'aux livrables.
- **Jamais en automatique** (confirmation explicite obligatoire) : push en production, suppression/redirection d'URLs live, modification `robots.txt`/sitemap/`.htaccess`, publication WordPress, envoi externe.
- **Budget API ≤ ~500 appels MCP payants** par audit ; point d'étape à l'approche du plafond.
- **Seuils** : le dossier `references/` de chaque agent fait foi (`thresholds.md` prime en cas de divergence).
- **Croiser minimum 2 sources** pour valider un insight.

Détails complets : [DISTRIBUTION-AGENTS.md](DISTRIBUTION-AGENTS.md).

## Sécurité

- Ne jamais commiter `.env`, `.mcp.json` ou toute clé API dans ce dépôt ou ailleurs.
- Les scripts lisent leurs credentials **uniquement** via variables d'environnement (voir `.env.example`).

## Maintenance

Les agents sont self-contained : une amélioration d'un skill ou d'un seuil commun doit être propagée dans chaque agent concerné, puis re-poussée ici. Source de vérité : le projet `Consultant SEO IA` (Emmanuel).
