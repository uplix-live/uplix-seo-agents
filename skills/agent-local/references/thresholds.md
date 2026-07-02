<!-- Mis à jour : 2026-06-11 -->
# Seuils SEO standardisés — SOURCE DE VÉRITÉ UNIQUE

> **Règle pour tous les skills, agents et prompts d'audit** : ne JAMAIS recopier ces valeurs dans un autre fichier.
> Référencer ce fichier (`claude-seo/seo/references/thresholds.md`) et le charger à la demande.
> Si une valeur diverge ailleurs dans le projet, c'est CE fichier qui fait foi — corriger l'autre.

## 1. Core Web Vitals

Détails complets (subparts LCP, bottlenecks, outils) : voir `cwv-thresholds.md`.

| Métrique | Bon | À améliorer | Mauvais |
|---|---|---|---|
| LCP | ≤ 2,5 s | 2,5–4,0 s | > 4,0 s |
| INP | ≤ 200 ms | 200–500 ms | > 500 ms |
| CLS | ≤ 0,1 | 0,1–0,25 | > 0,25 |
| TTFB (subpart LCP) | < 200 ms (excellent) / < 800 ms (cible CrUX) | 200–500 ms | > 800 ms |

- **INP a remplacé FID le 12 mars 2024** — ne jamais référencer FID.
- Évaluation au **75e percentile** des données terrain (CrUX), page level + origin level.

## 2. Contenu

| Critère | Seuil | Note |
|---|---|---|
| **Thin content** | < 300 mots OU ratio texte/HTML < 10 % | Les deux conditions se vérifient ensemble |
| **Cannibalisation (similarité)** | ≥ 0,85 (cosinus) | Seuil unique projet — pas 0,80 |
| Word count minimum par type | Homepage 500 · Service 800 · Blog 1 500 · Produit 400 · Catégorie 400 · Location primaire 600 / secondaire 500 | Détail : `quality-gates.md` |
| **Content refresh (rédaction)** | ≥ 2 700 mots, idéal 3 000–3 500 | Skill `/seo-content-refresh` |
| Pages location | WARNING à 30+, HARD STOP à 50+ | Détail : `quality-gates.md` |

## 3. Balises on-page

| Élément | Seuil d'audit (flag si hors plage) | Cible de rédaction |
|---|---|---|
| Title | 30–60 caractères | **50–60 caractères** (tolérance 45–65) |
| Meta description | 120–160 caractères | **145–160 caractères** |
| Alt text images | 10–125 caractères, descriptif | Descriptif + KW naturel |
| H1 | Exactement 1 par page | KW principal présent |

## 4. Maillage interne (méthode Boussardon)

| Critère | Seuil |
|---|---|
| Liens internes par article (1 500+ mots) | 5–10 dans le corps du texte |
| Liens internes page service | 3–5 |
| Ancres par cible | 5 formulations différentes (jamais N fois la même ancre) |
| Direction prioritaire | Know → Do (satellite → conversion) |
| Pages orphelines | 0 toléré |
| Blocs "Voir aussi" en footer | Interdits — liens dans le corps |

## 5. Schema.org — interdits et restrictions

| Type | Statut |
|---|---|
| `HowTo` | ❌ Déprécié (sept. 2023) — ne jamais recommander |
| `SpecialAnnouncement` | ❌ Déprécié (juil. 2025) |
| `FAQPage` | ⚠️ Restreint (août 2023) aux sites gouvernementaux/santé — FAQ HTML sans schema partout ailleurs |

Liste complète des types actifs/dépréciés : `schema-types.md`.

## 6. E-E-A-T

Étendu à **toutes les requêtes compétitives** depuis le core update de décembre 2025. Framework complet et pondérations : `eeat-framework.md`.

## 7. Indexation & technique

| Critère | Seuil |
|---|---|
| Chaînes de redirections | Max 1 saut (flag si > 1) |
| Taille DOM | > 1 500 éléments = préoccupant |
| Profondeur de crawl | Pages stratégiques ≤ 3 clics depuis la home |
| Sitemap | < 50 000 URLs / 50 Mo par fichier, uniquement URLs 200 indexables canoniques |

## 8. Recommandations — niveau d'exigence obligatoire

Chaque recommandation doit être **poussée au maximum et auto-suffisante** (le client l'implémente sans question de suivi) :

| Élément | Obligatoire |
|---|---|
| URL(s) exacte(s) | Vérifiées (200, indexables) — jamais de catégorie vague sans liste |
| KW + volume + position | Avec la source (Haloscan / GSC / Ahrefs) |
| Action technique | Format avant → après (ex. title actuel → title proposé avec nb de caractères) |
| Exemple prêt à implémenter | Snippet HTML/JSON-LD complet, paragraphe rédigé, liste d'ancres |
| Gain chiffré estimé | CTR curve × volume (ex. pos. 12 → top 5 = +320 clics/mois) |
| Sources croisées | Minimum 2 (donnée vérifiable) |

Quick Wins : format `quoi | où | pourquoi | impact estimé`.

## 9. Fraîcheur du contenu & déclin (refresh)

Bandes de **fraîcheur par type de contenu** (jours depuis la dernière mise à jour significative) — déclenchent un examen de refresh :

| Type de contenu | Vieillissant (vigilance) | Périmé (à rafraîchir) |
|---|---|---|
| Actualité / news | 60 j | 90 j |
| YMYL (santé, finance, juridique) | 150 j | 180 j |
| Logiciel / SaaS / tech | 220 j | 270 j |
| Commercial / transactionnel | 305 j | 365 j |
| Evergreen (guides intemporels) | 460 j | 545 j |
| Référence / documentation | 600 j | 730 j |

**Signal de déclin GSC (CTR decay)** — page à rafraîchir en priorité si, entre 2 périodes comparables :

| Signal | Seuil |
|---|---|
| Chute de CTR à impressions stables | **CTR −30 %** avec **impressions stables (±20 %)** |
| Chute de clics | **clics −30 %** |
| Perte de position moyenne | **position +3 places** |

> **Arbitrage refresh = croiser déclin × Business Value Score** (`bvs.md`) : déclin + BVS ≥ 4 → refresh prioritaire ; déclin + BVS ≤ 3 → consolidation/suppression plutôt que refresh ; ne jamais rafraîchir une page *zero-click trap* (la SERP répondra à sa place).
