"""BLOC 3 — point d'entrée (préparation campagne Meta).

Usage :
    python -m ads.run --dry-run --index 0     # draft pour 1 produit -> output/a_valider/

Phase 1 : dry-run FORCÉ. On bâtit le draft (campagne/adset/ad PAUSED) et le récap,
SANS appeler le MCP Meta. La création live et l'activation sont des actions
humaines validées séparément (cf. règle de sécurité, spec §5).
"""

from __future__ import annotations

import argparse

from veille import utils
from pipeline import redaction as redac

from . import campaign, creative, recap


def build_one(product, cfg, logger, dry_run: bool) -> dict:
    pid = product["id"]

    # rédaction (titre/handle) réutilisée du BLOC 2
    red = redac.load_redaction(pid) or redac.draft_template(product, cfg)
    red["handle"] = red.get("handle") or product.get("titre_source", "produit")

    creatives = creative.load_creatives(pid)
    brouillon = creatives is None
    if brouillon:
        creatives = creative.draft_template(cfg)
        logger.warning("Créatives absentes pour %s -> brouillon. À rédiger (voix Oria).", pid)

    draft = campaign.build_draft(product, red, creatives, cfg, utils.today_str())

    handle = red["handle"]
    out_dir = ("output", "a_valider")
    utils.write_json_atomic(utils.repo_path(*out_dir, f"{handle}.ads.json"), draft)
    md = recap.render(draft, cfg, dry_run, brouillon)
    with open(utils.repo_path(*out_dir, f"{handle}.ads.md"), "w", encoding="utf-8") as fh:
        fh.write(md)

    logger.info("Draft campagne prêt : %s (statut %s)%s",
                handle, draft["campaign"]["status"],
                "  [BROUILLON]" if brouillon else "")
    return {"handle": handle, "brouillon": brouillon}


def main() -> int:
    ap = argparse.ArgumentParser(description="BLOC 3 — draft campagne Meta")
    ap.add_argument("--id")
    ap.add_argument("--index", type=int, default=0)
    ap.add_argument("--limit", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--config", default="config.yaml")
    args = ap.parse_args()

    logger = utils.get_logger("ads")
    cfg = utils.load_config(args.config)

    # GARDE-FOU : en phase 1 (ou ads.actif=false), on n'appelle JAMAIS Meta.
    phase = cfg.get("meta", {}).get("phase", 1)
    if phase == 1 or not cfg.get("ads", {}).get("actif", False):
        if not args.dry_run:
            logger.warning("Phase 1 / ads.actif=false -> dry-run FORCÉ (aucune création Meta).")
        args.dry_run = True

    nouveaux = utils.read_json(
        utils.repo_path(cfg["sorties"]["nouveaux"]), default={"produits": []})
    produits = nouveaux.get("produits", [])
    if not produits:
        logger.error("Aucun produit dans nouveaux.json.")
        return 1

    if args.id:
        cibles = [p for p in produits if p["id"] == args.id] or []
    else:
        cibles = produits[args.index:args.index + args.limit]
    if not cibles:
        logger.error("Aucun produit sélectionné.")
        return 1

    logger.info("=== BLOC 3 ads — %d produit(s) — dry_run=%s ===", len(cibles), args.dry_run)
    res = [build_one(p, cfg, logger, args.dry_run) for p in cibles]
    prets = sum(1 for r in res if not r["brouillon"])
    logger.info("=== %d draft(s) prêt(s) à valider (PAUSED) dans output/a_valider/ "
                "(%d brouillon) ===", prets, len(res) - prets)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
