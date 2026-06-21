# ROUTINE QUOTIDIENNE — shop-automation (full auto)

> Lancée chaque matin **9h03** par un cron Claude Code. Exécute TOUT sans demander de
> validation, mais respecte les garde-fous. **Si un connecteur MCP (Shopify / Meta /
> Higgsfield) est absent ou échoue → STOP, ne rien créer à moitié, signaler lequel manque.**

## 0. Setup
- `cd '/Users/lucas/Desktop/dossier sans titre/shop-automation'` puis `git pull`.
- Lis `CLAUDE.md` + `config.yaml` → règles à respecter À LA LETTRE.

## 1. Ré-arme la routine de demain — FAIS-LE MAINTENANT (avant le travail)
Les crons récurrents expirent après 7 jours. Pour éviter ça, à CHAQUE run :
1. `CronList` → repère les jobs dont le prompt mentionne `ROUTINE.md`.
2. `CronDelete` ces jobs.
3. `CronCreate` avec :
   - cron `3 9 * * *`, `durable: true`, `recurring: true`
   - prompt : `Exécute intégralement /Users/lucas/Desktop/dossier sans titre/shop-automation/ROUTINE.md (routine quotidienne shop-automation, full auto).`

→ La fenêtre 7 jours se réinitialise chaque jour ; il reste toujours 1 seul job.

## 2. Veille (BLOC 1)
- `python3 -m veille.run` → met à jour `data/vus.json` + `data/nouveaux.json`
  (nouveaux produits concurrents ≥ 29,99 €).
- Si `nb_nouveaux == 0` : `git add data/ && git commit -m "veille: rien de neuf" && git push`, puis STOP.

## 3. Pour CHAQUE nouveau produit de `data/nouveaux.json`

### a. Fiche (voix Oria, FR)
- Titre `[vêtement] [coupe]` ; desc 70-110 mots (accroche + section matière + section coupe +
  **« Le bon geste d'entretien »**) + ligne fit **« Mannequin : 1m76, porte une taille S »**.
- Prix = prix concurrent. **PAS de prix barré** (Directive Omnibus). Tailles XS-XXXL
  (chaussures 34-45). Couleurs mappées FR.

### b. Images — Higgsfield `gpt_image_2`
- `media_import_url` de l'image produit concurrent → **référence**.
- **Hero** (quality `medium`) : mannequin DIFFÉRENT du concurrent, **face plein pied**, fond
  studio clair, GARDE le vêtement (coupe + couleur). Transformatif (pas un clone de leur photo).
- **Recolors** (quality `low`) : 1 par couleur, en réutilisant le hero comme référence
  (même mannequin/pose, seule la couleur change).
- **+ 1 vue de dos** (couleur principale seulement).
- QC : rejeter toute image avec logo / texte / watermark.

### c. Shopify (MCP)
- `create-product` : status `ACTIVE`, vendor `Oria Studio`, variants couleur×taille FR,
  `inventoryItem.tracked = false`.
- `publishablePublish` sur publication **Boutique en ligne** `348749201740`.
- `productVariantAppendMedia` : chaque image couleur → ses variantes.
- `metafieldsSet` : `custom.capsule` / `matiere` / `entretien` / `coupe`
  (**`coupe` = single_line_text_field** ; matiere/entretien = multi_line).
- Tag capsule (`intemporel` → collection Essentiels).

### d. Ads (MCP Meta) — structure ABO
- Ajoute **+1 adset** à la campagne ABO existante **`Oria | TEST Fashion` = `120249947032740725`**.
- Compte `962375839333565`, page `1108378915699122`, pixel `3023048557869065` event `PURCHASE`.
- Adset : `optimization_goal OFFSITE_CONVERSIONS`, `destination_type WEBSITE`,
  `billing_event IMPRESSIONS`, `daily_budget 2000` ($20/j), targeting `{FR, genders:[2], 25-65}`,
  `start_time` = **DEMAIN 00:01 fuseau Europe/Paris**, `dsa_beneficiary`+`dsa_payor` = `Oria Studio`.
- Créative : image **hero (face)**, link produit, CTA `SHOP_NOW`, message voix Oria.
- Crée l'ad → **active** campagne + adset + ad (ACTIVE).

## 4. Clôture
- `git add data/ && git commit -m "routine: <N> produits traités" && git push`.
- Récap : produits créés (liens storefront), adsets créés (IDs), dépense/jour ajoutée (= N × 20 $).

## Garde-fous stricts
- Aucun **prix barré** ; images **zéro logo/texte/watermark** ; data concurrente = **référence
  only** (jamais republiée telle quelle) ; produit **< 29,99 €** ignoré.
- **Connecteur MCP absent/échec → STOP**, ne rien créer à moitié, signaler lequel manque.
