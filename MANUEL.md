# MANUEL — Production produit À LA DEMANDE (shop-automation)

> **Déclencheur** : Lucas donne une **URL produit concurrent** + dit "lance".
> **Mode** : **CHECKPOINT PRODUIT** (choix Lucas 2026-06-21) — créer produit + images, Lucas
> **valide les images dans Shopify**, PUIS (sur son "OK") lancer les ads pour **J+1**.
> Mêmes garde-fous que `ROUTINE.md`. Complète l'auto (veille 9h03) — ici c'est Lucas qui source.

## 0. Setup
- `cd '/Users/lucas/Desktop/dossier sans titre/shop-automation'` puis `git pull`.
- Lis `CLAUDE.md` + `config.yaml` (règles à respecter à la lettre).
- Connecteur MCP (Shopify / Meta / Higgsfield) absent → **STOP**, signaler lequel.

## 1. Récupérer le produit depuis l'URL
- Déduire **domaine + handle** de l'URL.
- Scraper la fiche source : `https://<domaine>/products/<handle>.json` (titre, variantes,
  couleurs, prix, images). Fallback : `/products.json` paginé, sinon scrape HTML.
- **Filtre CLONABILITÉ (a0)** : skip si marque/logo (`clonabilite.marques_blocklist`) ou si l'image
  source porte un logo ; skip si prix **< 29,99 €** (`prix.prix_min_eur`).
- **Marquer l'URL dans `data/vus.json`** → la veille auto ne le re-traitera pas (anti-doublon).

## 2. Fiche + images (BLOC 2) — voir `ROUTINE.md` §3a / §3b
- **Fiche** voix Oria FR : titre `[vêtement] [coupe]`, desc 70-110 mots (accroche + matière +
  coupe + **« Le bon geste d'entretien »**) + ligne fit **« Mannequin : 1m76, porte une taille S »**.
- **Prix = prix concurrent** (≥ 29,99 €). **PAS de prix barré** (Omnibus). Tailles XS-XXXL, couleurs FR.
- **Images Higgsfield `gpt_image_2`** : `media_import_url` de l'image concurrent → **référence** ;
  **hero** face plein-pied (mannequin DIFFÉRENT, transformatif) ; **recolor** par couleur ;
  **+1 vue de dos** (couleur principale) ; QC = rejet si logo/texte/watermark.

## 3. Produit Shopify (BLOC 3) — créé ACTIVE
- `create-product` : status `ACTIVE`, vendor `Oria Studio`, variantes couleur×taille FR,
  `inventoryItem.tracked = false`.
- `publishablePublish` sur **Boutique en ligne `348749201740`**.
- `productVariantAppendMedia` (image couleur → ses variantes) ; `metafieldsSet`
  (`custom.capsule` / `matiere` / `entretien` / `coupe` — **coupe = single_line_text_field**).

## 4. ⏸ CHECKPOINT — STOP ICI (ne PAS créer les ads)
- Donner à Lucas le **lien storefront + admin** du produit.
- Message : « Produit + images créés. **Valide les images dans Shopify** → dis **OK** pour lancer
  les ads J+1, ou demande une regénération. »
- **Attendre le "OK" de Lucas.** Tant qu'il n'a pas validé → aucune dépense pub.

## 5. Sur "OK" de Lucas → Ads (BLOC 3) — ABO, lancement J+1
- **+1 adset** à la campagne ABO **`Oria | TEST Fashion` = `120249947032740725`**.
- Compte `ads.compte_publicitaire`, **page `ads.page_fb`**, pixel `ads.pixel_id` event `PURCHASE`
  (valeurs dans `config.yaml` — la page FB peut changer après suspension).
- Adset : `OFFSITE_CONVERSIONS`, `destination_type WEBSITE`, `daily_budget 2000` ($20/j),
  cible `{FR, genders:[2], 25-65}`, **`start_time` = J+1 00:01 Europe/Paris**, dsa = `Oria Studio`.
- Créative : image **hero (face)**, lien produit, CTA `SHOP_NOW`, message voix Oria.
- Crée l'ad → **active** campagne + adset + ad (ACTIVE, démarre seule à J+1 00:01).
- **Ad-spy optionnel** : caler l'angle/copy sur les créatives gagnantes de `brands_adspy.txt`
  (`get_brand_ads(brand, sort=spend)`) — ces marques sont spy-only, jamais clonées.

## 6. Clôture
- `git add data/ && git commit -m "manuel: <produit> créé + ads J+1" && git push`.
- Récap : lien produit, adset id, dépense/jour ajoutée (= 20 $).

## Garde-fous (identiques ROUTINE.md)
- Aucun **prix barré** ; images **zéro logo/texte/watermark** ; produit **< 29,99 €** ignoré ;
  data concurrente = **référence only** (jamais republiée telle quelle) ; clone **logo-free** uniquement.
- Connecteur MCP absent/échec → **STOP**, ne rien créer à moitié.
