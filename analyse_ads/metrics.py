"""Récupération + dérivation des métriques campagnes.

En production : fetch via MCP Meta Ads (insights). En phase 1 (dry-run, aucune
campagne réelle) : jeu simulé couvrant les 4 décisions, ou fichier --metrics.
"""

from __future__ import annotations

from veille import utils


def derive(m: dict) -> dict:
    """Ajoute CTR, CPC, ROAS, CPA à partir des champs bruts."""
    imp = m.get("impressions", 0) or 0
    clics = m.get("clics", 0) or 0
    dep = m.get("depense", 0.0) or 0.0
    conv = m.get("conversions", 0) or 0
    rev = m.get("revenu", 0.0) or 0.0
    m = dict(m)
    m["ctr"] = round(clics / imp * 100, 2) if imp else 0.0
    m["cpc"] = round(dep / clics, 2) if clics else None
    m["roas"] = round(rev / dep, 2) if dep else None
    m["cpa"] = round(dep / conv, 2) if conv else None
    return m


def sample_metrics() -> list[dict]:
    """Jeu simulé (dry-run) : 5 campagnes couvrant apprentissage / couper /
    scaler / ajuster / laisser tourner."""
    return [
        {"campagne": "TEST | robe-denim | A-apprentissage", "jours_actifs": 1,
         "budget_jour": 10, "depense": 9.0, "impressions": 1500, "clics": 18,
         "conversions": 0, "revenu": 0.0},
        {"campagne": "TEST | robe-denim | B-zero-vente", "jours_actifs": 5,
         "budget_jour": 10, "depense": 38.0, "impressions": 9000, "clics": 70,
         "conversions": 0, "revenu": 0.0},
        {"campagne": "TEST | robe-denim | C-perf", "jours_actifs": 4,
         "budget_jour": 10, "depense": 40.0, "impressions": 12000, "clics": 220,
         "conversions": 9, "revenu": 130.0},
        {"campagne": "TEST | robe-denim | D-faible-roas", "jours_actifs": 4,
         "budget_jour": 10, "depense": 42.0, "impressions": 15000, "clics": 90,
         "conversions": 4, "revenu": 60.0},
        {"campagne": "TEST | robe-denim | E-stable", "jours_actifs": 4,
         "budget_jour": 10, "depense": 40.0, "impressions": 11000, "clics": 200,
         "conversions": 6, "revenu": 76.0},
    ]


def load_metrics(path: str | None) -> list[dict]:
    """Charge depuis un fichier --metrics, sinon le jeu simulé (dry-run)."""
    base = utils.read_json(path) if path else None
    if base is None:
        base = sample_metrics()
    elif isinstance(base, dict):
        base = base.get("campagnes", base.get("metrics", []))
    return [derive(m) for m in base]
