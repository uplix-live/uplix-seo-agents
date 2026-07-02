---
name: seo-content-refresh
description: "Optimise et republie un contenu SEO existant à partir d'une simple URL : fetch, analyse SEOQuantum + Haloscan + GSC, brief, rédaction calibrée (3000+ mots, FAQ, comparatifs, JSON-LD), push WordPress REST API, vérification. Usage: /seo-content-refresh https://www.uplix.fr/ahrefs/"
user-invokable: true
args:
  - name: url
    description: "URL exacte de la page à optimiser (slug doit exister en WP)"
    required: true
  - name: mode
    description: "draft | live (défaut: live). 'draft' crée une révision en draft sans toucher au live."
    required: false
---

# SEO Content Refresh — méthodologie complète

À partir d'une simple URL, tu exécutes la chaîne complète d'optimisation : audit, rédaction calibrée, publication via API WordPress, vérification. Aucune question intermédiaire sauf si bloqué.

## Prérequis

- Site WordPress avec API REST activée (`/wp-json/wp/v2/`)
- Credentials WP en mémoire (voir `[[reference_uplix_wp_api]]` pour uplix.fr, ou demander pour autre site)
- SEOQuantum API key disponible (`scripts/seoquantum_client.py` — clé en fallback)
- Haloscan MCP configuré (volumes FR)
- GSC MCP configuré (`gsc-lucky`) avec accès au site
- Crédits disponibles : 5 tokens SEOQuantum minimum

## Étape 1 — Identifier le post WP

À partir de l'URL fournie :
1. Extraire le slug depuis l'URL (dernier segment avant `/`)
2. Tester d'abord `posts`, puis `pages` :
   ```
   GET https://www.<domain>/wp-json/wp/v2/posts?slug=<slug>
   GET https://www.<domain>/wp-json/wp/v2/pages?slug=<slug>
   ```
3. Récupérer l'**id**, le **type** (post ou page), le **title actuel**, la date de modification
4. Si pas trouvé : avorter avec message clair "Slug introuvable en WP"

Définir le **mot-clé principal** : par défaut, le slug nettoyé (`/ahrefs/` → "ahrefs"). Si le slug est composé (`/agence-seo-paris/`), demander une confirmation rapide ou prendre le premier terme significatif.

## Étape 2 — Créer le dossier de livrable

```
Audits/<domaine>/livrables/<YYYY-MM-DD>-optimisation-<slug>/
├── 00-brief-seoquantum.md
├── 01-nouveau-contenu.md
├── 02-page-optimisee.html  (standalone, pour preview locale)
├── push_content.py         (copie depuis assets/)
├── markers_check.py        (copie depuis assets/ — gate qualité pré-push)
├── backup_post_<id>_before.json
├── backup_post_<id>_pre_push.json
├── after_post_<id>.json
└── seoquantum_advisor.json
```

## Étape 3 — Collecte data (en parallèle)

Lancer **simultanément** :

### 3a. Fetch + parse de la page actuelle
- `python scripts/fetch_page.py <url>` ou `requests.get` avec UA neutre
- Parser : title, meta description, H1-H6, word count, schemas existants, liens internes/externes
- Sauvegarder le HTML brut dans `data/<slug>_raw.html`

### 3b. GSC — 16 mois sur cette URL
```python
mcp__gsc-lucky__gsc_search_analytics(
    site_url="sc-domain:<domain>" ou "https://www.<domain>/",
    start_date="<date_jour - 16 mois>",
    end_date="<date_jour - 1>",
    dimensions="query",
    dimension_filter=f"page equals {url}",
    row_limit=500
)
```
Extraire : top 20 KW par impressions, clics totaux, position moyenne, KW à 0 clic avec >100 impressions (opportunités).

### 3c. SEOQuantum analyze + advisor
```bash
python scripts/seoquantum_client.py audit-page <url> "<keyword_principal>"
```
Cela lance :
- Analyse sémantique (5 tokens) — récupère top_terms, questions PAA, concurrents SERP, mean_length, plan
- Advisor (0 tokens) — calcule advisor_score, google_score, common_terms_score, diff[]

Sauvegarder dans `seoquantum_advisor.json` et `data/seoquantum_cache/kw_<keyword>.json`.

