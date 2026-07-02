---
name: geo-compare
description: >
  Compare deux audits GEO (baseline vs actuel) pour un même domaine et génère
  un rapport mensuel de progression. Suit l'évolution du GEO Score, des scores
  par catégorie, de l'accessibilité AI crawlers, et du statut des actions.
  Use when user says "comparer les audits GEO", "progression GEO", "delta GEO",
  "rapport mensuel GEO", "évolution GEO", "geo compare", "geo monthly report".
---

# GEO Compare — Rapport de Progression Mensuel

## Commandes

```
/geo-compare <domain>
/geo-compare <baseline-file> <current-file>
```

**Exemples :**
```
/geo-compare maaf.fr
/geo-compare Audits/maaf.fr/md/GEO-AUDIT-2026-02.md Audits/maaf.fr/md/GEO-AUDIT-2026-03.md
```

---

## Métriques suivies

### Score GEO global (0-100)
- Score baseline vs score actuel
- Delta (+/-)
- Tendance sur les 3 derniers mois si disponible

### Scores par catégorie

| Catégorie | Poids | Baseline | Actuel | Delta |
|-----------|-------|----------|--------|-------|
| AI Citability & Visibility | 25% | — | — | — |
| Brand Authority Signals | 20% | — | — | — |
| Content Quality & E-E-A-T | 20% | — | — | — |
| Technical Foundations | 15% | — | — | — |
| Structured Data | 10% | — | — | — |
| Platform Optimization | 10% | — | — | — |

### Readiness par plateforme

| Plateforme | Baseline | Actuel | Delta |
|------------|----------|--------|-------|
| Google AI Overviews | — | — | — |
| ChatGPT Web Search | — | — | — |
| Perplexity AI | — | — | — |
| Google Gemini | — | — | — |
| Bing Copilot | — | — | — |

### Accès AI crawlers

| Crawler | Baseline | Actuel | Changement |
|---------|----------|--------|------------|
| GPTBot (OpenAI) | — | — | — |
| ClaudeBot (Anthropic) | — | — | — |
| PerplexityBot | — | — | — |
| OAI-SearchBot | — | — | — |
| Googlebot | — | — | — |
| Bingbot | — | — | — |

### Suivi des actions

Pour chaque action du plan précédent :
- [ ] Action 1 — statut (terminé / en cours / non démarré)
- [ ] Action 2 — statut
- [ ] ...

---

## Structure du rapport de sortie

Générer `GEO-COMPARE-<domain>-<YYYY-MM>.md` dans `Audits/<domain>/md/` :

```markdown
# GEO Monthly Delta Report — <domain>
**Période :** <mois baseline> → <mois actuel>
**Généré le :** <date>

## Résumé exécutif
<2-3 phrases résumant la progression globale>

## Score GEO global

| | Baseline | Actuel | Delta |
|-|----------|--------|-------|
| **Score** | XX/100 | XX/100 | **+X** ✅ / **-X** ⚠️ |

[Barre de progression visuelle en texte]
Baseline : [████████░░] 80/100
Actuel   : [█████████░] 87/100

## Progression par catégorie
<tableau avec deltas colorés — ↑ gain / ↓ régression / = stable>

## Plateforme readiness
<tableau avant/après par plateforme>

## Accès AI crawlers
<tableau des changements — nouveau accès accordé / bloqué>

## Wins du mois
<liste des améliorations concrètes réalisées>

## Actions terminées ✅
<liste des actions du plan précédent marquées comme terminées>

## Actions en retard ⚠️
<liste des actions non démarrées ou bloquées>

## Plan d'action — 30 prochains jours
- [ ] Action prioritaire 1 (impact estimé : +X pts)
- [ ] Action prioritaire 2 (impact estimé : +X pts)
- [ ] ...

## Projection 6 mois
<projection linéaire basée sur la vélocité actuelle>
Vélocité actuelle : +X pts/mois
Score projeté dans 6 mois : ~XX/100

## Impact business estimé
<estimation basée sur les benchmarks GEO>
- Trafic AI-referred actuel estimé : X visites/mois
- Projection à 6 mois : +XX% (basé sur score GEO)
- AI traffic conversion rate : 4.4x vs trafic organique standard
```

---

## Calcul du delta de score

```python
# Formule de calcul du delta pondéré
delta_total = sum(
    (score_actuel[cat] - score_baseline[cat]) * poids[cat]
    for cat in categories
)

# Interprétation
if delta_total >= 10:
    tendance = "Forte progression ✅"
elif delta_total >= 5:
    tendance = "Bonne progression ✅"
elif delta_total >= 0:
    tendance = "Légère progression →"
elif delta_total >= -5:
    tendance = "Légère régression ⚠️"
else:
    tendance = "Régression significative ❌"
```

---

## Sources de données

Pour remplir le rapport, chercher dans cet ordre :
1. Fichiers `.md` dans `Audits/<domain>/md/` (audits précédents)
2. Fichiers Excel dans `Audits/<domain>/livrables/excel/`
3. Relancer les checks techniques si les données sont trop anciennes (> 30 jours)

---

## Stockage

Rapports sauvegardés dans : `Audits/<domain>/md/GEO-COMPARE-<domain>-<YYYY-MM>.md`

Index des rapports passés dans : `Audits/<domain>/md/GEO-HISTORIQUE.md`
