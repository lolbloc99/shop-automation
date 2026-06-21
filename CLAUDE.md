# Boutique — règles permanentes (lues à chaque session)

> Marque de référence : **Oria Studio** (https://oriastudio.store/). Mode femme FR, essentiels élevés.
> Principe directeur : **la machine prépare tout, l'humain valide ce qui engage de l'argent**
> (mise en ligne Shopify, budget pub). **Phase actuelle : 1 (rodage).**

## Direction de marque & structure (refonte 2026-06-20)
- **Spec complète : [docs/2026-06-20-refonte-oria-studio-design.md](docs/2026-06-20-refonte-oria-studio-design.md)** — source de vérité de la structure boutique. Toute génération de page produit/collection DOIT la suivre.
- DA : **quiet luxury minimaliste** (neutres chauds Papier/Sable/Taupe/Moka/Encre, serif Fraunces + sans Inter, wordmark espacé).
- Catalogue en **capsules/drops** (1 capsule = 1 collection). Prix **premium accessible** (~40-70€).
- Marketing **hybride** : premium sobre + offres ponctuelles par email. **Aucun prix barré permanent.**
- PDP : galerie éditoriale + colonne sobre, accordéons (matière/entretien/livraison via métafields), reco « compléter la capsule ».

## Plateforme & création produit
- Plateforme : **Shopify** (MCP connecté à oriastudio.store).
- **Création produit = directe via MCP Shopify** (`productCreate` / graphql), statut **ACTIVE + publié sur la Boutique en ligne** (choix Lucas 2026-06-20). **Plus d'import CSV manuel.**
- **Flux autonome (phase 2)** : fiche voix Oria → image mannequin (sans logo/texte) → `productCreate` (active + publié + image principale) → récup du **lien produit** → tag capsule + métafields (`custom.capsule/matiere/entretien/coupe`) → **ad Meta en PAUSED** (MCP). **Seule action humaine : activer l'ad** (ça engage le budget).
- **CSV = export de secours** (format ci-dessous), utilisé seulement si le MCP est indisponible.
- Format CSV (en-têtes EXACTS — nouveau format Shopify, une ligne par variante) :
  ```
  Title,URL handle,Description,Vendor,Product category,Type,Tags,Published on online store,Status,SKU,Barcode,Option1 name,Option1 value,Option1 Linked To,Option2 name,Option2 value,Option2 Linked To,Option3 name,Option3 value,Option3 Linked To,Price,Compare-at price,Cost per item,Charge tax,Tax code,Unit price total measure,Unit price total measure unit,Unit price base measure,Unit price base measure unit,Inventory tracker,Inventory quantity,Continue selling when out of stock,Weight value (grams),Weight unit for display,Requires shipping,Fulfillment service,Product image URL,Image position,Image alt text,Variant image URL,Gift card,SEO title,SEO description,Color (product.metafields.shopify.color-pattern),Google Shopping / Google product category,Google Shopping / Gender,Google Shopping / Age group,Google Shopping / Manufacturer part number (MPN),Google Shopping / Ad group name,Google Shopping / Ads labels,Google Shopping / Condition,Google Shopping / Custom product,Google Shopping / Custom label 0,Google Shopping / Custom label 1,Google Shopping / Custom label 2,Google Shopping / Custom label 3,Google Shopping / Custom label 4
  ```
- Granularité : **1re ligne = produit complet** ; lignes suivantes = variantes (`URL handle` + `SKU` + `Option* value` + `Price`/`Compare-at price` répétés, autres colonnes vides).
- Couleurs : colonne `Color (product.metafields.shopify.color-pattern)` = liste séparée par `; ` sur la 1re ligne.

## Concurrents
- Surveillés via `concurrents.txt` (1 URL/ligne + plateforme).
- Test initial : **https://wijzijnvengee.nl/** (Shopify, NL, EUR).
- Méthode privilégiée : si Shopify → endpoint `/products.json` (structuré, propre). Fallback HTML + collage manuel.
- **Onboarding d'un nouveau concurrent (RÈGLE)** : ajouter l'URL dans `concurrents.txt` suffit. Au **1er passage**, tout son catalogue d'arrivée est **baseliné** = marqué « vu » dans `vus.json` **sans être traité** (on ne crée PAS les centaines de produits déjà en ligne, souvent plus trend). **Seuls ses drops FUTURS** (ajoutés après l'onboarding) sont traités. Logique dans `veille/diff.py` (un domaine est « connu » dès ≥1 produit en mémoire).
- **Garde anti-doublon / re-list** : un concurrent qui re-liste un produit lui donne un **nouvel id** mais garde la **même URL produit** (slug stable). La veille dédoublonne aussi sur l'**URL** → un re-list = **DOUBLON ignoré** (on ne recrée pas un produit déjà sur la boutique). Vu en réel 2026-06-21 (Veronica re-listée).

