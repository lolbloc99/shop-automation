"""Export CSV au format EXACT Shopify (nouveau format, une ligne par variante).

Les en-têtes correspondent au copier-coller d'un export Shopify réel (voir
CLAUDE.md). 1re ligne = produit complet ; lignes suivantes = variantes (handle +
SKU + valeurs d'option + prix + inventaire ; noms d'option et champs produit vides).
"""

from __future__ import annotations

import csv
import os

from veille import utils

# En-têtes EXACTS (ordre = export Shopify fourni). NE PAS réordonner.
SHOPIFY_HEADERS = [
    "Title", "URL handle", "Description", "Vendor", "Product category", "Type",
    "Tags", "Published on online store", "Status", "SKU", "Barcode",
    "Option1 name", "Option1 value", "Option1 Linked To",
    "Option2 name", "Option2 value", "Option2 Linked To",
    "Option3 name", "Option3 value", "Option3 Linked To",
    "Price", "Compare-at price", "Cost per item", "Charge tax", "Tax code",
    "Unit price total measure", "Unit price total measure unit",
    "Unit price base measure", "Unit price base measure unit",
    "Inventory tracker", "Inventory quantity", "Continue selling when out of stock",
    "Weight value (grams)", "Weight unit for display", "Requires shipping",
    "Fulfillment service", "Product image URL", "Image position", "Image alt text",
    "Variant image URL", "Gift card", "SEO title", "SEO description",
    "Color (product.metafields.shopify.color-pattern)",
    "Google Shopping / Google product category", "Google Shopping / Gender",
    "Google Shopping / Age group", "Google Shopping / Manufacturer part number (MPN)",
    "Google Shopping / Ad group name", "Google Shopping / Ads labels",
    "Google Shopping / Condition", "Google Shopping / Custom product",
    "Google Shopping / Custom label 0", "Google Shopping / Custom label 1",
    "Google Shopping / Custom label 2", "Google Shopping / Custom label 3",
    "Google Shopping / Custom label 4",
]

VENDOR = "Oria Studio"


def _fmt(montant) -> str:
    return f"{montant:.2f}" if montant is not None else ""


def build_rows(contenu: dict, variantes: list, dry_run: bool = True) -> list[dict]:
    """Construit les lignes CSV (une par variante). En dry-run, les colonnes
    image restent vides (aucune image Higgsfield générée en phase 1)."""
    rows = []
    couleurs_fr = sorted({v["couleur"] for v in variantes if v["couleur"]})
    has_color = any(v["couleur"] for v in variantes)
    has_size = any(v["taille"] for v in variantes)

    for i, v in enumerate(variantes):
        if i == 0:
            row = {
                "Title": contenu.get("titre", ""),
                "URL handle": contenu.get("handle", ""),
                "Description": contenu.get("description_html", ""),
                "Vendor": VENDOR,
                "Product category": contenu.get("categorie_shopify", ""),
                "Type": contenu.get("type", ""),
                "Tags": ", ".join(contenu.get("tags", [])),
                "Published on online store": "FALSE",   # phase 1 : non publié
                "Status": "draft",                       # brouillon tant que non validé
                "Option1 name": "Couleur" if has_color else "Taille",
                "Option2 name": "Taille" if has_color and has_size else "",
                "Charge tax": "TRUE",
                "Requires shipping": "TRUE",
                "Fulfillment service": "manual",
                "Gift card": "FALSE",
                "SEO title": contenu.get("seo_title", ""),
                "SEO description": contenu.get("seo_desc", ""),
                "Color (product.metafields.shopify.color-pattern)": "; ".join(couleurs_fr),
                "Google Shopping / Google product category": contenu.get("categorie_shopify", ""),
                "Google Shopping / Gender": "Female",
                "Google Shopping / Age group": "Adult",
                "Google Shopping / Condition": "new",
            }
        else:
            row = {"URL handle": contenu.get("handle", "")}

        # champs variante (toutes les lignes)
        if has_color:
            row["Option1 value"] = v["couleur"] or ""
            if has_size:
                row["Option2 value"] = v["taille"] or ""
        else:
            row["Option1 value"] = v["taille"] or "Default"

        row["SKU"] = v["sku"]
        row["Price"] = _fmt(v["prix"])
        row["Compare-at price"] = _fmt(v["compare_at"])
        row["Charge tax"] = "TRUE"
        row["Inventory tracker"] = "shopify"
        row["Inventory quantity"] = str(v.get("qty", 100))
        row["Continue selling when out of stock"] = "deny"
        row["Requires shipping"] = "TRUE"
        row["Fulfillment service"] = "manual"
        row["Weight unit for display"] = "g"
        # Product image URL / Variant image URL : VIDES en dry-run (pas d'image générée)
        rows.append(row)
    return rows


def write_csv(path: str, rows: list[dict]) -> None:
    utils.ensure_dir(os.path.dirname(path) or ".")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=SHOPIFY_HEADERS, restval="",
                           extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
