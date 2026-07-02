# Agents SEO portables — Distribution & installation

Ce projet fournit des **agents SEO autonomes et portables** pour Claude Code. Chaque agent vit dans son propre répertoire sous `.claude/skills/` et embarque **tout ce dont il a besoin** (skills, références de seuils, scripts Python, page de présentation HTML, README). Un agent peut donc être partagé seul — par exemple via un **lien Dropbox** — à n'importe quel consultant SEO disposant de Claude Code.

## Les agents disponibles

| Agent | Commande | Spécialité |
|---|---|---|
| **Audit technique** | `/agent-technique <domaine>` | Performance/CWV, Schema.org, crawl, indexation, rendu JS, sécurité |
| **Audit sémantique** | `/agent-semantique <domaine>` | Cartographie sémantique, clustering, cannibalisation, content gap concurrents, cocons |
| **Rédaction & contenu** | `/agent-redaction <domaine>` | Mots-clés GSC par URL, URLs entrantes/sortantes du ranking, refresh, E-E-A-T, rédaction |
| **Refonte & migration** | `/agent-refonte <domaine>` | Plan de redirection 301, préservation du trafic, plan de bascule, contrôle post-migration |
| **SEO local** | `/agent-local <domaine>` | NAP, Google Business Profile, pages locales, local pack, Schema LocalBusiness, avis |
| **Monitoring SEO** | `/agent-monitoring <domaine>` | Suivi récurrent : positions, indexation, trafic GSC, CWV, alertes sur dérives (/loop ou schedule) |

> **Catalogue visuel** : `index-agents.html` (racine du projet) — page HTML unique présentant tous les agents et skills SEO, leur rôle et leurs points de vérification, avec liens vers chaque présentation détaillée.

Chaque agent commence par **poser ses questions de cadrage**, puis exécute l'audit et produit les livrables dans `Audits/<domaine>/livrables/`, en respectant les garde-fous (voir plus bas).

## Anatomie d'un répertoire d'agent (autonome)

```
.claude/skills/agent-<nom>/
├── SKILL.md          # Orchestrateur : logique de l'agent + garde-fous (lu par Claude Code)
├── presentation.html # Page de présentation : objectif + tous les contrôles effectués
├── README.md         # Installation, prérequis, usage
├── skills/           # Skills SEO embarqués (lus à la demande par l'orchestrateur)
├── references/       # Seuils de référence — SOURCE DE VÉRITÉ (CWV, schema, thresholds…)
└── scripts/          # Scripts Python utilitaires
```

> Choix d'architecture : **copie self-contained** (chaque agent duplique ses skills/références/scripts) plutôt que des références partagées. Avantage = portabilité totale. Contrepartie = une amélioration d'un skill commun doit être reportée dans chaque agent (voir « Maintenance »).

## Mémoire de mission (par domaine)

À chaque activation (`/agent-<type> <domaine>`), après le cadrage, l'agent :
1. crée/met à jour `Audits/<domaine>/` (`data/` + `livrables/{md,html}`) ;
2. horodate tous les livrables (date du jour) ;
3. écrit/met à jour un **fichier mission par domaine** `Audits/<domaine>/CLAUDE-agent-<type>.md` (réponses de cadrage = mission courante + livrables visés + ligne d'historique ajoutée à chaque run). S'il existe déjà, il le relit d'abord.

> Le `SKILL.md` partagé **n'est jamais modifié** par une exécution : il reste portable. La mission est propre à chaque domaine/client (même logique que les `CLAUDE-audit-<CLIENT>.md` du projet).

## Installation chez un consultant (qui a déjà Claude Code)

1. **Récupérer le dossier** de l'agent voulu (ex: dossier `agent-technique/` reçu par lien Dropbox), ou le dossier `.claude/skills/` complet pour les 6 agents.
2. **Le déposer** dans `.claude/skills/` de son projet (ou de son répertoire personnel `~/.claude/skills/` pour le rendre global à toutes ses sessions).
3. **Relancer Claude Code** (ou recharger les skills). Vérifier avec `/help` ou en tapant `/agent-` que la commande apparaît.
4. **Lancer** : `/agent-technique example.fr`.

### Portée d'installation
- **Par projet** : `.claude/skills/` à la racine du projet → agent disponible dans ce projet uniquement.
- **Global** : `~/.claude/skills/` (dossier personnel) → agent disponible dans toutes les sessions du consultant.

## Prérequis

### Communs
- **Claude Code** installé et configuré.
- **Python 3.12+** pour les scripts embarqués. Installer les dépendances utiles :
  ```bash
  pip install advertools beautifulsoup4 lxml extruct requests playwright pandas
  ```

### MCP & clés API (selon l'agent — facultatif mais recommandé)
Les agents fonctionnent en mode dégradé sans ces accès, mais sont bien plus puissants avec.

| Besoin | Agent(s) | Comment |
|---|---|---|
| **Google Search Console** (`gsc-lucky`) | redaction (impératif), technique, sémantique | MCP OAuth — voir `.mcp.json`. La GSC est **obligatoire** pour `/agent-redaction` (mots-clés par URL, URLs entrantes/sortantes). |
| **Haloscan** (FR) | sémantique, refonte | MCP `@occirank/haloscan-server` + clé API |
| **Ahrefs** (multi-pays) | sémantique, refonte, redaction | Remote MCP + clé |
| **Chrome DevTools** (Lighthouse) | technique, refonte | MCP `chrome-devtools` |
| **Screaming Frog** (gros crawls) | technique, refonte | MCP `screaming-frog` |
| **WiseWand** (génération contenu) | redaction | MCP `@wisewandtools/mcp-server` |
| **Haloscan GMB** (backlinks Google Business) | local | MCP Haloscan (`get_domains_gmb_backlinks`…) |
| **Rank tracker / IsIndexed / seo-toolkit C1-C2** | monitoring | Ahrefs `rank-tracker-overview`, Haloscan visibility-trends, IsIndexed (B12), dashboard/alertes seo-toolkit |

Configuration des MCP : fichier `.mcp.json` à la racine du projet. Un consultant qui reçoit un agent doit déclarer dans son propre `.mcp.json` les serveurs MCP nécessaires avec ses propres clés API. **Ne jamais transmettre de clés API dans le dossier partagé** (les clés vivent dans `.env` / `.mcp.json`, hors du package agent).

## Garde-fous (communs à tous les agents)

- **Cadrage d'abord** : l'agent pose ses questions avant d'exécuter.
- **Exécution maximale** : une fois cadré, il enchaîne jusqu'aux livrables sans redemander, SAUF actions sensibles.
- **Jamais en automatique** (confirmation explicite obligatoire) : push en production, suppression/redirection d'URLs live, modification de `robots.txt`/sitemap/`.htaccess`, publication WordPress, envoi externe.
- **Profondeur d'exécution ≤ 3 niveaux**, puis liste des « pistes non exécutées ».
- **Budget API ≤ ~500 appels MCP payants** par audit.
- **Seuils** : le dossier `references/` de chaque agent fait foi (`thresholds.md` prime en cas de divergence).

## Maintenance

Comme chaque agent est self-contained, une mise à jour d'un skill ou d'un seuil commun doit être **propagée dans chaque agent concerné**. Pour redistribuer une version à jour, re-partager le(s) dossier(s) d'agent. La source des skills/références de référence reste `claude-seo/skills/` et `claude-seo/seo/references/` à la racine du projet.

## Sécurité du partage

- Ne jamais inclure `.env`, clés API, credentials clients dans un dossier partagé.
- Les pages `presentation.html` et `README.md` sont sans données sensibles : utilisables comme support commercial / onboarding.
