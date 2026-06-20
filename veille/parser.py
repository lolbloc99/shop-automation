"""Normalisation : produit brut Shopify -> schéma produit interne.

Le BLOC 1 capture la donnée concurrente telle quelle (référence). La règle de
prix (×1.4), la réécriture de marque et le mapping couleurs/tailles FR sont
appliqués plus tard par le BLOC 2. Ici on ne transforme PAS, on capture.
"""

from __future__ import annotations

from typing import Any

# Mots-clés indiquant une chaussure (NL / EN / FR) -> choix du référentiel tailles.
_CHAUSSURE_KW = (
    "schoen", "schoenen", "sneaker", "laars", "laarz", "boot", "sandaal",
    "sandal", "pump", "hak", "shoe", "chaussure", "basket", "botte", "escarpin",
    "mocassin", "loafer", "heel",
)

# Noms d'option qui désignent une couleur / une taille (NL / EN / FR).
_COLOR_NAMES = ("kleur", "color", "colour", "couleur")
_SIZE_NAMES = ("maat", "maten", "size", "taille", "pointure", "schoenmaat")


def guess_category(product_type: str, tags: list[str]) -> str:
    """'chaussure' si le type/les tags évoquent une chaussure, sinon 'vetement'."""
    haystack = " ".join([product_type or ""] + (tags or [])).lower()
    return "chaussure" if any(kw in haystack for kw in _CHAUSSURE_KW) else "vetement"


def _to_float(value: Any):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _classify_option(name: str, values: list[str]) -> str:
    """Devine si une option est 'couleur', 'taille' ou 'autre'."""
    low = (name or "").lower()
    if any(k in low for k in _COLOR_NAMES):
        return "couleur"
    if any(k in low for k in _SIZE_NAMES):
        return "taille"
    # heuristique sur les valeurs : XS/S/M/L.. ou nombres 30-50 -> taille
    sizes = {"xs", "s", "m", "l", "xl", "xxl", "xxxl"}
    vals = [str(v).strip().lower() for v in (values or [])]
    if vals and all(v in sizes or (v.isdigit() and 28 <= int(v) <= 50) for v in vals):
        return "taille"
    return "autre"


def normalize_shopify_product(raw: dict, concurrent_domain: str,
                              source_base: str, devise: str = "EUR",
                              scraped_at: str = "") -> dict:
    """Convertit un produit brut Shopify vers le schéma interne."""
    handle = raw.get("handle", "")
    pid = raw.get("id")
    tags = raw.get("tags", [])
    if isinstance(tags, str):  # certains stores renvoient une string CSV
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    product_type = raw.get("product_type", "") or ""

    # options -> classification couleur/taille
    options_src = []
    couleurs, tailles = [], []
    for opt in raw.get("options", []):
        name = opt.get("name", "")
        values = opt.get("values", []) or []
        kind = _classify_option(name, values)
        options_src.append({"name": name, "kind": kind, "values": values})
        if kind == "couleur":
            couleurs = values
        elif kind == "taille":
            tailles = values

    # variantes + bornes de prix
    variantes, prices, compares = [], [], []
    images = [img.get("src") for img in raw.get("images", []) if img.get("src")]
    for v in raw.get("variants", []):
        price = _to_float(v.get("price"))
        compare = _to_float(v.get("compare_at_price"))
        if price is not None:
            prices.append(price)
        if compare is not None:
            compares.append(compare)
        feat = v.get("featured_image") or {}
        variantes.append({
            "sku": v.get("sku", ""),
            "titre": v.get("title", ""),
            "option1": v.get("option1"),
            "option2": v.get("option2"),
            "option3": v.get("option3"),
            "prix": price,
            "compare_at": compare,
            "disponible": v.get("available"),
            "image": feat.get("src"),
        })

    prix_min = min(prices) if prices else None
    # compare-at représentatif : celui de la variante au prix mini (= "prix avant
    # réduction" à conserver), sinon le max des compare-at trouvés.
    compare_repr = None
    if prix_min is not None:
        for v in variantes:
            if v["prix"] == prix_min and v["compare_at"]:
                compare_repr = v["compare_at"]
                break
    if compare_repr is None and compares:
        compare_repr = max(compares)

    return {
        "id": f"{concurrent_domain}::{pid}",
        "concurrent": concurrent_domain,
        "platform": "shopify",
        "source_url": f"{source_base.rstrip('/')}/products/{handle}",
        "scraped_at": scraped_at,
        "titre_source": raw.get("title", ""),
        "description_source_html": raw.get("body_html", ""),
        "vendor": raw.get("vendor", ""),
        "type_source": product_type,
        "tags": tags,
        "categorie": guess_category(product_type, tags),
        "prix_source": {
            "devise": devise,
            "montant": prix_min,
            "compare_at": compare_repr,
            "min": prix_min,
            "max": max(prices) if prices else None,
        },
        "options_source": options_src,
        "couleurs_source": couleurs,
        "tailles_source": tailles,
        "variantes_source": variantes,
        "images": images,
    }
