"""BLOC 2 — point d'entrée du pipeline produit.

Usage :
    python -m pipeline.run --dry-run                 # 1er produit de nouveaux.json
    python -m pipeline.run --index 0 --dry-run       # produit par index
    python -m pipeline.run --id "domaine::123"       # produit par id
    python -m pipeline.run --limit 1 --dry-run       # n premiers produits

Phase 1 : --dry-run = aucune image Higgsfield, rien poussé sur Shopify. Sorties
(fiche .md + CSV) déposées dans output/a_valider/. La mise en ligne reste manuelle.
"""

from __future__ import annotations

import argparse

from veille import utils

from . import csv_export, fiche, redaction, transform


def build_one(product, cfg, logger, dry_run: bool) -> dict:
    pid = product["id"]
    contenu = redaction.load_redaction(pid)
    used_template = False
    if not contenu:
        contenu = redaction.draft_template(product, cfg)
        used_template = True
        logger.warning("Rédaction absente pour %s -> brouillon template. Prompt :\n%s",
                       pid, redaction.build_prompt(product, cfg))

    handle = contenu.get("handle") or transform.slug(product.get("titre_source", ""))
    contenu["handle"] = handle

    variantes, warnings = transform.build_variantes(product, cfg, handle)

    rows = csv_export.build_rows(contenu, variantes, dry_run=dry_run)
    csv_path = utils.repo_path("output", "a_valider", f"{handle}.csv")
    csv_export.write_csv(csv_path, rows)

    md = fiche.render(product, contenu, variantes, warnings, cfg, dry_run, used_template)
    md_path = utils.repo_path("output", "a_valider", f"{handle}.md")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(md)

    logger.info("Fiche prête : %s (%d variantes)%s",
                handle, len(variantes), "  [BROUILLON]" if used_template else "")
    return {"handle": handle, "csv": csv_path, "md": md_path,
            "n_variantes": len(variantes), "warnings": warnings,
            "brouillon": used_template}


def main() -> int:
    ap = argparse.ArgumentParser(description="BLOC 2 — pipeline produit")
    ap.add_argument("--id", help="id produit (domaine::id)")
    ap.add_argument("--index", type=int, default=0, help="index dans nouveaux.json")
    ap.add_argument("--limit", type=int, default=1, help="nombre de produits à traiter")
    ap.add_argument("--dry-run", action="store_true",
                    help="aucune image, rien poussé Shopify (phase 1)")
    ap.add_argument("--config", default="config.yaml")
    args = ap.parse_args()

    logger = utils.get_logger("pipeline")
    cfg = utils.load_config(args.config)

    # garde-fou : en phase 1, on force le dry-run même si oublié
    if cfg.get("meta", {}).get("phase", 1) == 1 and not args.dry_run:
        logger.warning("Phase 1 détectée -> dry-run forcé (pas d'image, pas de Shopify).")
        args.dry_run = True

    nouveaux_path = utils.repo_path(
        cfg.get("sorties", {}).get("nouveaux", "data/nouveaux.json"))
    data = utils.read_json(nouveaux_path, default={"produits": []})
    produits = data.get("produits", [])
    if not produits:
        logger.error("Aucun produit dans %s. Lance d'abord le BLOC 1 (veille).",
                     nouveaux_path)
        return 1

    # sélection
    if args.id:
        cibles = [p for p in produits if p["id"] == args.id]
        if not cibles:
            logger.error("Id introuvable : %s", args.id)
            return 1
    else:
        cibles = produits[args.index:args.index + args.limit]

    logger.info("=== Pipeline BLOC 2 — %d produit(s) — dry_run=%s ===",
                len(cibles), args.dry_run)

    resultats = [build_one(p, cfg, logger, args.dry_run) for p in cibles]

    prets = sum(1 for r in resultats if not r["brouillon"])
    logger.info("=== %d produit(s) prêt(s) à valider dans output/a_valider/ "
                "(%d brouillon(s) à rédiger) ===",
                prets, len(resultats) - prets)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
