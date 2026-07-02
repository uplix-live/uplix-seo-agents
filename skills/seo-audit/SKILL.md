---
name: seo-audit
description: >
  Full website SEO audit with parallel subagent delegation. Crawls up to 500
  pages, detects business type, delegates to 6 specialists, generates health
  score. Use when user says "audit", "full SEO check", "analyze my site",
  or "website health check". Quick parallel audit WITHOUT paid APIs — for a
  comprehensive multi-source audit (Haloscan, Ahrefs, GSC, French market, HTML
  deliverables), use seo-audit-complet instead. For a single page, use seo-page.
---

# Full Website SEO Audit

> **Scope** : audit rapide parallèle, sans APIs payantes.
> Audit complet multi-sources (Haloscan × Ahrefs × GSC + livrables HTML) → skill `seo-audit-complet`.
> Page unique → skill `seo-page`. Seuils : `references/thresholds.md` (source de vérité).

## Process

1. **Fetch homepage** — use `scripts/fetch_page.py` (at project root) to retrieve HTML
2. **Detect business type** — analyze homepage signals per seo orchestrator
3. **Crawl site** — follow internal links up to 500 pages, respect robots.txt
4. **Delegate to subagents** (if available, otherwise run inline sequentially):
   - `seo-technical` — robots.txt, sitemaps, canonicals, Core Web Vitals, security headers
   - `seo-content` — E-E-A-T, readability, thin content, AI citation readiness
   - `seo-schema` — detection, validation, generation recommendations
   - `seo-sitemap` — structure analysis, quality gates, missing pages
   - `seo-performance` — LCP, INP, CLS measurements
   - `seo-visual` — screenshots, mobile testing, above-fold analysis
5. **Score** — aggregate into SEO Health Score (0-100)
6. **Report** — generate prioritized action plan

## Crawl Configuration

```
Max pages: 500
Respect robots.txt: Yes
Follow redirects: Yes (max 3 hops)
Timeout per page: 30 seconds
Concurrent requests: 5
Delay between requests: 1 second
```

## Output Files

- `FULL-AUDIT-REPORT.md` — Comprehensive findings
- `ACTION-PLAN.md` — Prioritized recommendations (Critical → High → Medium → Low)
- `screenshots/` — Desktop + mobile captures (if Playwright available)

## Scoring Weights

| Category | Weight |
|----------|--------|
| Technical SEO | 25% |
| Content Quality | 25% |
| On-Page SEO | 20% |
| Schema / Structured Data | 10% |
| Performance (CWV) | 10% |
| Images | 5% |
| AI Search Readiness | 5% |

## Report Structure

### Executive Summary
- Overall SEO Health Score (0-100)
- Business type detected
- Top 5 critical issues
- Top 5 quick wins

### Technical SEO
- Crawlability issues
- Indexability problems
- Security concerns
- Core Web Vitals status

### Content Quality
- E-E-A-T assessment
- Thin content pages
- Duplicate content issues
- Readability scores

### On-Page SEO
- Title tag issues
- Meta description problems
- Heading structure
- Internal linking gaps

### Schema & Structured Data
- Current implementation
- Validation errors
- Missing opportunities

### Performance
- LCP, INP, CLS scores
- Resource optimization needs
- Third-party script impact

### Images
- Missing alt text
- Oversized images
- Format recommendations

### AI Search Readiness
- Citability score
- Structural improvements
- Authority signals

## Priority Definitions

- **Critical**: Blocks indexing or causes penalties (fix immediately)
- **High**: Significantly impacts rankings (fix within 1 week)
- **Medium**: Optimization opportunity (fix within 1 month)
- **Low**: Nice to have (backlog)

## Output Modes

Adapter le format de restitution selon l'interlocuteur. Demander en début d'audit ou détecter via le contexte.

### Boss Mode (DG, CMO, investisseur)
Format : 1 page max. Score global, verdict en 1 phrase, 3 priorités avec ROI estimé, prochaine action concrète.

```
## Audit SEO — [Domaine] — [Date]

**Score global : XX/100** — [Verdict en 1 phrase]

### 3 priorités
1. [Action] → Impact estimé : +X% trafic / €X valeur trafic
2. [Action] → Impact estimé : …
3. [Action] → Impact estimé : …

**Prochaine étape** : [Une action précise, assignée, avec deadline]
```

### Operator Mode (chef de projet SEO, responsable marketing)
Format : roadmap P0/P1/P2 avec actions concrètes, responsable, effort et gain estimé.

```
## Roadmap SEO — [Domaine]

### P0 — Cette semaine (bloquants)
| Action | Où | Effort | Gain estimé |
|--------|-----|--------|-------------|
| …      | …   | …      | …           |

### P1 — Ce mois-ci (fort impact)
| Action | Où | Effort | Gain estimé |
|--------|-----|--------|-------------|

### P2 — Backlog (optimisations)
| Action | Où | Effort | Gain estimé |
|--------|-----|--------|-------------|
```

### Specialist Mode (développeur, consultant SEO, analyste)
Format : rapport complet, données brutes, causes racines, extraits de code, benchmarks.
Correspond au `FULL-AUDIT-REPORT.md` standard — toutes les sections détaillées, chiffres vérifiables, sources citées.
