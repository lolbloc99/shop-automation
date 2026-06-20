# Refonte Oria Studio — Plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task.
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconstruire oriastudio.store en thème Shopify OS2 quiet luxury, structuré en
capsules, alimentable par le système d'automatisation.

**Architecture:** Fork de **Dawn** (OS2, gratuit) customisé. L'identité passe par les
*color schemes* + typo + un CSS custom (`assets/oria.css`). Les capsules sont des
**collections** ; les contenus PDP/capsule viennent de **métafields**. La home réutilise
les sections Dawn configurées (image-banner, featured-collection, rich-text, newsletter)
+ identité.

**Tech Stack:** Shopify OS2, thème Dawn, Liquid, Shopify CLI, métafields, Fraunces + Inter.

**Note "tests":** un thème Liquid n'a pas de tests unitaires. La porte de validation de
chaque tâche = `shopify theme check` (lint) + rendu **preview** (`shopify theme dev`) +
Lighthouse mobile sur les pages clés. Commits fréquents.

**Spec de référence :** [docs/2026-06-20-refonte-oria-studio-design.md](2026-06-20-refonte-oria-studio-design.md).

---

## Pré-requis (à faire une fois)
- Shopify CLI installé (`shopify version`).
- Accès thème au store (CLI OAuth ou Theme Access password) — **sans Payments**.
- Domaine myshopify du store (pour `--store`). Le custom domain est oriastudio.store.

---

## Phase 0 — Environnement & base thème

### Task 0.1 : Installer le CLI et s'authentifier
**Files:** aucun (env).
- [ ] **Step 1 :** installer le CLI.
  Run: `npm install -g @shopify/cli @shopify/theme`
  Expected: `shopify version` affiche une version ≥ 3.x.
- [ ] **Step 2 :** vérifier l'accès store.
  Run: `shopify theme list --store <store>.myshopify.com`
  Expected: liste des thèmes du store (auth OK).

### Task 0.2 : Forker Dawn dans `oria-theme/`
**Files:** Create: `oria-theme/` (squelette Dawn).
- [ ] **Step 1 :** init depuis Dawn.
  Run: `shopify theme init oria-theme` (clone Dawn par défaut)
  Expected: dossier `oria-theme/` avec `sections/`, `templates/`, `config/`, `assets/`.
- [ ] **Step 2 :** init git du thème.
  Run: `cd oria-theme && git init && git add -A && git commit -m "chore: fork Dawn baseline"`
  Expected: commit baseline.

### Task 0.3 : Baseline lint + preview
**Files:** aucun.
- [ ] **Step 1 :** lint.
  Run: `shopify theme check`
  Expected: 0 erreur (warnings Dawn tolérés).
- [ ] **Step 2 :** preview live.
  Run: `shopify theme dev --store <store>.myshopify.com`
  Expected: URL de preview locale qui rend Dawn par défaut.

---

## Phase 1 — Identité (design tokens)

### Task 1.1 : Color scheme quiet luxury
**Files:** Modify: `oria-theme/config/settings_data.json` (bloc `color_schemes`).
- [ ] **Step 1 :** définir le schéma « Papier » (par défaut) et « Encre » (inversé).
```json
"scheme-papier": {
  "settings": {
    "background": "#F5F2EC",
    "background_gradient": "",
    "text": "#2A2622",
    "button": "#2A2622",
    "button_label": "#F5F2EC",
    "secondary_button_label": "#2A2622",
    "shadow": "#A89A87"
  }
},
"scheme-encre": {
  "settings": {
    "background": "#2A2622",
    "text": "#F5F2EC",
    "button": "#F5F2EC",
    "button_label": "#2A2622",
    "secondary_button_label": "#F5F2EC",
    "shadow": "#000000"
  }
}
```
- [ ] **Step 2 :** vérifier en preview que fond = Papier, texte/boutons = Encre.
  Expected: la home prend les tons neutres chauds.
- [ ] **Step 3 :** commit. `git commit -am "feat(identity): color schemes papier + encre"`

