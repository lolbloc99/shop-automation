# Boutique — règles permanentes (lues à chaque session)

> Marque de référence : **Oria Studio** (https://oriastudio.store/). Mode femme FR, essentiels élevés.
> Principe directeur : **la machine prépare tout, l'humain valide ce qui engage de l'argent**
> (mise en ligne Shopify, budget pub). **Phase actuelle : 1 (rodage).**

## Plateforme & import
- Plateforme : **Shopify**.
- Format d'import CSV (en-têtes EXACTS — nouveau format Shopify, une ligne par variante) :
  ```
  Title,URL handle,Description,Vendor,Product category,Type,Tags,Published on online store,Status,SKU,Barcode,Option1 name,Option1 value,Option1 Linked To,Option2 name,Option2 value,Option2 Linked To,Option3 name,Option3 value,Option3 Linked To,Price,Compare-at price,Cost per item,Charge tax,Tax code,Unit price total measure,Unit price total measure unit,Unit price base measure,Unit price base measure unit,Inventory tracker,Inventory quantity,Continue selling when out of stock,Weight value (grams),Weight unit for display,Requires shipping,Fulfillment service,Product image URL,Image position,Image alt text,Variant image URL,Gift card,SEO title,SEO description,Color (product.metafields.shopify.color-pattern),Google Shopping / Google product category,Google Shopping / Gender,Google Shopping / Age group,Google Shopping / Manufacturer part number (MPN),Google Shopping / Ad group name,Google Shopping / Ads labels,Google Shopping / Condition,Google Shopping / Custom product,Google Shopping / Custom label 0,Google Shopping / Custom label 1,Google Shopping / Custom label 2,Google Shopping / Custom label 3,Google Shopping / Custom label 4
  ```
- Granularité : **1re ligne = produit complet** ; lignes suivantes = variantes (`URL handle` + `SKU` + `Option* value` + `Price`/`Compare-at price` répétés, autres colonnes vides).
- Couleurs : colonne `Color (product.metafields.shopify.color-pattern)` = liste séparée par `; ` sur la 1re ligne.

## Concurrents
- Surveillés via `concurrents.txt` (1 URL/ligne + plateforme).
- Test initial : **https://wijzijnvengee.nl/** (Shopify, NL, EUR).
- Méthode privilégiée : si Shopify → endpoint `/products.json` (structuré, propre). Fallback HTML + collage manuel.

## Voix de marque (déduite d'Oria Studio)
- Langue : **Français uniquement**.
- Ton : élevé, sensoriel, rassurant, body-positive, intemporel. Vend le ressenti et la durabilité, pas le hype.
- Longueur description : **70–110 mots**.
- Structure description imposée :
  1. Accroche 1 ligne (ex. « La chemise qui fait tout le travail »).
  2. 1–2 phrases de lead.
  3. 3 sous-titres en gras : **section matière**, **section coupe**, et TOUJOURS **« Le bon geste d'entretien »** (instructions lavage).
  4. (optionnel) « Guide des tailles ».
- Pas d'emoji. Prose sous les sous-titres, pas de listes à puces.
- Titre produit : `[Vêtement] [coupe/style] en [matière]`, minuscule après le 1er mot, 4–6 mots, **sans couleur ni SKU**. Ex. « Chemise oversize en coton ».
- À privilégier : « Livraison offerte », « Retour gratuit », « Support Français », « Nous célébrons chaque corps », « Conception intentionnelle ».
- À ÉVITER (claims à risque) : origine non prouvée (« Fabriqué en France »), % de fibres précis non vérifié, allégations santé.

## Prix
- Devise : **EUR**.
- Règle : `prix_vente = prix_concurrent` (**identique**, multiplicateur 1.0, sans arrondi forcé).
- **Prix avant réduction (`Compare-at price`) : OBLIGATOIRE** (le barré fait partie de l'identité Oria, ~45–50 % affiché).
  - Stratégie par défaut `concurrent` : si le concurrent expose un `compare_at_price` réel → le reprendre ×1.4 arrondi .99.
  - Sinon `markup` : ancre = `prix_vente / (1 − remise_affichee)`, `remise_affichee = 0.45`.
- ⚠️ **Légal FR** : un prix barré permanent inventé viole la règle « prix de référence » (Directive Omnibus / Code conso : référence = plus bas prix pratiqué sur 30 j). Préférer `strategie=concurrent` ; ne pas fabriquer de fausse remise permanente.

## Variantes
- Tailles **vêtements** : XS, S, M, L, XL, XXL, XXXL (2XL→XXL, 3XL→XXXL).
- Tailles **chaussures** : 34 à 45.
- Référentiel choisi selon la catégorie produit (vêtement vs chaussure) détectée chez le concurrent.
- Couleurs : reprises du concurrent, **normalisées en français** (mapping dans `config.yaml`). Ex. Blauw/Blue → Bleu, Zwart/Black → Noir.

## Images — via MCP Higgsfield (BLOC 2 — NE PAS générer en phase config)
- **RÈGLE DURE — AUCUN logo, AUCUN texte, AUCUN watermark sur les images générées.**
  - Prompt négatif systématique : `no text, no logo, no watermark, no typography, no letters`.
  - Éviter `soul_2` (injecte texte/watermark). Modèle pressenti `recraft-v4-1` (respecte le « no text »).
  - Contrôle qualité BLOC 2 : toute image suspectée de contenir logo/texte → **rejetée**, placée en `output/a_valider/` avec mention, jamais poussée automatiquement.
- Style (choix Lucas) : **mannequin femme portant le vêtement**, met en valeur le produit (lifestyle / studio), PNG. Pas de packshot vide.
- Dimensions : 1024×1024 (fiche) + **1:1 (1080×1080) pour les ads** (Advantage+ adapte à tous les placements ; pas de 4:5/9:16 en auto).
- 1 image/produit (+1 par couleur si plusieurs coloris).

## Facebook Ads — via MCP Meta Ads (BLOC 3 — RIEN créé/activé en phase 1)
- **3 règles immuables (Lucas)** :
  1. Objectif **OUTCOME_SALES** + pixel **PURCHASE** systématiques.
  2. **Visuel 1:1 unique** : Advantage+ placements le recadre sur tous les feeds/placements. (Le MCP Meta ne sait pas uploader d'images ni gérer `asset_feed_spec` → pas de 4:5/9:16 natifs en auto ; à faire à la main si besoin.)
  3. **3-5 variations** : bodies (primary texts) + titles (headlines) + descriptions.
- Compte publicitaire / Page FB / IG / pixel : `[récupérés via MCP Meta au moment de créer]`.
- Budget de test par produit : 10 €/jour (défaut).
- Audience par défaut : femmes FR, 25-65+ (age_max=65), large/advantage+ (à confirmer).
- Campagne TOUJOURS créée en **PAUSED**. Activation = action humaine (phases 1 et 2).
- Texte d'accroche dans la voix de marque Oria. Claims interdits = mêmes que la voix de marque.

## Seuils ads (BLOC 4)
- Couper : dépense ≥ 2 × CPA cible ET 0 vente.
- Scaler : +20 %/jour si ROAS ≥ 2 sur 3 jours.
- Fenêtre d'apprentissage : 3 jours / ~15 €/jour avant tout jugement.
- CPA cible : **15 €** (à confirmer, dépend de la marge réelle).
- Surveiller : ROAS 1.5-2 = laisser tourner ; CTR < 1 % = créative à retravailler.

## Règle absolue (droit d'auteur)
La data concurrente (textes, images) sert **UNIQUEMENT** de référence pour générer mes propres contenus. **Jamais réutilisée telle quelle.**

## Garde-fous phase 1 (rodage)
- **Aucune** image Higgsfield générée, **aucun** push Shopify, **aucune** création/activation d'ads sans OK explicite de Lucas.
- Tout ce qui engage de l'argent ou met en ligne → déposé dans `output/a_valider/` + notification.
- Chaque run journalisé dans `logs/`. Mode `--dry-run` partout.
