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


def find_new(normalized: list[dict], seen: dict) -> tuple[list[dict], dict]:
    """Sépare les produits jamais vus. Renvoie (nouveaux, seen_mis_a_jour).

    `seen` n'est PAS écrit ici (le caller décide selon --dry-run) ; on renvoie la
    version mise à jour en mémoire.
    """
    produits = dict(seen.get("produits", {}))
    nouveaux = []
    for prod in normalized:
        pid = prod["id"]
        if pid not in produits:
            nouveaux.append(prod)
            produits[pid] = {
                "titre": prod.get("titre_source", ""),
                "concurrent": prod.get("concurrent", ""),
                "source_url": prod.get("source_url", ""),
                "vu_le": prod.get("scraped_at", utils.now_iso()),
            }
    return nouveaux, {"produits": produits}