### 3d. Haloscan keyword data
- `mcp__haloscan__get_keywords_overview(keyword, requested_data=["volume","cpc","competition","similar_serp","related_search"])`
- `mcp__haloscan__get_keywords_questions(keyword, lineCount=30)` — questions PAA FR

## Étape 4 — Construire le brief (`00-brief-seoquantum.md`)

Document structuré avec :

| Section | Contenu |
|---|---|
| **URL cible** | URL fournie |
| **KW principal** | + volume Haloscan |
| **Diagnostic SEOQuantum** | advisor_score actuel vs moy/max concurrents, google_score, content_len actuel vs mean concurrents, Flesch |
| **Position GSC** | top 5 KW + position moyenne + clics 16 mois |
| **Top 6 concurrents SERP** | URL, mots, score, title |
| **KW sous-représentés** | tableau `terme | actuel | idéal | Δ` — du diff SEOQuantum, delta>0 (top 20) |
| **KW à réduire** | termes avec delta<0 (à diminuer) |
| **Questions PAA** | depuis SEOQuantum + Haloscan, sélectionner 8-10 questions pour FAQ |
| **KW secondaires** | volumes Haloscan : variations, longue traîne (top 10) |
| **Plan H2/H3** | structure de la nouvelle page (8-10 H2) |
| **JSON-LD** | types à ajouter selon le contenu (Article + autre selon type : SoftwareApplication, Service, Product, Organization…) |
| **Maillage** | 5 liens sortants + 5 liens entrants souhaités (méthode Boussardon) |
| **Quick wins** | tableau action / où / impact estimé |
| **Métriques de succès** | objectifs 30/60/90 jours sur GSC |

## Étape 5 — Rédiger le nouveau contenu (`01-nouveau-contenu.md`)

### Règles de calibration

| Critère | Cible |
|---|---|
| **Word count** | ≥ `mean_length` concurrents SEOQuantum, **minimum 2 700 mots**, idéal 3 000-3 500 |
| **Structure** | 1 H1 + 6-10 H2 + H3 sous chaque H2 (>3) |
| **TL;DR** | encadré au début (3-4 phrases) pour featured snippet + AI Overviews |
| **FAQ** | 8-10 questions PAA en `<details><summary>` accordéon |
| **Tableaux comparatifs** | 1-2 tableaux denses (tarifs, vs concurrents, vs alternatives) |
| **Image featured** | 1 cover image (générée par WiseWand, ratio 16:9, palette site) |
| **Images inline** | **3 images inline minimum** réparties dans le corps (ratio 16:9 ou 4:3, palette site) |
| **Fréquences cibles SEOQuantum** | atteindre ou dépasser ≥80 % des `ideal` du diff (vérifier en local après rédaction) |
| **Mots à réduire** | termes du diff avec delta<0 → max 30 % de leur fréquence actuelle |
| **Date visible** | "Mis à jour le DD mois YYYY" sous H1 et dans le footer |
| **Auteur visible** | "Par l'équipe <NomAgence>" ou auteur expert |
| **Lien sortant vers source officielle** | au moins 1 (ex: ahrefs.com pour un article Ahrefs) |
| **5 liens internes** | méthode Boussardon, ancres différentes (voir [[feedback_maillage_methode]]) |
| **CTA agence** | bloc callout en fin d'article vers la page pilier business |

### Configuration WiseWand `create_article` (paramètres clés)

**Toujours activer pour un refresh SEO complet :**

