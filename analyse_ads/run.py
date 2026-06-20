"""BLOC 4 — point d'entrée (analyse ads, recommandation seule).

Usage :
    python -m analyse_ads.run --dry-run            # jeu simulé -> rapport
    python -m analyse_ads.run --metrics fichier.json

Phase 1 & 2 : RECOMMANDE seulement. N'appelle aucune action Meta (pas de
coupe/scale auto). Écrit un rapport dans output/a_valider/.
"""

from __future__ import annotations

import argparse

from veille import utils

from . import metrics, report, rules


def main() -> int:
    ap = argparse.ArgumentParser(description="BLOC 4 — analyse ads (recommandation)")
    ap.add_argument("--metrics", help="fichier JSON de métriques (sinon jeu simulé)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--config", default="config.yaml")
    args = ap.parse_args()

    logger = utils.get_logger("analyse_ads")
    cfg = utils.load_config(args.config)

    # GARDE-FOU : mode recommandation = jamais d'action automatique.
    if cfg.get("analyse_ads", {}).get("mode") != "recommandation":
        logger.warning("mode != recommandation : en phase 1 on force la recommandation seule.")

    mets = metrics.load_metrics(args.metrics)
    if not mets:
        logger.error("Aucune métrique à analyser.")
        return 1

    evaluated = [{"m": m, **rules.evaluate(m, cfg)} for m in mets]

    date_str = utils.today_str()
    md = report.render(evaluated, cfg, date_str)
    out = utils.repo_path("output", "a_valider", f"rapport_ads_{date_str}.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(md)

    from collections import Counter
    c = Counter(e["action"] for e in evaluated)
    logger.info("=== Analyse : %d campagnes -> %s ===",
                len(evaluated), dict(c))
    logger.info("Rapport (recommandation seule) : %s", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
