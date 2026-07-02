# Agent SEO Rédaction & Contenu — `/agent-redaction`

Agent SEO **rédaction / contenu** packagé et portable, prêt à être partagé à n'importe quel consultant disposant de Claude Code. **Piloté par la Google Search Console.**

## Objectif

Deux missions complémentaires, toujours data-driven via la GSC :
1. **Créer du nouveau contenu** (plan éditorial, briefs, rédaction calibrée).
2. **Identifier les contenus à mettre à jour** (content refresh) : pages en déclin, thin content, contenu obsolète, E-E-A-T faible, citabilité GEO faible.

Le contrôle distinctif : pour **chaque URL**, récupérer en GSC tous les mots-clés sur lesquels elle rank déjà, puis détecter sur deux périodes les **URLs/requêtes qui entrent** dans le ranking et celles qui en **sortent** (décrochage). Voir `presentation.html` pour la liste complète des contrôles.

## Usage

```
/agent-redaction example.fr
```

L'agent pose ses questions de cadrage, **vérifie la connexion GSC** (bloquant), analyse chaque URL via la Search Console, détecte les contenus à rafraîchir et les entrées/sorties du ranking, rédige les briefs et contenus calibrés, puis produit les livrables dans `Audits/<domaine>/livrables/`.

## Contenu du répertoire (autonome)

| Dossier / fichier | Rôle |
|---|---|
| `SKILL.md` | Orchestrateur de l'agent (logique GSC + garde-fous) |
| `presentation.html` | Page de présentation : objectif + tous les contrôles |
| `README.md` | Ce fichier |
| `skills/` | Skills SEO contenu embarqués (seo-content, seo-page, seo-geo, seo-competitor-pages, maillage-systeme, seo-content-refresh) |
| `references/` | Seuils de référence — **source de vérité** (eeat-framework, quality-gates, thresholds, **bvs** = Business Value Score) |
| `scripts/` | Scripts Python (fetch_page, parse_html, gsc_query, seoquantum_client, citability_scorer) |

## Prérequis

### Google Search Console — IMPÉRATIVE (bloquant)

L'agent ne peut pas analyser une URL sans GSC. Connexion :

1. **MCP `gsc-lucky` (principal, live par page)** — vérifier qu'il figure dans `.mcp.json` et qu'il est autorisé. Au premier appel, lancer l'OAuth Google si demandé. Tester avec `mcp__gsc-lucky__gsc_list_sites` : le domaine doit apparaître dans la liste des propriétés.
2. **Accès à la propriété** — le compte Google connecté doit avoir accès à la propriété (domaine `sc-domain:` ou préfixe d'URL) dans [search.google.com/search-console](https://search.google.com/search-console). Sinon, demander au client de partager l'accès.
3. **Outils GSC d'Ahrefs (complément, historique long)** — via le MCP Ahrefs : `gsc-keywords`, `gsc-keyword-history`, `gsc-page-history`, `gsc-pages-history`.
4. **Fallback dégradé** (seulement si accepté explicitement) — `scripts/gsc_query.py` avec credentials de service, ou Ahrefs GSC seul. À signaler comme limite dans les livrables.

### Autres prérequis

- **Claude Code** installé.
- **Python 3.12+** pour les scripts (`pip install requests beautifulsoup4 lxml`).
- **MCP recommandés** :
  - `gsc-lucky` — **obligatoire** (mots-clés par URL, comparaison de périodes, indexation).
  - `ahrefs` — historique GSC long terme (entrées/sorties du ranking).
  - `wisewand` (`@wisewandtools/mcp-server`) — **proposé** pour la génération / l'aide à la rédaction de contenu SEO (`create_article`). Optionnel : sans lui, rédaction manuelle calibrée.
  - `haloscan` — volumes FR, questions PAA, KW similaires (marché français).
- **SEOQuantum** (clé pour `scripts/seoquantum_client.py`) — calibration sémantique de la rédaction.

## Installation chez un autre consultant

1. Copier le dossier `agent-redaction/` dans son `.claude/skills/`.
2. Configurer et autoriser le MCP `gsc-lucky`, puis connecter la Search Console (voir ci-dessus).
3. Redémarrer Claude Code (ou recharger les skills).
4. Taper `/agent-redaction <domaine>`.

> Voir la doc de distribution globale du projet : `../../DISTRIBUTION-AGENTS.md`.

## Périmètre

Strictement rédaction / contenu : création de contenu, content refresh, E-E-A-T, citabilité GEO, maillage interne dans le corps du texte.

Pour les autres besoins, renvoyer vers l'agent dédié :
- Audit technique (CWV, crawl, indexation, sécurité, Schema, robots/sitemap) → `/agent-technique`
- Stratégie sémantique globale (cartographie, clustering par univers, content-gap macro, cocons, territoires à conquérir) → `/agent-semantique`
- Refonte / migration sans perte de trafic (redirections 301, link equity) → `/agent-refonte`

> **Publication.** L'agent ne publie ni ne pousse jamais sur WordPress automatiquement : toute mise en ligne (live OU draft) exige une confirmation explicite ET le passage de la gate qualité 14/14 de `seo-content-refresh` (`markers_check.py`).
