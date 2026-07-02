---
name: maillage-systeme
description: >
  Maillage interne stratégique d'un site (blog, catalogue, doc) : architecture en piliers,
  classification hub/satellite, sélection d'ancres avec diversification entrante,
  détection des pages orphelines et dead-end, audit complet du graphe interne.
  Complémentaire au skill maillage-interne-gsc qui exploite la donnée Search Console.
  Celui-ci raisonne sur la structure éditoriale et le contenu, sans dépendre de la GSC.
  Utilisable dès la phase de cadrage d'un nouveau site, avant qu'aucune donnée
  comportementale ne soit disponible.
  TOUJOURS utiliser ce skill quand l'utilisateur mentionne : architecture de maillage,
  piliers de blog, hub et satellite, ancres internes, anchor text, choix d'ancre, audit
  maillage interne, orphan pages, pages dead-end, link equity, structurer le maillage
  d'un nouveau site, mailler un blog avant lancement, plan de cocon, ou uploade
  une liste d'articles/URLs et veut un plan de maillage complet.
---

# Skill — Maillage Interne : Architecture, Ancres et Audit

## Rôle

Construire et auditer le graphe de liens internes d'un site à partir du contenu existant ou planifié, sans dépendre de la Search Console. Le skill produit trois livrables : une **architecture en piliers**, un **plan d'ancres diversifiées** par lien, et un **rapport d'audit** des trous structurels.

L'objectif n'est pas de générer des liens à la chaîne. C'est de construire un graphe où chaque lien est justifié par trois signaux : topique, intention et autorité.

---

## Réflexion appliquée (méthode Boussardon)

- Le maillage interne est **un système, pas une passe**. Trois axes simultanés : topique, intention, autorité.
- Une ancre, ce n'est pas un mot-clé. C'est **une promesse de continuité** entre deux pages, lue par Google, par les LLM (en vecteur), et par l'humain (en désir de cliquer).
- **5 ancres possibles vers la même page = 5 ancres différentes.** Un seul exact match. Le reste est partial / sémantique / contextuel long.
- **Test à voix haute** : si la phrase tombe juste sans le lien, l'ancre est bien intégrée. Si elle clopine, l'ancre est plaquée.
- **Le maillage Know→Do passe avant le maillage Know→Know.** Une page qui explique un concept doit toujours pointer vers la page qui permet de l'exécuter (outil, audit, démo).
- **Pas de "Voir aussi" en bas d'article.** Le contexte de lien est dilué. Liens contextuels in-body uniquement.
- **Une page mère n'est pas un titre de catégorie.** C'est l'article le plus stratégique du pilier, celui qui définit le vocabulaire et reçoit le plus de liens internes.
- **Le cross-pillar pollination compte autant que le maillage intra-cluster.** 1 lien sortant sur N doit pointer vers un autre pilier pour éviter la siloïsation (le silo SEO classique isole les sections, le cocon les fait communiquer).

---

## Données requises

| Source | Description | Obligatoire |
|--------|-------------|-------------|
| Liste des URLs/articles | Titre, slug, catégorie, excerpt, mots-clés cibles | Oui |
| Contenu intégral (markdown ou HTML) | Pour détecter les opportunités contextuelles | Recommandé |
| Mots-clés piliers (3-5) | Le vocabulaire métier business du client | Recommandé |
| Pages "Do" identifiées | URLs des outils, audits, formulaires, simulateurs | Recommandé |

**Minimum viable** : la liste des articles avec titre + excerpt + mots-clés. Sans le contenu intégral, le skill produit l'architecture mais pas les ancres précises.

---

## Raisonnement de l'agent (étapes obligatoires)

L'agent DOIT suivre ces étapes **dans l'ordre** avant de répondre.

### Étape 1 — Classifier chaque page en intention

Pour chaque article, déterminer son intention dominante :

| Intention | Description | Exemples de signaux |
|-----------|-------------|---------------------|
| **Know-Simple** | Définition courte, réponse directe | titre commence par "Qu'est-ce que", "C'est quoi" |
| **Know** | Guide approfondi, méthode, comparatif | titre "Comment", "Pourquoi", "Guide" |
| **Do** | Outil, simulateur, formulaire, démo | URL contient `/outils/`, `/audit`, `/contact` |

Une page peut avoir une intention dominante + une intention secondaire. Noter les deux.

### Étape 2 — Identifier les piliers