```python
mcp__wisewand__create_article(
    subject="<description détaillée du contenu cible>",
    target_keyword="<KW principal>",
    keywords_secondary="<KW1>, <KW2>, ...",
    title="<title final 50-60 char>",
    keep_title=True,                  # WiseWand garde notre title
    lang="fr",
    country="fr",
    length=3000,                      # 2700-3500 idéal
    type="blog",
    apply_project_brief_config=False,

    # Structure et SEO
    use_summary=True,                 # TL;DR encadré
    use_toc=True,                     # Table des matières
    use_faq=True,
    faq_questions="Q1\nQ2\nQ3\n...",  # 8-10 questions PAA
    use_infotable=True,               # Tableaux comparatifs
    use_bulletlist=True,
    use_blockquotes=True,
    use_boldkeywords=True,
    use_enhancedformatting=True,
    use_externalsources=True,         # Sources autoritaires
    use_internallinks=True,
    use_list_internal_links=True,
    internal_links_list="url1, url2, url3, url4, url5",

    # IMAGES (3 inline + 1 cover obligatoires)
    use_image=True,                   # Featured image (cover)
    image_ratio="16:9",
    image_use_palette=True,
    image_primary_color="#XXXXXX",    # Couleur primaire de la charte du site
    image_secondary_color="#XXXXXX",  # Couleur secondaire

    use_inlineimages=True,            # 3 images dans le corps
    inlineimages_count=3,             # Réparties automatiquement entre les H2
    inline_images_ratio="16:9",
    inline_images_use_palette=True,
    inline_images_primary_color="#XXXXXX",
    inline_images_secondary_color="#XXXXXX",

    # Brief de ciblage sémantique
    additional_information="<termes SEOQuantum à renforcer / à réduire, ton, freshness 2026, auteur>",
    avoid_information="Ne pas mentionner FID (obsolète depuis mars 2024, remplacé par INP). Pas de schema HowTo ni FAQPage (déprécié/restreint).",
    search_intention_answer="<résumé de l'intent de recherche en 1 phrase>",
)
```

### Palette par site (mémoire)

Charger la palette du site cible depuis `[[template-design-system]]` ou la mémoire du domaine. Exemples :
- **topcafetiere.fr** : primary `#6b3410` (brun torréfié) / secondary `#c89572` (crème)
- **uplix.fr** : primary `#000000` / secondary `#c084fc` (violet)
- **maaf.fr** : primary `#003DA5` / secondary `#FFFFFF`

Si la palette n'existe pas en mémoire pour le domaine, **demander à l'utilisateur** une fois et la sauvegarder dans `[[template-design-system-<domain>]]`.

### Référentiel complet des options WiseWand : priorisation

#### Combo gagnant minimum (12 options à activer SYSTÉMATIQUEMENT)

```python
use_summary=True                          # TL;DR encadré (featured snippet + AI Overviews)
use_toc=True                              # Table des matières (sitelinks SERP)
use_faq=True                              # FAQ accordéon (PAA, longue traîne)
faq_questions="Q1\nQ2\nQ3\n..."           # 8-10 questions PAA du brief
use_infotable=True                        # Tableaux comparatifs (AI citation readiness)
use_bulletlist=True                       # Listes 3-7 items (Google adore)
use_boldkeywords=True                     # KW en gras (signal sémantique)
use_externalsources=True                  # Sources autoritaires (E-E-A-T)
use_internallinks=True                    # Maillage interne
internal_links_list="url1,url2,url3,url4,url5"  # 5 URLs Boussardon
use_image=True                            # Featured image (OpenGraph + Article schema)
image_ratio="16:9"                        # Standard responsive
image_use_palette=True                    # Palette site
image_primary_color="#XXXXXX"             # De la mémoire site
image_secondary_color="#XXXXXX"
use_inlineimages=True                     # 3 images dans le corps
inlineimages_count=3                      # Minimum
inline_images_ratio="16:9"
inline_images_use_palette=True
inline_images_primary_color="#XXXXXX"
inline_images_secondary_color="#XXXXXX"
keep_title=True                           # CRITIQUE : sans ça WiseWand prend le subject complet comme H1
length=3000                               # Pas "auto" (donne 1500-2000)
avoid_information="Ne pas mentionner FID (obsolète depuis mars 2024, remplacé par INP). Pas de schema HowTo ni FAQPage (déprécié/restreint)."
```

#### Options RECOMMANDÉES selon contexte

| Option | Type | Quand l'activer |
|---|---|---|
| `use_blockquotes=True` | bool | Guides experts / comparatifs (citations marquantes pour AI Overviews) |
| `use_enhancedformatting=True` | bool | Sites premium uniquement (callouts/widgets stylés). À éviter sur sites sobres. |
| `additional_information` | string | **Très puissant** pour piloter les fréquences SEOQuantum (delta>0 à booster, delta<0 à réduire), spécifier auteur, date, freshness 2026 |
| `search_intention_answer` | string | Aide WiseWand à viser l'intent juste sur KW ambigus |
| `image_prompt` | string | Override du prompt visuel si la palette ne suffit pas (logo, produit spécifique...) |

