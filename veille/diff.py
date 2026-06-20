"""Comparaison avec la mémoire `data/vus.json` -> nouveautés du jour.

Persistance : vus.json est versionné dans le dépôt. Une routine cloud n'a aucune
mémoire d'un run à l'autre ; cette mémoire EST le fichier.
"""

from __future__ import annotations

from . import utils


def load_seen(vus_path: str) -> dict:
    """Charge la mémoire des produits déjà vus. Schéma : {"produits": {id: {...}}}."""
    data = utils.read_json(vus_path, default={"produits": {}})
    if "produits" not in data:
        data = {"produits": {}}
    return data


def find_new(normalized: list[dict], seen: dict) -> tuple[list[dict], dict, int]:
    """Sépare les produits jamais vus. Renvoie (nouveaux, seen_mis_a_jour, nb_baseline).

    **Onboarding nouveau concurrent** : un concurrent est « connu » dès qu'il a ≥1
    produit en mémoire. Au TOUT PREMIER passage d'un domaine (catalogue d'arrivée,
    potentiellement des centaines de produits PAS forcément trend), on marque tout
    « vu » SANS le traiter (baseline silencieuse). Seuls les produits ajoutés ENSUITE
    par un concurrent déjà connu remontent en `nouveaux` (= vrais drops). Ça évite de
    créer tout le vieux catalogue d'un concurrent qu'on vient d'ajouter.

    `seen` n'est PAS écrit ici (le caller décide selon --dry-run).
    """
    produits = dict(seen.get("produits", {}))
    # domaines déjà baseline (>=1 produit en mémoire) -> leurs nouveaux sont de vrais drops
    domaines_connus = {e.get("concurrent", "") for e in produits.values()} - {""}

    nouveaux, nb_baseline = [], 0
    for prod in normalized:
        pid = prod["id"]
        if pid in produits:
            continue
        dom = prod.get("concurrent", "")
        produits[pid] = {
            "titre": prod.get("titre_source", ""),
            "concurrent": dom,
            "source_url": prod.get("source_url", ""),
            "vu_le": prod.get("scraped_at", utils.now_iso()),
        }
        if dom in domaines_connus:
            nouveaux.append(prod)   # concurrent déjà connu -> vrai nouveau à traiter
        else:
            nb_baseline += 1        # 1er passage du concurrent -> baseline, on ne traite pas
    return nouveaux, {"produits": produits}, nb_baseline