## Voix de marque (déduite d'Oria Studio)
- Langue : **Français uniquement**.
- Ton : élevé, sensoriel, rassurant, body-positive, intemporel. Vend le ressenti et la durabilité, pas le hype.
- Longueur description : **70–110 mots**.
- Structure description imposée :
  1. Accroche 1 ligne (ex. « La chemise qui fait tout le travail »).
  2. 1–2 phrases de lead.
  3. 3 sous-titres en gras : **section matière**, **section coupe**, et TOUJOURS **« Le bon geste d'entretien »** (instructions lavage).
  4. (optionnel) « Guide des tailles ».
  5. **Note mannequin (fit) — TOUJOURS** : « Mannequin : 1m76, porte une taille S » (rassure sur la coupe ; standard 1m76 / taille S).
- Pas d'emoji. Prose sous les sous-titres, pas de listes à puces.
- Titre produit : `[Vêtement] [coupe/style] en [matière]`, minuscule après le 1er mot, 4–6 mots, **sans couleur ni SKU**. Ex. « Chemise oversize en coton ».
- À privilégier : « Livraison offerte », « Retour gratuit », « Support Français », « Nous célébrons chaque corps », « Conception intentionnelle ».
- À ÉVITER (claims à risque) : origine non prouvée (« Fabriqué en France »), % de fibres précis non vérifié, allégations santé.

