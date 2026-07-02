# Business Value Score (BVS) — cadre de priorisation par valeur business

> **Principe** : avant de cibler un mot-clé ou de produire/rafraîchir un contenu, répondre à **une seule question** —
> **« Si on se positionne là-dessus, est-ce que ça amène un client ? »**
> Le BVS note cette valeur de **0 à 10**. Il sert à **prioriser** (quoi attaquer d'abord) et à **filtrer** (quoi ne pas produire).
> Il **complète** `thresholds.md` (seuils techniques/sémantiques) — il ne le remplace pas. Barème inspiré du système easygrowth, adapté au marché FR et à notre stack (Haloscan / Ahrefs / GSC).

## Formule

**BVS = clamp( Intent + SignauxCommerciauxSERP + CPC + MoneyPageMatch + PénalitéRéponseDirecte , 0 , 10 )**

### 1. Score d'intention (0 à +4)
| Intention | Points |
|---|---|
| Transactionnelle (achat/devis/contact) | 4 |
| Commerciale (BOFU, « prix », « tarif ») | 3 |
| Comparaison (« meilleur X », « X vs Y », « alternative à ») | 3 |
| Navigationnelle | 2 **uniquement si la marque rank déjà top 10**, sinon 0 |
| Informationnelle | 1 |
| Ambiguë | 1 |

Source intention : `seo_toolkit intent` / Haloscan `get_keywords_overview` (intent) / analyse SERP.

### 2. Signaux commerciaux dans la SERP (0 à +4, plafonné à 4)
| Signal présent | Points |
|---|---|
| Shopping pack | +2 |
| Product pack | +2 |
| Local pack (si requête locale) | +2 |
| ≥ 2 annonces payantes (Google Ads) | +1 |

Source : SERP Haloscan / Ahrefs `serp-overview` / SEObserver `serps`.

### 3. CPC (0 à +2) — en euros
| CPC | Points |
|---|---|
| ≥ 5 € | +2 |
| 1 € – 5 € | +1 |
| < 1 € ou inconnu | 0 |

Source : Haloscan / Ahrefs `keywords-overview`. (Un CPC élevé = des annonceurs paient = valeur commerciale prouvée.)

### 4. Money-Page Match (0 à +3)
Le KW correspond-il à une **page qui convertit** (offre/produit/service du client) ?
| Correspondance | Points |
|---|---|
| Totale (le KW cible directement une offre) | +3 |
| Partielle (univers adjacent à l'offre) | +1 |
| Aucune | 0 |

### 5. Pénalité réponse directe / zero-click (−4 à 0) — **garder la pire seule**
| Situation SERP | Points |
|---|---|
| Knowledge graph + réponse factuelle | −4 |
| Réponse instantanée / calculatrice | −4 |
| Knowledge panel sans organique above-the-fold | −3 |
| Featured snippet **complet** (réponse exhaustive) | −2 |
| AI Overview sans organique above-the-fold | −2 |
| Densité zero-click ≥ 70 % de la SERP | −2 |

Source : inspection SERP (AI Overview, featured snippet, PAA, knowledge panel) — Haloscan SERP / Ahrefs `serp-overview` / `seo-geo`.

## Règle « Zero-Click Trap » → force BVS = 0
Si **les 3** conditions sont vraies simultanément :
1. intention informationnelle ou ambiguë,
2. SERP avec knowledge graph **ou** réponse instantanée **ou** featured snippet complet,
3. money-page match = aucune,
→ **BVS = 0, skip** (documenter la raison). La SERP répondra à la place du site : CTR ≈ 0 même bien positionné. Viser la **citation GEO / le passage** (cf. `seo-geo`), pas une page dédiée.

## Mapping priorité / refus
| BVS | Priorité | Action |
|---|---|---|
| **8–10** | P1 🟢 | Cibler/produire immédiatement |
| **5–7** | P2 🟠 | Cibler quand le budget le permet |
| **2–4** | P3 🔵 | Mettre en réserve ; ne poursuivre que pour la **valeur de cluster** (pilier/maillage de cocon) |
| **0–1** | Skip 🔴 | **Ne jamais produire / cibler** — seuil de refus dur |

### Garde-fou content-gap : la money-page match agit en PLAFOND
En analyse de **content-gap concurrentiel**, le gap contient massivement des mots-clés de **blog des concurrents sans rapport avec l'offre du client** (ex. « police d'écriture », « instagram story », noms d'outils). Un KW peut être transactionnel + à fort CPC et pourtant n'amener **aucun client** au client analysé. Dans ce contexte, la money-page match n'est pas qu'un bonus, elle **plafonne** le BVS :

| Money-page match | Plafond BVS |
|---|---|
| Aucune | **2** (trafic non monétisable pour CE client → écarté/réserve) |
| Partielle | **7** |
| Totale | **10** |

> **Le BVS mesure la valeur, PAS la difficulté.** Ne jamais confondre avec le KD. Priorisation finale = **BVS × faisabilité × volume** (faisabilité = inverse de la difficulté KD/concurrence × proximité avec ce que le client couvre déjà). À volume égal, BVS 9 passe avant BVS 5.

## Pré-tri sans appel API (optionnel)
Pour dégrossir une grosse liste avant de consommer du budget SERP : calculer un **BVS partiel** = Intent + MoneyPageMatch seuls (composantes SERP/CPC à 0), trier, puis compléter par les signaux SERP uniquement sur le haut de la liste.

## Application au refresh (contenus existants)
Croiser BVS et signal de déclin GSC :
- **Déclin + BVS ≥ 4** → **refresh prioritaire**.
- **Déclin + BVS ≤ 3** → **ne pas rafraîchir** : consolidation/fusion ou suppression/no-index.
- **Stable + BVS élevé** → maintenir/renforcer.
- Seuil de déclin de référence (CTR decay) : **CTR −30 % à impressions stables (±20 %)** entre 2 périodes (cf. `thresholds.md` / agent-redaction Étape 4).

## Restitution (obligatoire)
- Colonne **BVS (0-10)** + le **détail des 5 composantes** sur chaque KW / territoire / URL.
- Onglet/section **« écartés (BVS ≤ 1) »** avec la raison — la transparence sur ce qu'on ne fait PAS fait partie de la reco.
- Signaler explicitement les *zero-click traps* et rediriger vers la stratégie GEO/passage.