### Task 1.2 : Typographie Fraunces + Inter
**Files:** Modify: `oria-theme/config/settings_data.json` (typo) ; Create: `oria-theme/assets/oria-fonts.css`.
- [ ] **Step 1 :** charger les fonts Google (titres Fraunces, texte Inter) via `assets/oria-fonts.css`.
```css
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500&family=Inter:wght@400;500&display=swap');
:root{
  --font-heading: 'Fraunces', Georgia, serif;
  --font-body: 'Inter', system-ui, sans-serif;
}
h1,h2,h3,.h1,.h2,.h3{ font-family: var(--font-heading); font-weight:400; letter-spacing:-0.01em; }
body{ font-family: var(--font-body); }
.caps-label{ text-transform:uppercase; letter-spacing:.18em; font-size:.72rem; }
```
- [ ] **Step 2 :** inclure le CSS dans `layout/theme.liquid` (`{{ 'oria-fonts.css' | asset_url | stylesheet_tag }}`).
- [ ] **Step 3 :** preview → titres en serif, texte en Inter, labels en caps espacées.
- [ ] **Step 4 :** commit. `git commit -am "feat(identity): typographie Fraunces + Inter"`

### Task 1.3 : Logo wordmark
**Files:** admin (upload) + Modify: header settings.
- [ ] **Step 1 :** générer/poser le wordmark « ORIA STUDIO » (serif espacé, Encre + version inversée). Upload dans Réglages → thème → logo.
- [ ] **Step 2 :** régler la hauteur + centrage dans le header (section header settings).
- [ ] **Step 3 :** preview header → wordmark net, lisible, espacé. Commit settings.

### Task 1.4 : CSS d'identité (boutons, espacements)
**Files:** Create: `oria-theme/assets/oria.css` ; Modify: `layout/theme.liquid`.
- [ ] **Step 1 :** styles boutons Encre + générosité d'espace.
```css
.button, .shopify-payment-button__button--unbranded{
  background: var(--color-button, #2A2622); color:#F5F2EC;
  border-radius: 0; letter-spacing:.04em; padding:14px 28px; font-weight:500;
}
.section{ padding-block: clamp(48px, 8vw, 96px); }
.product__title h1{ font-size: clamp(1.6rem, 3vw, 2.2rem); }
img{ border-radius:0; }
```
- [ ] **Step 2 :** inclure `oria.css` dans le layout.
- [ ] **Step 3 :** preview → boutons noir chaud, coins droits, sections aérées. Lint + commit.

---

## Phase 2 — Métafields (structure capsules + PDP)

### Task 2.1 : Métafields collection (capsules)
**Files:** admin Réglages → Données personnalisées → Collections (ou API).
- [ ] **Step 1 :** créer les définitions :
  - `custom.statut` (single line text ; valeurs `en_cours` / `archivee`)
  - `custom.image_hero` (file/image)
  - `custom.manifeste` (multi-line text)
  - `custom.ordre` (integer)
- [ ] **Step 2 :** vérifier qu'elles apparaissent sur l'éditeur de collection. Pas de commit (config admin).

### Task 2.2 : Métafields produit (PDP)
**Files:** admin Réglages → Données personnalisées → Produits (ou API).
- [ ] **Step 1 :** créer :
  - `custom.matiere` (multi-line text)
  - `custom.entretien` (multi-line text)
  - `custom.coupe` (single line text)
  - `custom.capsule` (single line text — slug de la capsule)
- [ ] **Step 2 :** renseigner ces métafields sur le produit test (robe-chemise) pour les essais PDP.

---

## Phase 3 — Home (sections Dawn configurées + identité)

### Task 3.1 : Barre d'annonce sobre
**Files:** Modify: `oria-theme/sections/header.liquid` (announcement) ou section announcement-bar.
- [ ] **Step 1 :** texte « Livraison offerte · Retours gratuits », fond Papier, texte Encre, **pas** de compteur.
- [ ] **Step 2 :** preview → barre fine, discrète. Commit.

