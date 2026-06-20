"""Contenu créatif (texte d'accroche voix de marque) par produit.

Partie générative du BLOC 3, comme redaction.py pour le BLOC 2. En production,
la routine (Claude) rédige les variations dans la voix Oria en respectant les
claims interdits de CLAUDE.md, et les écrit dans
output/a_valider/ads_creatives/<id>.json. Le pipeline assemble ensuite le draft.
"""

from __future__ import annotations

import os

from veille import utils


def creatives_dir() -> str:
    return utils.repo_path("output", "a_valider", "ads_creatives")


def _safe_id(pid: str) -> str:
    return pid.replace("::", "__").replace("/", "_")


def load_creatives(pid: str):
    """Charge les variations créatives d'un produit (ou None)."""
    return utils.read_json(os.path.join(creatives_dir(), _safe_id(pid) + ".json"))


def draft_template(cfg) -> dict:
    """Brouillon vide marqué À RÉDIGER (fallback)."""
    v = cfg["ads"]["variations"]
    return {
        "_brouillon": True,
        "bodies": ["[À RÉDIGER — voix Oria]"] * v["bodies"],
        "titles": ["[À RÉDIGER]"] * v["titles"],
        "descriptions": ["[À RÉDIGER]"] * v["descriptions"],
        "call_to_action": "SHOP_NOW",
    }
