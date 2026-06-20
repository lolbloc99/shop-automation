"""Transformations déterministes : prix, mapping tailles/couleurs, variantes.

Aucune création de contenu ici (ça, c'est redaction.py / Claude). On applique
les règles chiffrées et de structure définies dans config.yaml.
"""

from __future__ import annotations

import math
import re
import unicodedata

# Tailles concurrent -> référentiel marque (le reste passe en majuscules tel quel).
_SIZE_MAP = {"2XL": "XXL", "3XL": "XXXL", "4XL": "XXXXL"}


def slug(text: str) -> str:
    """Transforme un titre en handle URL (minuscule, accents retirés, tirets)."""
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "produit"


def arrondi_99(x):
    """Arrondi supérieur au .99 le plus proche (ex. 62.99, 104.99)."""
    if x is None:
        return None
    base = math.floor(x)
    cand = base + 0.99
    if cand + 1e-9 >= x:
        return round(cand, 2)
    return round(base + 1.99, 2)


def _applique_prix(montant, cfg) -> float | None:
    """montant × multiplicateur, puis arrondi .99 uniquement si activé en config.
    Avec multiplicateur 1.0 + appliquer_arrondi false => prix concurrent exact."""
    if montant is None:
        return None
    val = montant * cfg["prix"]["multiplicateur"]
    if cfg["prix"].get("appliquer_arrondi", False):
        return arrondi_99(val)
    return round(val, 2)


def calc_prix_vente(prix_source, cfg) -> float | None:
    return _applique_prix(prix_source, cfg)


def calc_compare_at(prix_vente, compare_source, cfg) -> float | None:
    """Prix barré (« prix avant réduction »). Stratégie depuis config.yaml."""
    c = cfg["prix"].get("compare_at", {})
    if not c.get("actif"):
        return None
    strat = c.get("strategie", "concurrent")
    if strat == "none":
        return None
    if strat == "concurrent":
        # reprend le vrai prix barré du concurrent (défendable légalement)
        return _applique_prix(compare_source, cfg) if compare_source else None
    if strat == "markup":
        r = c.get("remise_affichee", 0.45)
        if 0 < r < 1 and prix_vente:
            return arrondi_99(prix_vente / (1 - r))  # ancre synthétique : .99 voulu
    return None


def map_taille(valeur, categorie, cfg) -> tuple[str, bool]:
    """Renvoie (taille_mappée, dans_référentiel)."""
    up = str(valeur).strip().upper()
    mapped = _SIZE_MAP.get(up, up)
    ref = (cfg["variantes"]["tailles_vetements"] if categorie == "vetement"
           else cfg["variantes"]["tailles_chaussures"])
    ref = [str(x).upper() for x in ref]
    return mapped, mapped in ref


def map_couleur(valeur, cfg) -> tuple[str, bool]:
    """Renvoie (couleur_fr, mappée). Si non trouvée : valeur gardée + flag False."""
    s = str(valeur).strip()
    mapping = cfg["variantes"]["couleurs"].get("mapping", {})
    for src, fr in mapping.items():
        if src.lower() == s.lower():
            return fr, True
    return s, False


def make_sku(handle: str, couleur, taille) -> str:
    abbr = "".join(w[0] for w in handle.split("-") if w)[:6].upper() or "PROD"
    col = (str(couleur)[:3].upper() if couleur else "NA")
    siz = (str(taille).upper() if taille else "U")
    return f"ORIA-{abbr}-{col}-{siz}"


def _option_positions(product) -> tuple[int | None, int | None]:
    """Position (1-based) des options couleur et taille."""
    pos_color = pos_size = None
    for i, opt in enumerate(product.get("options_source", []), start=1):
        if opt.get("kind") == "couleur":
            pos_color = i
        elif opt.get("kind") == "taille":
            pos_size = i
    return pos_color, pos_size


def build_variantes(product, cfg, handle: str):
    """Construit les variantes marque depuis les variantes concurrent.

    Renvoie (variantes, warnings). Mappe couleurs->FR et tailles->référentiel ;
    exclut les tailles hors référentiel (avec avertissement) ; calcule prix +
    compare-at par variante.
    """
    pos_color, pos_size = _option_positions(product)
    categorie = product.get("categorie", "vetement")
    variantes, warnings = [], []
    couleurs_non_mappees = set()
    tailles_exclues = set()

    for v in product.get("variantes_source", []):
        color_src = v.get(f"option{pos_color}") if pos_color else None
        size_src = v.get(f"option{pos_size}") if pos_size else None

        couleur, color_ok = (map_couleur(color_src, cfg) if color_src else (None, True))
        if color_src and not color_ok:
            couleurs_non_mappees.add(f"{color_src}->{couleur}")

        taille, size_ok = (map_taille(size_src, categorie, cfg) if size_src else (None, True))
        if size_src and not size_ok:
            tailles_exclues.add(f"{size_src}->{taille}")
            continue  # hors référentiel -> exclue

        prix = calc_prix_vente(v.get("prix"), cfg)
        compare = calc_compare_at(prix, v.get("compare_at"), cfg)
        dispo = v.get("disponible")
        variantes.append({
            "couleur": couleur,
            "taille": taille,
            "sku": make_sku(handle, couleur, taille),
            "prix": prix,
            "compare_at": compare,
            "qty": 100 if dispo is not False else 0,
            "prix_source": v.get("prix"),
            "compare_source": v.get("compare_at"),
        })

    if couleurs_non_mappees:
        warnings.append("Couleurs non mappées en FR (gardées telles quelles) : "
                        + ", ".join(sorted(couleurs_non_mappees)))
    if tailles_exclues:
        warnings.append("Tailles hors référentiel exclues : "
                        + ", ".join(sorted(tailles_exclues)))
    return variantes, warnings