#### Options OPTIONNELLES (cas spécifiques)

| Option | Type | Cas d'usage |
|---|---|---|
| `use_cta=True` + `ctas` | bool + array | Pages business/conversion (pas guides éditoriaux) |
| `use_widget=True` | bool | Calculatrices/quizz interactifs |
| `use_social=True` + `social_networks` | bool + array | Workflow distribution réseaux sociaux automatisé |
| `use_audio=True` + `audio_voice_id` | bool + string | Accessibilité (RGAA) + podcasts |
| `information_search_only_from_subject_sources=True` | bool | Si sources précises fournies dans le `subject` (article de niche) |
| `persona_id` | uuid | Si plusieurs voix éditoriales sur le même site |
| `use_app_internal_links=True` | bool | Maillage automatique géré par WiseWand (si pas de liste custom) |
| `use_indexed_pages_internal_links=True` | bool | Maillage basé sur pages indexées GSC (si connecté) |
| `use_wp_internal_links=True` + `internal_links_wp_connection` | bool + uuid | Maillage automatique depuis pages WP (nécessite connexion WP configurée dans WiseWand) |
| `type="affiliation-product-review"` | enum | Reviews de produits avec affiliation |
| `type="affiliation-compare-products"` | enum | Comparatifs 2 produits avec affiliation (`affiliation_product_1_name`, `affiliation_product_2_name`...) |
| `type="affiliation-top-product"` | enum | Top X produits avec `affiliation_top_products` |

#### Options à ÉVITER par défaut

| Option | Raison |
|---|---|
| `use_publishwordpress=True` sans contrôle qualité | Risque de pousser du contenu non vérifié en live. Toujours préférer un push manuel après nettoyage (H1, dédup "Mis à jour", JSON-LD custom). |
| `type="affiliation-*"` sur du refresh éditorial | Force une structure produit qui dénature un guide info |
| `length="auto"` | WiseWand choisit souvent court (1500-2000 mots). Forcer **3000** explicitement. |
| `publishwordpress_author` | Si le user WP n'a pas `edit_others_posts` → erreur `rest_cannot_edit_others`. Laisser par défaut. |
| Tous les `publish<plateforme>_*` (Shopify, WooCommerce, PrestaShop) | Sauf workflow e-commerce explicite. Trop de dépendances. |
| `use_webhook=True` | Sauf intégration webhook custom prête |

#### Récapitulatif des paramètres image (obligatoires en refresh)

| Paramètre | Valeur recommandée | Note |
|---|---|---|
| `use_image` | `True` | Featured image (cover OpenGraph) |
| `image_ratio` | `"16:9"` | Standard responsive (4:3 si magazine, 1:1 si réseaux sociaux) |
| `image_primary_color` | hex | De la mémoire `[[template-design-system-<domain>]]` |
| `image_secondary_color` | hex | Idem |
| `image_use_palette` | `True` | Force la cohérence visuelle |
| `image_prompt` | (optionnel) | Override si visuel spécifique requis |
| `use_inlineimages` | `True` | 3 images dans le corps |
| `inlineimages_count` | `3` | Minimum 3, max 5 |
| `inline_images_ratio` | `"16:9"` | Cohérent avec la cover |
| `inline_images_primary_color` | hex | Même palette que la cover |
| `inline_images_secondary_color` | hex | Idem |
| `inline_images_use_palette` | `True` | Force la palette |

#### Métadonnées générales

| Paramètre | Valeur recommandée |
|---|---|
| `lang` | `"fr"` pour les sites français |
| `country` | `"fr"` pour le marché français (impact ton et références) |
| `type` | `"blog"` par défaut (sauf affiliation explicite) |
| `apply_project_brief_config` | `False` (sauf si brief WiseWand préexistant validé) |
| `writing_style_mode` | `"auto"` (sauf usage `persona`) |

### Placement des images dans le HTML final

