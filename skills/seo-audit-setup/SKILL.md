---
name: seo-audit-setup
description: "Prepare et lance un audit SEO complet a partir d'un simple nom de domaine. Cree le dossier, detecte le site, remplit le template, lance l'audit. Usage: /seo-audit-setup example.fr"
user-invokable: true
args:
  - name: domain
    description: "Le nom de domaine a auditer (ex: example.fr)"
    required: true
---

# Audit SEO — Setup automatique

Tu recois un nom de domaine. Tu dois preparer **tout le necessaire** puis lancer l'audit complet sans intervention humaine.

## Etape 1 — Creer la structure

```
Audits/<domaine>/
├── context/          # Context Bootstrapper (cf. Etape 2bis) — contexte business reutilisable
├── data/
├── livrables/
│   ├── html/
│   └── md/
```

## Etape 2 — Detecter les infos du site (en parallele)

Lancer ces actions simultanement :

### 2a. Crawl de la homepage
- Fetcher `https://www.<domaine>` (et `https://<domaine>` en fallback)
- Extraire : title, meta description, H1, couleurs CSS dominantes, fonts Google Fonts chargees, favicon
- Detecter le secteur d'activite a partir du contenu

### 2b. Donnees Haloscan
- `get_domains_overview` pour le domaine → positions, trafic estime, top KW, top pages, categories
- `get_domains_competitors` → 5 concurrents principaux

### 2c. Donnees Ahrefs
- `domain_rating` → DR du domaine
- `backlinks_stats` → nombre de backlinks, referring domains
- `competitors_overview` → concurrents organiques

### 2d. Detecter les univers produits/services
- A partir du crawl homepage + sitemap + top pages Haloscan, identifier les 3-5 univers principaux

## Etape 2bis — Context Bootstrapper (contexte business + apprentissage de la charte)

> **But** : creer un dossier `Audits/<domaine>/context/` qui contient le **contexte business reutilisable** par tous les agents, et **apprendre la charte editoriale** du client en lisant ses contenus reels. Ces fichiers evitent de re-poser les memes questions a chaque agent et empechent les contenus generiques.

### A. Initialiser / merger le dossier context/

1. Si `Audits/<domaine>/context/` **n'existe pas** : le creer en copiant **tous** les fichiers de `context-templates/` (racine du projet) dedans (`identity.md`, `audience.md`, `voice.md`, `products.md`, `competitors.md`, `author.md`, `experience-notes.md`, `brand-guidelines.md`).
2. Si le dossier **existe deja** (re-run) : **ne PAS ecraser**. Lire l'existant et faire un **merge intelligent** — ne remplir que les champs encore en `TK:` ou vides, conserver tout ce que l'utilisateur a deja rempli. Signaler ce qui a ete complete vs conserve.

### B. Apprendre la charte editoriale (auto-detection)

Recolter de la matiere reelle pour pre-remplir `voice.md` et `identity.md` :

```bash
python scripts/fetch_page.py https://www.<domaine>/            # homepage
python scripts/parse_html.py home.html --url https://www.<domaine>/
```

