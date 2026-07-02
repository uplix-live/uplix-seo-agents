# Agent SEO Monitoring — `/agent-monitoring`

Agent SEO de **suivi récurrent** packagé et portable, prêt à être partagé à n'importe quel consultant disposant de Claude Code.

## Objectif

Surveiller dans le temps la santé SEO d'un domaine par **snapshots comparés période sur période** : positions, indice de visibilité, indexation, trafic/requêtes (GSC), Core Web Vitals — et remonter les **dérives** sous forme d'alertes priorisées par gravité, chacune avec sa cause probable et son action corrective. L'agent pose d'abord une **baseline (T0)**, puis ne signale que ce qui bouge à chaque passage. Voir `presentation.html` pour la liste complète des contrôles.

## Usage

```
/agent-monitoring example.fr
```

L'agent pose ses questions de cadrage (KW/pages prioritaires, concurrents, fréquence, seuils d'alerte, périmètre indexation, accès GSC), génère le snapshot de référence, compare au passage précédent, priorise les alertes par gravité, puis produit les livrables dans `Audits/<domaine>/livrables/`.

## Contenu du répertoire (autonome)

| Dossier / fichier | Rôle |
|---|---|
| `SKILL.md` | Orchestrateur de l'agent (baseline → comparaison → alertes + garde-fous) |
| `presentation.html` | Page de présentation : objectif + tous les contrôles |
| `README.md` | Ce fichier |
| `skills/` | Skills SEO de support embarqués (seo-technical, seo-sitemap) |
| `references/` | Seuils de référence — **source de vérité** (thresholds, cwv-thresholds) |
| `scripts/` | Scripts Python (gsc_query, parse_gsc_results, fetch_page, advertools_utils) |
| `data/monitoring/` | Snapshots datés (générés dans `Audits/<domaine>/data/monitoring/`) |

## Prérequis

- **Claude Code** installé.
- **Python 3.12+** + **seo-toolkit** pour l'indexation (module B12) et le reporting (C1 dashboard / C2 alerts) : `python -m seo_toolkit isindexed …`. Clé `ISINDEXED_API_KEY` dans `.env`.
- **MCP recommandés** :
  - `gsc-lucky` (Google Search Console) — **fortement recommandé** : trafic/requêtes, comparaison 2 périodes (`gsc_compare_performance`), inspection d'indexation (`gsc_inspect_url`).
  - `ahrefs` (rank-tracker) — positions suivies et comparaison concurrents (`rank-tracker-overview`, `rank-tracker-competitors-overview`).
  - `haloscan` (marché FR) — visibilité et historique de positions (`get_domains_visibility_trends`, `get_domains_positions`, `get_domains_history_positions`).
- Le suivi reste utile même partiellement : avec GSC seul on suit trafic + indexation ; ajouter Haloscan/Ahrefs enrichit positions et visibilité.

## Installation chez un autre consultant

1. Copier le dossier `agent-monitoring/` dans son `.claude/skills/`.
2. Renseigner les clés nécessaires (`ISINDEXED_API_KEY`) dans `.env` et configurer les MCP (`gsc-lucky`, `ahrefs`, `haloscan`).
3. Redémarrer Claude Code (ou recharger les skills).
4. Taper `/agent-monitoring <domaine>`.

## Programmer le suivi récurrent

Le monitoring est récurrent par nature. Une fois la baseline posée :

- **À intervalle régulier (local)** : `/loop <intervalle> /agent-monitoring <domaine>` — ex. `/loop 7d /agent-monitoring example.fr` pour un passage hebdomadaire. À chaque tour l'agent recharge le dernier snapshot, en crée un nouveau et ne remonte que les dérives.
- **Agent programmé (cloud / cron)** : utiliser le skill `schedule` pour créer une routine qui exécute `/agent-monitoring <domaine>` (ex. tous les lundis) et dépose le rapport de période dans les livrables.
- **Reporting continu** : brancher le **dashboard C1** et les **alertes C2** du seo-toolkit.

> Les **actions correctives live** (modification d'un site client, push, redirection, désindexation, envoi d'email) restent **toujours soumises à confirmation explicite** et sont déléguées à l'agent compétent.

> Voir la doc de distribution globale du projet : `../../DISTRIBUTION-AGENTS.md`.

## Périmètre

Strictement le suivi récurrent et les alertes. Pour un audit technique approfondi → `/agent-technique`, la stratégie sémantique et le content gap → `/agent-semantique`, le contenu / content refresh → `/agent-redaction`, une refonte ou migration → `/agent-refonte`.
