"""Contenu rédactionnel (voix de marque) par produit.

C'est la partie GÉNÉRATIVE du BLOC 2. En production, la routine = Claude lit
data/nouveaux.json + CLAUDE.md et écrit, pour chaque produit, un fichier de
rédaction dans output/a_valider/redactions/<id>.json (jamais de copier-coller
du concurrent). Le pipeline lit ensuite ce fichier et assemble la fiche + CSV.

Si la rédaction est absente, on produit un brouillon structurel clairement
marqué « À RÉDIGER » pour que le pipeline ne casse pas.
"""

from __future__ import annotations

import os

from veille import utils  # réutilise les helpers IO/log du BLOC 1

from .transform import slug


def redaction_dir() -> str:
    return utils.repo_path("output", "a_valider", "redactions")


def _safe_id(pid: str) -> str:
    return pid.replace("::", "__").replace("/", "_")


def load_redaction(pid: str):
    """Charge la rédaction voix-de-marque pour un produit (ou None)."""
    return utils.read_json(os.path.join(redaction_dir(), _safe_id(pid) + ".json"))


def build_prompt(product, cfg) -> str:
    """Instruction de rédaction (ce que Claude suit en production). Loggée pour
    audit et utilisable telle quelle."""
    vm = cfg["voix_marque"]
    lo, hi = vm["longueur_description_mots"]
    return (
        f"Rédige en {vm['langue']}, voix {', '.join(vm['ton'])}, {lo}-{hi} mots. "
        f"Structure imposée : accroche 1 ligne ; lead ; **section matière** ; "
        f"**section coupe** ; **Le bon geste d'entretien** (lavage). Pas d'emoji, prose. "
        f"Titre au format « {vm['titre_pattern']} », sans nom ni marque du concurrent. "
        f"Produit source (RÉFÉRENCE, ne jamais copier) : "
        f"« {product.get('titre_source','')} » — {product.get('type_source','')}. "
        f"À privilégier : {', '.join(vm.get('privilegier', []))}. "
        f"À éviter : {', '.join(vm.get('eviter', []))}."
    )


def draft_template(product, cfg) -> dict:
    """Brouillon structurel, marqué À RÉDIGER (fallback si pas de rédaction)."""
    titre = product.get("titre_source", "produit")
    return {
        "titre": f"[À RÉDIGER] {titre}",
        "handle": slug(titre),
        "type": "",
        "categorie_shopify": "",
        "tags": [],
        "description_html": "<p>[À RÉDIGER — voix de marque Oria Studio]</p>",
        "seo_title": "",
        "seo_desc": "",
        "image_prompt": "",
        "_brouillon": True,
    }
