"""BLOC 1 — point d'entrée de la veille.

Usage :
    python -m veille.run                       # tous les concurrents de concurrents.txt
    python -m veille.run --concurrent URL      # un seul concurrent (test)
    python -m veille.run --dry-run             # n'écrit PAS vus.json (mode aperçu)

Le BLOC 1 NE met rien en ligne, NE dépense rien, NE génère aucune image.
`--dry-run` = aperçu : on calcule et on écrit data/nouveaux.json SANS consommer
la mémoire (vus.json non modifié), pour pouvoir relancer à l'identique.
"""

from __future__ import annotations

import argparse

from . import diff, parser, sources, utils


def read_concurrents(path: str) -> list[tuple[str, str]]:
    """Lit concurrents.txt -> liste de (url, plateforme_hint). Ignore # et vides."""
    out = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = [p.strip() for p in line.split("|")]
                url = parts[0]
                hint = parts[1].lower() if len(parts) > 1 else ""
                out.append((url, hint))
    except FileNotFoundError:
        pass
    return out


def process_concurrent(url: str, hint: str, cfg: dict, logger) -> list[dict]:
    """Traite un concurrent : détecte la plateforme, récupère, normalise.
    Renvoie la liste des produits normalisés (vide si échec, loggé)."""
    v = cfg.get("veille", {})
    devise = cfg.get("meta", {}).get("devise", "EUR")
    timeout = v.get("timeout_sec", 20)
    ua = v.get("user_agent", sources.DEFAULT_UA)
    delay = v.get("delai_entre_requetes_sec", 2.0)
    page_size = v.get("shopify", {}).get("page_size", 250)
    cache_dir = utils.repo_path(v.get("cache_brut", "data/raw/").rstrip("/"))
    domain = utils.domain_of(url)

    plateforme = hint or sources.detect_platform(url, timeout, ua, logger)
    logger.info("Concurrent %s -> plateforme : %s", domain, plateforme)

    raw_products = None
    if plateforme == "shopify":
        raw_products = sources.fetch_shopify_products(
            url, page_size, delay, timeout, ua, cache_dir, logger)

    if raw_products is None:
        # fallback collage manuel
        raw_products = sources.load_manual(domain, cache_dir, logger)

    if raw_products is None:
        logger.error("Aucune donnée récupérée pour %s (plateforme=%s). "
                     "Astuce : coller un export dans %s/manual/%s.json",
                     domain, plateforme, cache_dir, domain)
        return []

    scraped_at = utils.now_iso()
    normalized = []
    for raw in raw_products:
        try:
            normalized.append(parser.normalize_shopify_product(
                raw, domain, url, devise, scraped_at))
        except Exception as exc:  # robustesse : un produit cassé ne casse pas le run
            logger.warning("Produit ignoré (parse échoué) chez %s : %s", domain, exc)
    # filtre PRIX PLANCHER : on ne traite aucun produit sous prix_min_eur
    prix_min = cfg.get("prix", {}).get("prix_min_eur")
    if prix_min:
        avant = len(normalized)
        normalized = [p for p in normalized
                      if (p["prix_source"].get("montant") or 0) >= prix_min]
        ignores = avant - len(normalized)
        if ignores:
            logger.info("  %d produits ignorés (< %.2f €) chez %s", ignores, prix_min, domain)
    logger.info("  %d produits retenus pour %s", len(normalized), domain)
    return normalized


def main() -> int:
    ap = argparse.ArgumentParser(description="BLOC 1 — veille concurrents")
    ap.add_argument("--concurrent", help="traiter une seule URL (test)")
    ap.add_argument("--dry-run", action="store_true",
                    help="aperçu : n'écrit pas vus.json")
    ap.add_argument("--config", default="config.yaml")
    args = ap.parse_args()

    logger = utils.get_logger()
    cfg = utils.load_config(args.config)

    if args.concurrent:
        targets = [(args.concurrent, "")]
    else:
        targets = read_concurrents(utils.repo_path(
            cfg.get("veille", {}).get("fichier_concurrents", "concurrents.txt")))

    if not targets:
        logger.error("Aucun concurrent à traiter (concurrents.txt vide ?).")
        return 1

    logger.info("=== Veille BLOC 1 — %d concurrent(s) — dry_run=%s ===",
                len(targets), args.dry_run)

    all_normalized, traites = [], []
    for url, hint in targets:
        all_normalized.extend(process_concurrent(url, hint, cfg, logger))
        traites.append(utils.domain_of(url))

    # comparaison à la mémoire
    vus_path = utils.repo_path(cfg.get("sorties", {}).get("vus", "data/vus.json"))
    seen = diff.load_seen(vus_path)
    nb_avant = len(seen.get("produits", {}))
    nouveaux, seen_maj = diff.find_new(all_normalized, seen)

    # sortie du jour
    nouveaux_path = utils.repo_path(
        cfg.get("sorties", {}).get("nouveaux", "data/nouveaux.json"))
    utils.write_json_atomic(nouveaux_path, {
        "genere_le": utils.now_iso(),
        "dry_run": args.dry_run,
        "concurrents_traites": traites,
        "nb_total_scrape": len(all_normalized),
        "nb_nouveaux": len(nouveaux),
        "produits": nouveaux,
    })

    # mise à jour mémoire (sauf en dry-run)
    if args.dry_run:
        logger.info("[dry-run] vus.json NON modifié (mémoire à %d produits).", nb_avant)
    else:
        utils.write_json_atomic(vus_path, seen_maj)
        logger.info("vus.json mis à jour : %d -> %d produits.",
                    nb_avant, len(seen_maj.get("produits", {})))

    logger.info("=== Résumé : %d scrapés, %d NOUVEAUX -> %s ===",
                len(all_normalized), len(nouveaux), nouveaux_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