### Task 3.2 : Hero éditorial (section `image-banner`)
**Files:** Modify: `oria-theme/templates/index.json` (ajout image-banner).
- [ ] **Step 1 :** ajouter une section `image-banner` : image plein écran, hauteur large, 1 titre serif court, 1 bouton (« Découvrir la capsule »), overlay léger.
```json
"hero": {
  "type": "image-banner",
  "settings": { "image_height": "large", "show_text_box": true,
    "image_overlay_opacity": 10, "color_scheme": "scheme-papier" },
  "blocks": {
    "h": { "type":"heading", "settings": { "heading":"Le vestiaire essentiel" } },
    "b": { "type":"buttons", "settings": { "button_label_1":"Découvrir la capsule" } }
  }, "block_order": ["h","b"]
}
```
- [ ] **Step 2 :** preview → hero épuré, image grande, 1 CTA. Commit.

### Task 3.3 : Capsule du moment (section `featured-collection`)
**Files:** Modify: `oria-theme/templates/index.json`.
- [ ] **Step 1 :** `featured-collection` pointant la collection `statut=en_cours`, 4 produits, titre « La capsule du moment », lien « Voir la capsule ».
- [ ] **Step 2 :** preview → 3-4 pièces héros. Commit.

### Task 3.4 : Manifeste (section `rich-text`)
**Files:** Modify: `oria-theme/templates/index.json`.
- [ ] **Step 1 :** `rich-text` : 2-3 lignes voix de marque (conception intentionnelle, matières, intemporel), fond Sable.
- [ ] **Step 2 :** preview + commit.

### Task 3.5 : Les essentiels (section `featured-collection`)
**Files:** Modify: `oria-theme/templates/index.json`.
- [ ] **Step 1 :** `featured-collection` « Les essentiels » (collection sélection), 4-6 produits.
- [ ] **Step 2 :** preview + commit.

### Task 3.6 : Réassurance (section `multicolumn`)
**Files:** Modify: `oria-theme/templates/index.json`.
- [ ] **Step 1 :** `multicolumn` 4 items texte fin : Livraison offerte · Retours gratuits · Paiement sécurisé · Support FR. Icônes fines ou pas d'icône.
- [ ] **Step 2 :** preview + commit.

### Task 3.7 : Accès prioritaire aux drops (newsletter)
**Files:** Modify: `oria-theme/templates/index.json` (section `newsletter`).
- [ ] **Step 1 :** `newsletter` : titre « Accès prioritaire aux drops », sous-texte « Ventes privées et avant-premières de capsules », champ email.
- [ ] **Step 2 :** preview → capture email sobre. Commit.

### Task 3.8 : Footer sobre
**Files:** Modify: `oria-theme/sections/footer.liquid` (settings).
- [ ] **Step 1 :** colonnes : Capsules · Aide · Légal · Réseaux. Typo fine, fond Papier ou Encre.
- [ ] **Step 2 :** preview + commit.

---

## Phase 4 — Gabarits PDP & collection

### Task 4.1 : PDP — colonne achat + accordéons métafields
**Files:** Modify: `oria-theme/sections/main-product.liquid` ; `oria-theme/templates/product.json`.
- [ ] **Step 1 :** label capsule au-dessus du titre (lit `product.metafields.custom.capsule`).
```liquid
{% if product.metafields.custom.capsule %}
  <p class="caps-label">Capsule · {{ product.metafields.custom.capsule }}</p>
{% endif %}
```
- [ ] **Step 2 :** accordéons (collapsible-tab blocks) reliés aux métafields :
  - « Détails & matière » → `product.metafields.custom.matiere`
  - « Le bon geste d'entretien » → `product.metafields.custom.entretien`
  - « Livraison & retours » → page statique
- [ ] **Step 3 :** prix : pas de barré sauf si `compare_at_price` > `price` (promo réelle). Garder le bloc prix Dawn (gère déjà compare-at).
- [ ] **Step 4 :** preview PDP du produit test → galerie gauche, colonne sobre, accordéons fermés. Lint + commit.

### Task 4.2 : PDP — storytelling + « compléter la capsule »
**Files:** Modify: `oria-theme/templates/product.json` (ajout sections).
- [ ] **Step 1 :** section `rich-text` ou `image-with-text` « Storytelling matière & entretien » (grande image + texte).
- [ ] **Step 2 :** section `related-products` configurée pour afficher la **même collection-capsule** (via tag/metafield) plutôt que reco générique.
- [ ] **Step 3 :** preview + commit.