## Prix
- Devise : **EUR**.
- Règle : `prix_vente = prix_concurrent` (**identique**, multiplicateur 1.0, sans arrondi forcé).
- **Prix plancher : on ne traite/scrape AUCUN produit concurrent < 29,99 €** (`prix.prix_min_eur`). Filtré dès le BLOC 1 (veille).
- **Prix avant réduction (`Compare-at price`) : PAS de barré automatique.** Un prix de référence jamais pratiqué sur NOTRE boutique = illégal (Directive Omnibus FR : référence = plus bas prix pratiqué sur 30 j). Reprendre le barré du concurrent ne suffit pas — c'est NOTRE historique qui compte. **Bloqué par le classifier 2026-06-20.**
  - Barré autorisé **uniquement** pour une **vraie promo time-boxée** (le prix de départ a réellement été pratiqué ≥ 30 j), gérée manuellement.
  - Création autonome → `compare_at.actif=false`, prix plein.
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
- **Modèle = `gpt_image_2`** (text-guard, zéro texte/logo). recraft texte-seul abandonné (réinvente le vêtement → coupes différentes à chaque image).
- **PIPELINE RÉFÉRENCE (Lucas 2026-06-20)** : l'image produit **concurrent sert de RÉFÉRENCE** → on génère NOTRE version. On garde **uniquement le vêtement** (coupe + couleur) ; **mannequin + pose + fond DIFFÉRENTS** (sinon = quasi-copie de leur photo = droit d'auteur). Output = image originale, transformative.
- **Cadrage** : **face, plein pied, vêtement entièrement visible** (le concurrent shoote face plein pied — on réplique l'angle, pas la photo).
- **Consistance couleur** : 1 **hero** par produit → **recolor** par couleur (= même mannequin/pose, seule la couleur change). Chaque image couleur **affectée à sa variante** Shopify.
- **+ 1 vue de DOS** dans la galerie (**couleur principale seulement**, pas par couleur) — image commune. Indispensable pour les pièces à dos travaillé (ex. robe dos ouvert).

## Facebook Ads — via MCP Meta Ads (BLOC 3 — RIEN créé/activé en phase 1)
- **3 règles immuables (Lucas)** :
  1. Objectif **OUTCOME_SALES** + pixel **PURCHASE** systématiques.
  2. **Visuel 1:1 unique** : Advantage+ placements le recadre sur tous les feeds/placements. (Le MCP Meta ne sait pas uploader d'images ni gérer `asset_feed_spec` → pas de 4:5/9:16 natifs en auto ; à faire à la main si besoin.)
  3. **3-5 variations** : bodies (primary texts) + titles (headlines) + descriptions.
- Compte publicitaire / Page FB / IG / pixel : `[récupérés via MCP Meta au moment de créer]`.
- **Structure (Lucas 2026-06-20)** : **1 seule campagne `Oria | TEST Fashion` en ABO** ; chaque nouveau produit = **+1 adset** (budget 10 €/j à l'adset) + 1 ad. Pas une campagne par produit (CBO multi-produits affame les nouveaux). Les **winners** migrent plus tard vers une campagne **SCALE (CBO)** à gros budget.
- Budget de test par produit : **20 €/jour** (à l'adset, ABO) — 10 € jugé trop faible (Lucas 2026-06-20).
- Audience par défaut : femmes FR, 25-65+ (age_max=65), large/advantage+ (à confirmer).
- **Lancement AUTO** (choix Lucas 2026-06-20) : ad créée **ACTIVE** avec `start_time` = **J+1 à 00h01** (fuseau du compte / France) → démarre seule à 00h01 le lendemain. **Lève la règle « activation manuelle ».**
- **Garde-fous budget (car auto)** : budget test **20 €/j par adset** + **volume illimité** (1 adset/produit) + BLOC 4 surveille et recommande de couper. Toit dur = plafond de dépense compte Meta.
- Texte d'accroche dans la voix de marque Oria. Claims interdits = mêmes que la voix de marque.

## Seuils ads (BLOC 4)
- Couper : dépense ≥ 2 × CPA cible ET 0 vente.
- Scaler : +20 %/jour si ROAS ≥ 2 sur 3 jours.
- Fenêtre d'apprentissage : 3 jours / ~15 €/jour avant tout jugement.
- CPA cible : **15 €** (à confirmer, dépend de la marge réelle).
- Surveiller : ROAS 1.5-2 = laisser tourner ; CTR < 1 % = créative à retravailler.

## Règle absolue (droit d'auteur)
La data concurrente (textes, images) sert **UNIQUEMENT** de référence pour générer mes propres contenus. **Jamais réutilisée telle quelle.**
- **Image en référence = OK** pour capter la **forme du vêtement** (coupe/couleur), MAIS l'output doit être **transformatif** : mannequin, pose et fond **différents**. Un simple re-teintage de leur photo (même mannequin/pose) = quasi-copie = INTERDIT (vérifié 2026-06-20 : Nano Banana clonait, gpt_image_2 avec prompt "mannequin différent" = transformatif OK).

## Garde-fous (phase 2/3 — autonomie complète)
- **Bout en bout autonome** : image (sans logo/texte + QC) → produit Shopify active+publié → **ad Meta ACTIVE programmée J+1 00h01**. Aucun clic humain requis.
- **Volume : ILLIMITÉ** (choix Lucas 2026-06-20) — N nouveaux produits détectés → N produits créés + N images + **N ads** (1 ad/produit). Pas de cap de nombre.
- **Contrôle budget** :
  - budget test **20 €/j par adset** (seul plafond par adset) ;
  - ⚠ **dépense/jour = (nb produits détectés) × 20 €** (ex. 20 produits → 400 €/j) — assumé par Lucas ;
  - toit dur conseillé = **plafond de dépense au niveau du COMPTE Meta** (réglé côté Ads Manager) ;
  - BLOC 4 surveille les ads actives et **recommande de couper** ce qui brûle (auto-coupe possible en phase 3).
- Image : règle dure no logo / no texte / no watermark + QC (rejet si détecté).
- Chaque run journalisé dans `logs/`. CSV = export de secours uniquement.