- Choisir **2-3 pages/articles representatifs** (depuis le sitemap, le blog, ou les top pages Haloscan de l'Etape 2b) et les fetcher + parser de la meme facon.
- A partir des textes extraits, **pre-remplir** :
  - `voice.md` (section « Mesures apprises ») : tutoiement/vouvoiement, longueur de phrase moyenne, niveau de jargon, personne (je/nous/on), registre, presence de first-person, exemples reels (2-3 extraits avec URL source) + lister les URLs analysees.
  - `identity.md` : secteur, modele, **proposition de valeur detectee** (en respectant la regle anti-generalite — reformuler en « pour QUI / quel PROBLEME / quel MECANISME / quelle PREUVE »), univers produits.
  - `products.md` : money pages candidates detectees depuis homepage + sitemap + top pages (marquer les URLs `TK: a verifier` tant que le statut 200 n'est pas confirme).
  - `competitors.md` : pre-remplir avec les concurrents de l'Etape 2b/2c (Haloscan + Ahrefs croises).
  - `author.md` : si une page « a propos »/auteur est detectee, pre-remplir nom/titre/profils `sameAs` **uniquement si reellement presents** (jamais inventer).
- Si le contenu est insuffisant pour apprendre la voix : marquer `TK: contenu insuffisant` et le demander en C.

### C. Interroger l'utilisateur (uniquement le non-detectable)

Poser des questions **ciblees** seulement sur ce que le crawl ne peut pas determiner. Regrouper en un seul bloc de questions :

1. **Audience fine** : persona principal precis (role + contexte + declencheur), pas « les professionnels ».
2. **Money pages exactes** : confirmer/corriger la liste de `products.md` et le type de conversion de chacune.
3. **Auteur & credentials** : nom, titre, diplomes/certifications reels, profils (LinkedIn...). Alimente le schema Person + E-E-A-T.
4. **Anecdotes d'experience** : 1-2 retours first-person concrets (situation, action, resultat chiffre) pour `experience-notes.md`.
5. **Mots bannis / interdits** : termes a ne jamais employer, claims reglementes (sante/finance), concurrents a ne jamais citer.

Regles d'interrogation :
- **Pousser a la precision** : si une reponse est vague (« on aide les entreprises », « nos clients sont satisfaits »), **redemander** un exemple concret avant de l'ecrire.
- **Ne JAMAIS fabriquer** : aucune reponse inventee. Si l'utilisateur ne sait pas / ne fournit rien → ecrire `TK: a completer` ou `Aucun a ce jour`. Pour `experience-notes.md` et `author.md` (credentials), l'anti-fabrication est **absolue** (faux credential = risque E-E-A-T + juridique).
- L'utilisateur peut repondre « passe » : laisser le `TK:` et continuer.

### D. Sauvegarder au fil de l'eau

Ecrire chaque fichier `context/*.md` des qu'il est complete (ne pas attendre la fin). En re-run, appliquer le merge de A.2.

### E. Reutilisation (a rappeler dans le resume final)

Ces fichiers `context/` sont **lus par les autres agents**, pas seulement par le setup :
- `/agent-redaction` → `voice.md` (calibrage ton), `author.md` (byline + schema Person + E-E-A-T), `experience-notes.md` (Information Gain + Experience), `products.md` (money pages pour Money-Page Match du **BVS**), `brand-guidelines.md` (filtre conformite).
- `/agent-semantique` → `competitors.md` (content gap + exclusions), `products.md` (Money-Page Match du BVS), `identity.md`/`audience.md` (univers & intentions).
- `/seo-content-refresh` → `voice.md`, `brand-guidelines.md`, `author.md` (coherence avant push WP).

### F. Garde-fou securite

Le dossier `context/` peut contenir des **infos sensibles** (e-mails auteurs, URLs internes, notes client). **Recommander a l'utilisateur d'ajouter `Audits/*/context/` au `.gitignore`** et **ne jamais inclure ces fichiers dans un package d'agent partage**.

## Etape 3 — Remplir le template

Lire `TEMPLATE-AUDIT-PROMPT.md` et remplacer tous les `{{placeholders}}` :

| Placeholder | Source |
|---|---|
| `{{domaine}}` | Argument fourni |
| `{{nom_client}}` | Extraire du title/meta ou du whois, ou mettre le domaine en fallback |
| `{{secteur}}` | Detecte depuis le contenu (etape 2a) |
| `{{concurrent1-5}}` | Haloscan `get_domains_competitors` (etape 2b) |
| `{{univers1-3}}` | Detecte depuis top pages et categories (etape 2d) |
| `{{couleur_primaire}}` | Extraite du CSS de la homepage (etape 2a) |
| `{{couleur_secondaire}}` | Extraite du CSS de la homepage (etape 2a) |
| `{{font}}` | Google Font detectee (etape 2a), ou 'Inter' par defaut |
| `{{date}}` | Date du jour |

Sauvegarder le resultat dans `Audits/<domaine>/CLAUDE-audit-<CLIENT>.md`

## Etape 4 — Afficher le resume et demander confirmation

Avant de lancer l'audit, afficher un resume compact :

```
Audit SEO de <domaine>
━━━━━━━━━━━━━━━━━━━━━
Secteur    : <detecte>
DR         : <score>/100
Positions  : <nb> KW dans le top 100
Concurrents: <c1>, <c2>, <c3>, <c4>, <c5>
Univers    : <u1> | <u2> | <u3>
Couleurs   : <hex1> / <hex2>
Font       : <font>
Voix apprise: <tutoiement/vouvoiement>, phrases ~<N> mots, jargon <niveau>
Context    : <X>/8 fichiers context/ pre-remplis (reste <Y> TK a completer)

Fichiers crees :
  Audits/<domaine>/CLAUDE-audit-<CLIENT>.md
  Audits/<domaine>/context/ (8 fichiers, reutilises par /agent-redaction, /agent-semantique, /seo-content-refresh)
```

Rappeler : **ajouter `Audits/*/context/` au `.gitignore` (donnees sensibles)**.

Demander : **"Je lance l'audit complet ? (oui/non)"**

## Etape 5 — Lancer l'audit

Si confirmation, lire le `CLAUDE-audit-<CLIENT>.md` genere et executer les instructions de demarrage (section "Demarrage" du template) :

1. Lister le contenu de `Audits/<domaine>/`
2. Collecte MCP en parallele (Haloscan + Ahrefs + GSC)
3. Crawl complet du site
4. Enchainer toutes les phases sans interruption

## Regles

- **Context Bootstrapper (Etape 2bis)** : ne jamais ecraser un `context/` existant (merge) ; ne jamais fabriquer (`TK:` / `Aucun a ce jour`) ; pousser a la precision (refuser le vague) ; sauvegarder au fil de l'eau.
- **Zero question inutile** : si une info manque, la detecter ou mettre un defaut raisonnable
- **Couleurs** : si non detectables, utiliser `--accent: oklch(55% .18 250)` et `--danger: oklch(55% .2 25)` (defaut CLAUDE.md)
- **Font** : si non detectable, utiliser `Inter`
- **Concurrents** : minimum 3, maximum 5. Croiser Haloscan et Ahrefs.
- **Timeout** : si le fetch homepage echoue, continuer avec les donnees MCP seules