WiseWand insère automatiquement les 3 images entre les H2, généralement aux positions 1/3, 2/3, et fin. **Vérifier après réception** que :
- Les 3 `<img>` sont bien dans le corps (pas seulement la cover qui est dans `cover_image`)
- Chaque `<img>` a un `alt` descriptif (sinon l'enrichir manuellement avant push)
- Chaque `<img>` a `loading="lazy"` (l'ajouter via regex si absent)
- Les URLs Supabase de WiseWand restent stables (sinon télécharger les images et les uploader via `/wp/v2/media`)

```python
# Post-processing images (à intégrer dans push_content.py)
import re
content = re.sub(r'<img(?![^>]*loading=)', r'<img loading="lazy"', content)
content = re.sub(r'<img(?![^>]*alt=)([^>]*)>', r'<img\1 alt="<KW principal> illustration">', content)
```

### Téléchargement et hébergement WP des images (optionnel mais recommandé)

Pour éviter une dépendance sur les URLs Supabase WiseWand (risque de lien cassé à terme), **uploader les images sur le WP cible** :

```python
def upload_image_to_wp(image_url, title, alt):
    img_data = requests.get(image_url, timeout=30).content
    r = requests.post(
        f"https://www.<domain>/wp-json/wp/v2/media",
        auth=(USER, PWD),
        headers={
            "Content-Disposition": f'attachment; filename="{title}.jpg"',
            "Content-Type": "image/jpeg",
        },
        data=img_data, timeout=60,
    )
    media = r.json()
    # Set alt text via PUT (separate call)
    requests.post(
        f"https://www.<domain>/wp-json/wp/v2/media/{media['id']}",
        auth=(USER, PWD), json={"alt_text": alt}, timeout=30,
    )
    return media["source_url"], media["id"]
```

Remplacer ensuite chaque URL Supabase dans le contenu par l'URL WP avant push.

### Ton

- Voix : expert, rigoureux, accessible — éviter le marketing creux
- Langue : française (lexique métier OK : SERP, KW, backlink, DR, KD, INP, CLS, AI Overviews)
- Source unique d'autorité dans l'intro : indiquer dates, chiffres, références officielles
- **Si la page est ancienne** : ajouter les évolutions 2025-2026 (AI Overviews, INP, E-E-A-T étendu déc 2025, Brand Radar Ahrefs, etc.)

### Vérification fréquences (locale, avant push)

```python
import collections, re
text = open('01-nouveau-contenu.md').read()
plain = re.sub(r'[#*_>|\[\]()-]', ' ', text)
plain = re.sub(r'\s+', ' ', plain).strip()
words = [w.lower() for w in plain.split()]
counts = collections.Counter(words)
# vérifier vs diff SEOQuantum
```
Si plusieurs cibles à >50 % d'écart : itérer la rédaction avant de pousser.

## Étape 6 — Convertir en HTML WP-friendly (`02-page-optimisee.html`)

Le contenu envoyé en `content` à WordPress doit être **HTML pur** (pas de markdown) avec :

1. **Pas** de `<html>`, `<head>`, `<body>` (WP gère)
2. **CSS inline minimal** via balise `<style>` au début, classes préfixées `uplix-*` (ou `<agence>-*`) pour ne pas conflit avec le thème
3. **JSON-LD** dans le content (au début), WP ne le strip pas par défaut
4. **Balises sémantiques** : `<h2>`, `<h3>`, `<p>`, `<ul>`, `<ol>`, `<table>`, `<details>`, `<summary>`, `<blockquote>`
5. **Liens** : URLs complètes (https://www.<domain>/...) pour stabilité
6. **Anchors d'en-têtes** : `<h2 id="slug-section">` pour table des matières et liens directs

### Template CSS de base (à adapter au site)

Voir `assets/template_styles.html` et `assets/json_ld_templates.json` dans le skill.

## Étape 7 — GATE QUALITÉ PRÉ-PUSH (BLOQUANTE)

**Aucun push WordPress (live OU draft) n'est autorisé tant que cette gate n'est pas passée à 14/14.**

Copier `assets/markers_check.py` dans le dossier de livrable, puis lancer :

```bash
python markers_check.py 02-page-optimisee.html \
  --title "<NEW_TITLE>" \
  --excerpt "<NEW_EXCERPT>" \
  --domain <domain> \
  [--allow-h1]   # uniquement si le thème WP ne rend PAS le title en H1
```

### Les 14 marqueurs obligatoires

| # | Marqueur | Seuil |
|---|---|---|
| 01 | Title | 50-60 car (tolérance 45-65) |
| 02 | Meta description | 145-160 car (tolérance 120-165) |
| 03 | H1 unique | 0 `<h1>` dans le content (le thème rend le title) |
| 04 | Structure H2 | ≥ 6 H2 avec `id` (anchors) |
| 05 | Structure H3 | ≥ 3 H3 |
| 06 | Word count | ≥ 2 700 mots |
| 07 | TL;DR | encadré résumé dans les 6 000 premiers caractères |
| 08 | FAQ | ≥ 8 `<details><summary>` |
| 09 | Tableaux | ≥ 1 tableau comparatif (idéal 2) |
| 10 | Images | ≥ 3 inline, alt non vide, `loading="lazy"`, 0 URL Supabase |
| 11 | JSON-LD | présent, parseable, sans HowTo/FAQPage/SpecialAnnouncement |
| 12 | Maillage interne | ≥ 5 liens internes, ≥ 4 ancres distinctes (Boussardon) |
| 13 | Lien externe | ≥ 1 source officielle |
| 14 | Fraîcheur | "Mis à jour le" + auteur/équipe visibles |

### Règles de la gate

1. **Exit code 0 (14/14)** → passer à l'Étape 8 (push)
2. **Exit code 1** → corriger les marqueurs KO, relancer. Maximum **2 itérations de correction** ; si la gate échoue encore, **basculer en mode `draft`** + lister les marqueurs KO à l'utilisateur — ne JAMAIS forcer un push live
3. Vérifier aussi les **fréquences SEOQuantum** (Étape 5, vérification locale) avant la gate : si plusieurs cibles à >50 % d'écart, itérer la rédaction d'abord
4. Afficher le récap 14/14 dans la sortie AVANT le push (l'utilisateur doit pouvoir voir la checklist)

## Étape 8 — Push WordPress

### Option A — Push direct (mode `live`)

```bash
WP_USER="<user>" WP_APP_PASSWORD="<app password>" \
  python Audits/<domain>/livrables/<date>-optimisation-<slug>/push_content.py
```

Le script `push_content.py` (copié depuis `assets/push_content.py`) :
1. Re-backup `backup_post_<id>_pre_push.json`
2. PUT `/wp-json/wp/v2/posts/<id>` avec body `{title, content, excerpt}`
3. Sauvegarde la réponse dans `after_post_<id>.json`
4. Vérifie 10-15 markers clés en backend ET en live (avec `?bypass=<timestamp>` pour contourner cache navigateur)
5. Reporte un récap chiffré

### Option B — Mode `draft` (révision sans toucher au live)

Modifier le payload : `{title, content, excerpt, status: "draft"}` → WordPress crée une révision draft. L'utilisateur publie manuellement depuis WP-admin.

### Credentials

Lire en mémoire le site cible :
- uplix.fr → `[[reference_uplix_wp_api]]` (user=`damien`, App Password en mémoire)
- Autre site → demander à l'utilisateur (ne pas hardcoder)

## Étape 9 — Vérification + récap

Sortir un récap final :

```
✓ Mise à jour appliquée en LIVE
Post id <id> — slug <slug> — site <domain>
─────────────────────────────────────────
Title         : <ancien> → <nouveau>
Content len   : <ancien> → <nouveau> chars (+X %)
Modified      : <timestamp>

Markers backend : XX/XX OK
Markers live    : Y/Y OK

advisor_score SEOQuantum : <avant> → <après cible>
content_len               : <avant> → <après>

Sauvegardes :
  - backup_post_<id>_before.json   (état initial)
  - backup_post_<id>_pre_push.json (juste avant push)
  - after_post_<id>.json           (après push)

À faire côté toi :
  1. Vider cache WP Rocket / FlyingPress / Cloudflare
  2. Demander indexation GSC (Inspect URL → Request indexing)
  3. Monitorer positions sur <KW principal> + secondaires (vol Haloscan) sur 30 jours
```

## Étape 10 — Documenter dans MEMORY

Si un pattern non standard émerge (problème API, structure spéciale, plugin spécifique), enrichir `[[reference_<domain>_wp_api]]` avec la note.

## Règles critiques

### Schemas JSON-LD à NE JAMAIS recommander
- `HowTo` (déprécié sept 2023)
- `SpecialAnnouncement` (déprécié juil 2025)
- `FAQPage` (restreint août 2023 aux sites gouvernementaux/santé) — utiliser une FAQ HTML simple sans schema

### Schemas à privilégier selon le type de page

| Type de page | Schemas |
|---|---|
| Article guide/comparatif | `Article` + `BreadcrumbList` (+ `Review` si avis) |
| Page outil/SaaS | `SoftwareApplication` + `AggregateRating` + `Article` |
| Page service agence | `Service` + `Organization` + `BreadcrumbList` |
| Page produit e-commerce | `Product` + `Offer` + `AggregateRating` |
| Page locale | `LocalBusiness` + `PostalAddress` + `OpeningHoursSpecification` |

### Règles images obligatoires

- **1 image featured** (cover) générée par WiseWand `use_image=true` avec `image_ratio="16:9"`
- **3 images inline minimum** dans le corps via `use_inlineimages=true` + `inlineimages_count=3`
- **Palette cohérente** avec le site cible via `image_use_palette=true` + `image_primary_color` / `image_secondary_color`
- **Alt text descriptif** sur chaque `<img>` (post-processing si manquant)
- **`loading="lazy"`** sur toutes les images sauf la cover (post-processing)
- **Hébergement WP** : uploader les images sur le WP cible via `/wp/v2/media` avant push pour éviter les dépendances aux URLs externes Supabase WiseWand
- **JSON-LD Article `image`** : pointer vers l'URL WP (pas Supabase) une fois upload effectué

### Métriques obsolètes — interdit de référencer
- **FID** → remplacé par **INP** depuis mars 2024
- **PageSpeed Insights v5** → utiliser v6+

### E-E-A-T (étendu à TOUTES les requêtes compétitives depuis déc 2025)
- Auteur visible avec lien vers page expert/agence
- Date publication ET modification
- Sources citées (officielles)
- Témoignages d'expérience pratique
- Mise à jour annuelle minimum si "best of / top X / guide année"

### Maillage interne (méthode Boussardon)
- 5 liens sortants minimum vers piliers + lexique
- Cibles : **Know→Do prioritaire** (page satellite → page conversion)
- **5 ancres différentes** pour chaque cible (varier les formulations)
- Pas de bloc "Voir aussi" en footer — liens dans le corps du texte
- Cross-pillar obligatoire (lier entre univers)

### Workflow auto vs questions

- **Auto** : tout le processus (étapes 1 à 9) sans interruption sauf erreur fatale
- **Demander** uniquement si :
  - Credentials WP introuvables pour le domaine
  - Le slug WP n'existe pas (post inconnu)
  - SEOQuantum advisor renvoie une erreur API
  - Mode `draft` non spécifié et le post a >100 clics/mois (sécurité)
  - La gate qualité (Étape 7) échoue encore après 2 itérations de correction

### En cas d'échec partiel
- **Gate qualité <14/14 après 2 itérations** → JAMAIS de push live. Basculer en `draft` + récap des marqueurs KO, ou laisser le livrable en local pour révision humaine
- Si push WP échoue → laisser le brouillon en local + script `push_content.py` prêt, ne PAS rollback
- Si SEOQuantum timeout → utiliser uniquement Haloscan + GSC, signaler dans le brief
- Si GSC ne trouve pas la page → continuer (page peut être nouvelle), signaler dans le brief

## Assets du skill

Dans `.claude/skills/seo-content-refresh/assets/` :
- `push_content.py` — script de push réutilisable (à copier dans chaque dossier de livrable)
- `template_styles.html` — CSS inline classes `uplix-*` (TL;DR, FAQ accordéon, tableaux, callout CTA)
- `json_ld_templates.json` — templates JSON-LD par type de page
- `markers_check.py` — gate qualité pré-push : 14 marqueurs obligatoires, exit 0 = push autorisé, exit 1 = push interdit (Étape 7)

## Résultat attendu

À la fin de l'invocation, le user a :
1. Un dossier livrable complet avec tous les artefacts
2. La page mise à jour en live (mode `live`) ou en draft (mode `draft`)
3. Un récap chiffré markdown
4. Des sauvegardes pour rollback