Regrouper les articles par cohérence sémantique (pas par catégorie technique). Cibler **3 à 5 piliers max**. Pas plus. Pas moins de 3.

Critères pour qu'un cluster forme un vrai pilier :
- Au moins 3 articles dans le cluster
- Un mot-clé business central qui revient dans tous les titres ou excerpts
- Une page-hub naturelle : l'article le plus complet ou le plus stratégique du cluster

Si un cluster a moins de 3 articles, il devient un **sous-cluster** d'un pilier existant, pas un pilier indépendant.

### Étape 3 — Désigner le hub de chaque pilier

Pour chaque pilier, identifier la page-hub :
- Article le plus complet (ou prévu pour l'être)
- Recouvre les concepts secondaires des autres articles du pilier
- Idéalement : positionné sur le mot-clé pilier exact

Le hub reçoit des liens entrants depuis tous les satellites. Le hub redistribue vers les satellites via des liens contextuels (pas une liste).

### Étape 4 — Cartographier les liens existants

Pour chaque article, lister :
- **Inbound links** : combien d'articles pointent vers lui ?
- **Outbound links** : vers combien d'articles pointe-t-il ?
- **Click depth** : combien de clics depuis la home ?

Détecter les anomalies :
- **Orphan pages** : 0 inbound link
- **Dead-end pages** : 0 outbound link
- **Hub sous-maillé** : moins de 5 inbound depuis ses satellites

### Étape 5 — Sélectionner les ancres pour chaque lien proposé

Pour chaque lien Source → Cible à créer, produire **3 propositions d'ancres** classées :

1. **Exact match** (1 max par cible, sur la première mention) : reproduit le mot-clé pilier exact de la cible
2. **Partial match** (60-70% des liens entrants vers une cible) : variation autour du mot-clé pilier
3. **Sémantique étendue** : reformule la promesse de la cible sans utiliser le mot-clé

Pour chaque ancre, vérifier les 5 critères :

| Critère | Question à se poser |
|---------|---------------------|
| Promesse de la cible | L'ancre reflète-t-elle ce que l'utilisateur va trouver, pas le titre H1 ? |
| Phrase porteuse | La phrase reste-t-elle fluide à voix haute sans le lien ? |
| Diversification | Cette ancre est-elle déjà utilisée vers la même cible depuis une autre page ? |
| Position | L'ancre porte-t-elle le verbe d'action ou le substantif central, pas un mot de liaison ? |
| Link context | Les 5 mots avant/après parlent-ils du sujet de la cible ? |

Si une ancre rate un critère, la rejeter.

### Étape 6 — Prioriser les liens à créer

Score d'urgence par lien proposé :

**Score = (impressions cible × poids_intention) + (gain_authority × 0.4)**

Où :
- `poids_intention` : Do = 1.0, Know-décisionnel = 0.8, Know = 0.5, Know-Simple = 0.3
- `gain_authority` : 1 si la source est un hub, 0.5 si la source est un satellite mailé, 0.2 sinon

Prioriser dans cet ordre :
1. **Liens manquants Hub → Satellite** dans un pilier (pour activer le cocon)
2. **Liens Know → Do** (pour orienter le funnel)
3. **Liens cross-pillar** (1 par pilier minimum vers un autre pilier)
4. **Liens vers pages orphelines** identifiées en étape 4

### Étape 7 — Vérifier les règles de conservation

Avant de finaliser le plan, valider :
- Aucune page orpheline restante (chaque page reçoit ≥ 1 inbound)
- Aucune page dead-end (chaque page contient ≥ 2 outbound)
- Chaque hub reçoit ≥ 5 inbound depuis ses satellites
- Aucune cible ne reçoit la même ancre 2 fois
- Densité raisonnable : 2 à 5 liens internes par 1000 mots, jamais plus

**NE PAS répondre avant d'avoir complété chaque étape.**

---

## Format de sortie OBLIGATOIRE

### Bloc 1 — Architecture détectée

```
PILIER 1 — [Nom thématique] (mot-clé pilier : "...")
├── HUB : [titre article + slug]
├── Satellite : [titre + slug] (intention : Know)
├── Satellite : [titre + slug] (intention : Know)
└── Satellite : [titre + slug] (intention : Do)

PILIER 2 — [Nom]
...
```

### Bloc 2 — Audit du graphe existant

Tableau :

| Article | Inbound | Outbound | Click depth | Statut |
|---------|---------|----------|-------------|--------|
| ... | 3 | 4 | 2 | OK |
| ... | 0 | 2 | 3 | **ORPHELINE** |
| ... | 5 | 0 | 1 | **DEAD-END** |

### Bloc 3 — Plan de liens à créer (priorisé)

Pour chaque lien proposé :

```
PRIORITÉ : HAUTE | Score : 8.4
─────────────────────────────────
SOURCE : [titre article source] (Know)
CIBLE  : [titre article cible] (Do)
PILIER : Cross-pillar (Pilier 1 → Pilier 3)
NATURE : Know → Do (orientation funnel)

PASSAGE PROPOSÉ :
"[Phrase complète où insérer le lien, en montrant les mots avant/après]"

ANCRES PROPOSÉES (choisir 1) :
  [exact]    "mot-clé pilier exact"
  [partial]  "variation naturelle du mot-clé"
  [sémant.]  "reformulation de la promesse cible"

JUSTIFICATION : [1 phrase sur pourquoi ce lien crée de la valeur]
```

### Bloc 4 — Règles de gouvernance

Une checklist finale que le client suit à chaque nouvelle publication :

- [ ] Le nouvel article reçoit ≥ 3 liens entrants depuis 3 articles existants
- [ ] Le nouvel article contient ≥ 3 liens sortants vers des articles existants
- [ ] Au moins 1 lien sortant pointe vers une page Do
- [ ] Au moins 1 lien sortant pointe vers un autre pilier (cross-pollination)
- [ ] Aucune ancre exacte n'est dupliquée vers la même cible
- [ ] Tous les liens sont in-body, aucun en bloc "Voir aussi"

---

## Points de vigilance

- **Ne pas tout automatiser.** Le skill propose, l'humain décide. Une ancre forcée détruit le naturel d'un texte.
- **Le contexte vaut plus que l'ancre.** Une ancre parfaite dans une phrase qui parle d'autre chose = lien faible. Réécris la phrase.
- **Le hub n'est pas figé.** Si un nouveau satellite devient plus complet que le hub historique, on bascule le hub. La structure suit le contenu, pas l'inverse.
- **Cross-pillar ≠ liens hors-sujet.** Le pont entre deux piliers doit reposer sur une vraie passerelle conceptuelle (pas "j'avais besoin d'un lien").
- **Ne jamais lier vers la home depuis le contenu.** La home a déjà tout le PageRank, elle n'en a pas besoin. Garde le jus pour les pages business.
- **Les FAQ sont une mine d'ancres.** Chaque réponse de FAQ qui mentionne un sous-sujet déjà traité doit lier. Densité haute, contexte naturel.
- **Densité plafonnée.** Au-delà de 5 liens internes pour 1000 mots, la dilution s'installe. Google pondère chaque ancre par 1/N où N est le nombre total de liens.

---

## Cas particulier — Site sans donnée GSC

Si le site est nouveau (moins de 3 mois ou pas d'accès GSC) :
- Étape 4 (cartographie inbound/outbound) se fait par parsing du contenu (markdown/HTML)
- Étape 6 (scoring) utilise un proxy : `position_business` (1 si Do, 0.7 si Know-décisionnel, 0.5 si Know, 0.3 si Know-Simple) au lieu d'impressions GSC
- Le plan reste valable, ajusté avec la GSC dès que la donnée arrive

---

## Cas particulier — Refonte de site existant

Si le site existe et a ≥ 6 mois de GSC :
- Chaîner ce skill avec **maillage-interne-gsc** : ce skill définit l'architecture, l'autre injecte la donnée comportementale
- Identifier les pages qui rankent déjà sur le pilier et les promouvoir hub si pertinent
- Préserver les liens existants qui marchent (pas de refonte aveugle)

---

## Rappels méthode

> "Le maillage interne, c'est un système, pas une passe."
> "5 liens entrants vers la même page = 5 ancres différentes. Un seul exact match."
> "Test à voix haute : si la phrase tombe juste sans le lien, l'ancre est bonne."
> "Une page Know doit toujours pointer vers une page Do."
> "Pas de Voir aussi. Liens in-body uniquement."
> "Un hub n'est pas une catégorie. C'est l'article le plus stratégique du pilier."
> "Le contexte des 5 mots avant/après l'ancre vaut plus que l'ancre elle-même."
