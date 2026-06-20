"""Construit le DRAFT de campagne Meta (structure proche de l'API Marketing).

Le dict produit ici est ce que la création live enverrait au MCP Meta Ads. En
phase 1 il n'est PAS envoyé : il est seulement écrit en récap pour validation.
"""

from __future__ import annotations

# Meta : 1 = hommes, 2 = femmes
_GENRE_META = {"hommes": [1], "femmes": [2], "tous": [1, 2]}

# Placeholders remplis au moment de la création live (produit publié + visuels générés).
PH_URL = "{{SHOPIFY_PRODUCT_URL}}"
PH_VISUEL = {"1:1": "{{VISUEL_1x1}}", "4:5": "{{VISUEL_4x5}}", "9:16": "{{VISUEL_9x16}}"}


def build_targeting(cfg) -> dict:
    a = cfg["ads"]["audience_defaut"]
    return {
        "geo_locations": {"countries": a.get("pays", ["FR"])},
        "genders": _GENRE_META.get(a.get("genre", "femmes"), [2]),
        "age_min": a.get("age_min", 25),
        "age_max": a.get("age_max", 55),
        "targeting_automation": {"advantage_audience": 1},  # large / advantage+
    }


def build_draft(product, redaction, creatives, cfg, date_str: str) -> dict:
    """Assemble campagne + ad set + ad (asset_feed_spec multi-format) en PAUSED."""
    ads = cfg["ads"]
    handle = redaction.get("handle", "produit")
    titre = redaction.get("titre", product.get("titre_source", ""))
    budget = ads["budget_test_jour_eur"]

    campaign = {
        "name": f"TEST | {handle} | SALES | {date_str}",
        "objective": ads["objectif"],                 # OUTCOME_SALES
        "special_ad_categories": [],
        "status": ads["statut_creation"],             # PAUSED
    }

    adset = {
        "name": f"{handle} | FR-femmes-{cfg['ads']['audience_defaut']['age_min']}"
                f"-{cfg['ads']['audience_defaut']['age_max']}",
        "daily_budget_eur": budget,
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "OFFSITE_CONVERSIONS",
        "promoted_object": {
            "pixel_id": ads.get("pixel_id", "") or "{{PIXEL_ID}}",
            "custom_event_type": ads["evenement_conversion"],  # PURCHASE
        },
        "targeting": build_targeting(cfg),
        "status": ads["statut_creation"],
    }

    ad = {
        "name": f"{handle} | multiformat",
        "status": ads["statut_creation"],
        "creative": {
            "asset_feed_spec": {
                # multi-format dans la MÊME ad (règle 2)
                "formats": ads["formats"],
                "visuels_par_format": dict(PH_VISUEL),   # placeholders (images non générées)
                "bodies": creatives.get("bodies", []),       # règle 3 : 3-5
                "titles": creatives.get("titles", []),
                "descriptions": creatives.get("descriptions", []),
                "link_url": PH_URL,                          # produit publié -> au GO
                "call_to_action": {"type": creatives.get("call_to_action", "SHOP_NOW")},
            }
        },
    }

    return {
        "campaign": campaign,
        "adset": adset,
        "ad": ad,
        "_meta": {
            "compte_publicitaire": ads.get("compte_publicitaire", "") or "{{ACT_ID}}",
            "page_fb": ads.get("page_fb", "") or "{{PAGE_ID}}",
            "compte_ig": ads.get("compte_ig", "") or "{{IG_ID}}",
            "titre_produit": titre,
        },
    }
