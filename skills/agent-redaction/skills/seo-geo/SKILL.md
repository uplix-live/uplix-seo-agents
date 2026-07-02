---
name: seo-geo
description: >
  Optimize content for AI Overviews (formerly SGE), ChatGPT web search,
  Perplexity, and other AI-powered search experiences. Generative Engine
  Optimization (GEO) analysis including brand mention signals, AI crawler
  accessibility, passage-level citability scoring, and
  platform-specific optimization. Use when user says "AI Overviews", "SGE",
  "GEO", "AI search", "LLM optimization", "Perplexity", "AI citations",
  "ChatGPT search", or "AI visibility".
---

# AI Search / GEO Optimization (February 2026)

## Key Statistics

| Metric | Value | Source |
|--------|-------|--------|
| AI Overviews reach | 1.5 billion users/month across 200+ countries | Google |
| AI Overviews query coverage | 50%+ of all queries | Industry data |
| AI-referred sessions growth | 527% (Jan-May 2025) | SparkToro |
| ChatGPT weekly active users | 900 million | OpenAI |
| Perplexity monthly queries | 500+ million | Perplexity |

## Critical Insight: Brand Mentions > Backlinks

**Brand mentions correlate 3× more strongly with AI visibility than backlinks.**
(Ahrefs December 2025 study of 75,000 brands)

| Signal | Correlation with AI Citations |
|--------|------------------------------|
| YouTube mentions | ~0.737 (strongest) |
| Reddit mentions | High |
| Wikipedia presence | High |
| LinkedIn presence | Moderate |
| Domain Rating (backlinks) | ~0.266 (weak) |

**Only 11% of domains** are cited by both ChatGPT and Google AI Overviews for the same query — platform-specific optimization is essential.

---

## GEO Analysis Criteria (Updated)

### 1. Citability Score (25%)

**Optimal passage length: 134-167 words** for AI citation.

**Strong signals:**
- Clear, quotable sentences with specific facts/statistics
- Self-contained answer blocks (can be extracted without context)
- Direct answer in first 40-60 words of section
- Claims attributed with specific sources
- Definitions following "X is..." or "X refers to..." patterns
- Unique data points not found elsewhere

**Weak signals:**
- Vague, general statements
- Opinion without evidence
- Buried conclusions
- No specific data points

### 2. Structural Readability (20%)

**92% of AI Overview citations come from top-10 ranking pages**, but 47% come from pages ranking below position 5 — demonstrating different selection logic.

**Strong signals:**
- Clean H1→H2→H3 heading hierarchy
- Question-based headings (matches query patterns)
- Short paragraphs (2-4 sentences)
- Tables for comparative data
- Ordered/unordered lists for step-by-step or multi-item content
- FAQ sections with clear Q&A format

**Weak signals:**
- Wall of text with no structure
- Inconsistent heading hierarchy
- No lists or tables
- Information buried in paragraphs

### 3. Multi-Modal Content (15%)

Content with multi-modal elements sees **156% higher selection rates**.

**Check for:**
- Text + relevant images
- Video content (embedded or linked)
- Infographics and charts
- Interactive elements (calculators, tools)
- Structured data supporting media

### 4. Authority & Brand Signals (20%)

**Strong signals:**
- Author byline with credentials
- Publication date and last-updated date
- Citations to primary sources (studies, official docs, data)
- Organization credentials and affiliations
- Expert quotes with attribution
- Entity presence in Wikipedia, Wikidata
- Mentions on Reddit, YouTube, LinkedIn

**Weak signals:**
- Anonymous authorship
- No dates
- No sources cited
- No brand presence across platforms

### 5. Technical Accessibility (20%)

**AI crawlers do NOT execute JavaScript** — server-side rendering is critical.

**Check for:**
- Server-side rendering (SSR) vs client-only content
- AI crawler access in robots.txt
- RSL 1.0 licensing terms

---

## AI Crawler Detection

Check `robots.txt` for these AI crawlers:

| Crawler | Owner | Purpose |
|---------|-------|---------|
| GPTBot | OpenAI | ChatGPT web search |
| OAI-SearchBot | OpenAI | OpenAI search features |
| ChatGPT-User | OpenAI | ChatGPT browsing |
| ClaudeBot | Anthropic | Claude web features |
| PerplexityBot | Perplexity | Perplexity AI search |
| CCBot | Common Crawl | Training data (often blocked) |
| anthropic-ai | Anthropic | Claude training |
| Bytespider | ByteDance | TikTok/Douyin AI |
| cohere-ai | Cohere | Cohere models |

**Recommendation:** Allow GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot for AI search visibility. Block CCBot and training crawlers if desired.

---


## RSL 1.0 (Really Simple Licensing)

New standard (December 2025) for machine-readable AI licensing terms.

**Backed by:** Reddit, Yahoo, Medium, Quora, Cloudflare, Akamai, Creative Commons

**Check for:** RSL implementation and appropriate licensing terms.

---