### Task 4.3 : Page collection (capsule)
**Files:** Modify: `oria-theme/sections/main-collection-banner.liquid` ; `templates/collection.json`.
- [ ] **Step 1 :** bannière capsule : `collection.metafields.custom.image_hero` + nom + `collection.metafields.custom.manifeste`.
- [ ] **Step 2 :** grille sobre (2 col mobile / 3-4 desktop), beaucoup de blanc, filtres discrets si volume.
- [ ] **Step 3 :** preview sur une collection test + commit.

---

## Phase 5 — Migration des produits existants

### Task 5.1 : Taguer en capsules + remplir métafields
**Files:** script (via MCP Shopify / Admin API) ou admin.
- [ ] **Step 1 :** définir les capsules initiales (ex. « Denim », « Maille »). Créer les collections + métafields (`statut`, `image_hero`, `manifeste`).
- [ ] **Step 2 :** pour chaque produit existant : set `custom.capsule`, `custom.matiere`, `custom.entretien`, `custom.coupe` ; ajouter à la bonne collection.
- [ ] **Step 3 :** vérifier la PDP d'un produit migré (accordéons remplis).

### Task 5.2 : Visuels mannequin + descriptions raffinées
**Files:** flux Higgsfield (validé) + MCP Shopify (`update-product`).
- [ ] **Step 1 :** générer/poser des visuels **mannequin porté** (sans logo/texte) pour chaque produit migré.
- [ ] **Step 2 :** réécrire les descriptions dans la voix raffinée (accroche + matière + coupe + entretien).
- [ ] **Step 3 :** mise à jour produit via MCP ; vérifier rendu. (Mise en ligne = validée à la main.)

---

## Phase 6 — Marketing (offres hybrides, conforme)

### Task 6.1 : Capture email opérationnelle
**Files:** admin (Shopify Forms / Klaviyo) + section newsletter (déjà posée 3.7).
- [ ] **Step 1 :** connecter la liste (Shopify Email ou Klaviyo). Tag « drops ».
- [ ] **Step 2 :** email de bienvenue « accès prioritaire aux drops ».

### Task 6.2 : Mécanique d'offres conforme
**Files:** admin (réductions) + garde-fou thème.
- [ ] **Step 1 :** offres = **codes / ventes privées time-boxées** envoyés par email. Pas de barré permanent.
- [ ] **Step 2 :** si `compare_at_price` utilisé : ce doit être un **vrai prix de référence** (plus bas prix 30 j, Directive Omnibus). Documenter la règle dans l'admin.

---

## Phase 7 — QA & mise en ligne

### Task 7.1 : Lint + perf
- [ ] **Step 1 :** `shopify theme check` → 0 erreur.
- [ ] **Step 2 :** Lighthouse mobile sur home + PDP → LCP < 2,5 s, CLS < 0,1.

### Task 7.2 : Conformité & légal
- [ ] **Step 1 :** vérifier pages légales FR (CGV, mentions, RGPD, rétractation) présentes et à jour.
- [ ] **Step 2 :** vérifier aucun faux avis, aucun barré permanent, aucune fausse urgence.

### Task 7.3 : Revue preview + publication
- [ ] **Step 1 :** `shopify theme push --unpublished` → thème en preview non publié.
- [ ] **Step 2 :** Lucas relit le preview (mobile + desktop).
- [ ] **Step 3 :** publication **validée à la main** par Lucas (`shopify theme publish` ou bouton admin).

---

## Hors périmètre (YAGNI)
Headless, checkout custom, fidélité, multi-langue, blog, wishlist.

## Couverture spec (self-review)
- §2 positionnement → Phase 1 (identité) + 6 (marketing).
- §3 identité → Phase 1.
- §4 home → Phase 3.
- §5 capsules → Phase 2 (métafields) + 3.3 + 4.3 + 5.1.
- §6 PDP → Phase 4.1/4.2.
- §7 collection → Phase 4.3.
- §8 marketing → Phase 6 + garde-fou prix (4.1, 6.2).
- §9 technique → Phases 0-4.
- §10 migration → Phase 5.
- §11 phasing → ordre des phases.
- §13 succès → Phase 7.