## Platform-Specific Optimization

| Platform | Key Citation Sources | Optimization Focus |
|----------|---------------------|-------------------|
| **Google AI Overviews** | Top-10 ranking pages (92%) | Traditional SEO + passage optimization |
| **ChatGPT** | Wikipedia (47.9%), Reddit (11.3%) | Entity presence, authoritative sources |
| **Perplexity** | Reddit (46.7%), Wikipedia | Community validation, discussions |
| **Google Gemini** | Knowledge Graph, YouTube (fort), Schema.org | Structured data, YouTube, Google Business |
| **Bing Copilot** | Bing index, LinkedIn, sites autoritaires | Bing SEO, IndexNow, meta descriptions |

### Google AI Overviews
- Priorise les pages déjà dans le top-10 organique
- Favorise les réponses directes, les tableaux, les listes, les FAQ
- Headings en forme de questions ("Comment...", "Qu'est-ce que...")
- Dates de publication et de mise à jour visibles
- Structured data (FAQ, HowTo retiré, Article)

### ChatGPT Web Search (index Bing)
- Utilise l'index Bing, pas Google — vérifier aussi Bing Webmaster Tools
- Wikipedia/Wikidata : 47.9% des citations ChatGPT viennent de Wikipedia
- Contenu long et complet (2 000+ mots) cité plus souvent
- Reconnaissance d'entité critique : sameAs vers Wikipedia/Wikidata dans le schema
- Reddit (11.3%) : présence dans les discussions communautaires pertinentes

### Perplexity AI
- Reddit en tête : 46.7% des citations Perplexity viennent de Reddit
- Valorise la validation communautaire et les discussions de forum
- Contenu récent (date visible) fortement favorisé
- Données originales et recherches exclusives très citées
- Multi-source : croiser plusieurs plateformes augmente la probabilité de citation

### Google Gemini
- Accès direct au Knowledge Graph Google — avoir une fiche entité complète
- **YouTube fortement pondéré** : créer des vidéos éducatives sur les sujets clés
- Google Business Profile intégré (pour les sites locaux)
- Schema.org intensivement utilisé : Organisation, Produit, Article avec auteur
- sameAs vers YouTube channel = signal fort pour Gemini

### Bing Copilot
- Vérifier Bing Webmaster Tools et soumettre le sitemap
- **IndexNow** : notifier Bing en temps réel à chaque mise à jour de contenu
- LinkedIn (B2B) : présence et thought leadership importants pour Bing
- Meta descriptions bien rédigées avec mots-clés exacts
- Vitesse de page < 2s (plus strict que Google sur ce critère)
- Réponses en 3-5 citations par query : être dans les top résultats Bing suffit

### Actions universelles (toutes plateformes)
1. Présence Wikipedia/Wikidata avec entité complète
2. Chaîne YouTube avec contenu éducatif
3. Hiérarchie de headings claire H1→H2→H3
4. Schema.org : Organization + sameAs exhaustif
5. Pages auteur avec credentials + liens Wikipedia/LinkedIn
6. Dates de publication et mise à jour visibles

---

## Scripts disponibles (dans `scripts/`)

```bash
# Scorer la citabilité passage par passage (score 0-100, grade A-F)
python scripts/citability_scorer.py https://example.com/page

# Scanner la présence de marque sur YouTube, Reddit, Wikipedia, LinkedIn
python scripts/brand_scanner.py "Nom de marque" example.com

```

---

## Output

Generate `GEO-ANALYSIS.md` with:

1. **GEO Readiness Score: XX/100**
2. **Platform breakdown** (Google AIO, ChatGPT, Perplexity scores)
3. **AI Crawler Access Status** (which crawlers allowed/blocked)
5. **Brand Mention Analysis** (presence on Wikipedia, Reddit, YouTube, LinkedIn)
6. **Passage-Level Citability** (optimal 134-167 word blocks identified)
7. **Server-Side Rendering Check** (JavaScript dependency analysis)
8. **Top 5 Highest-Impact Changes**
9. **Schema Recommendations** (for AI discoverability)
10. **Content Reformatting Suggestions** (specific passages to rewrite)

---

## Quick Wins

1. Add "What is [topic]?" definition in first 60 words
2. Create 134-167 word self-contained answer blocks
3. Add question-based H2/H3 headings
4. Include specific statistics with sources
5. Add publication/update dates
6. Implement Person schema for authors
7. Allow key AI crawlers in robots.txt

## Medium Effort

2. Add author bio with credentials + Wikipedia/LinkedIn links
3. Ensure server-side rendering for key content
4. Build entity presence on Reddit, YouTube
5. Add comparison tables with data
6. Implement FAQ sections (structured, not schema for commercial sites)

## High Impact

1. Create original research/surveys (unique citability)
2. Build Wikipedia presence for brand/key people
3. Establish YouTube channel with content mentions
4. Implement comprehensive entity linking (sameAs across platforms)
5. Develop unique tools or calculators
