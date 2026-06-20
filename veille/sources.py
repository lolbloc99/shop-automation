"""Récupération de la donnée concurrente.

Méthode privilégiée : si la boutique est Shopify, on tape l'endpoint public
`/products.json` (data structurée, propre, stable) plutôt que de scraper le HTML.
Fallbacks prévus : HTML, ou collage manuel d'un fichier dans data/raw/manual/.
"""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from typing import Optional

from . import utils

DEFAULT_UA = "Mozilla/5.0 (compatible; veille-bot/1.0; +contact)"


def _ssl_context() -> ssl.SSLContext:
    """Contexte SSL avec vérification active. Utilise le bundle CA de `certifi`
    si disponible (certains Python macOS n'ont pas les certs système), sinon le
    contexte par défaut. La vérification n'est jamais désactivée."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


_SSL_CTX = _ssl_context()


def http_get(url: str, timeout: int = 20, user_agent: str = DEFAULT_UA,
             retries: int = 3, backoff: float = 1.5, logger=None):
    """GET robuste : retries + backoff. Renvoie (status, body_text, headers) ou
    (None, None, None) en cas d'échec définitif (loggé clairement)."""
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": user_agent})
            with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                return resp.status, body, dict(resp.headers)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last_err = exc
            if logger:
                logger.warning("GET échec (tentative %d/%d) %s : %s",
                               attempt, retries, url, exc)
            utils.polite_sleep(backoff * attempt)
    if logger:
        logger.error("GET abandonné après %d tentatives : %s (%s)",
                     retries, url, last_err)
    return None, None, None


def detect_platform(base_url: str, timeout: int, user_agent: str, logger=None) -> str:
    """Détecte la plateforme. Renvoie 'shopify' ou 'unknown'.

    Signaux Shopify : header `powered-by: Shopify`, ou `/products.json` renvoyant
    un objet avec une clé `products`.
    """
    base = base_url.rstrip("/")
    status, body, headers = http_get(f"{base}/products.json?limit=1",
                                     timeout, user_agent, logger=logger)
    if status == 200 and body:
        try:
            data = json.loads(body)
            if isinstance(data, dict) and "products" in data:
                return "shopify"
        except json.JSONDecodeError:
            pass
    if headers and "shopify" in str(headers.get("powered-by", "")).lower():
        return "shopify"
    return "unknown"


def fetch_shopify_products(base_url: str, page_size: int, delay: float,
                           timeout: int, user_agent: str, cache_dir: str,
                           logger=None) -> Optional[list]:
    """Récupère TOUT le catalogue via /products.json paginé.

    Renvoie la liste des produits bruts Shopify, ou None si échec.
    Met en cache chaque page brute dans data/raw/<domaine>/ (audit + reprise).
    """
    base = base_url.rstrip("/")
    domain = utils.domain_of(base_url)
    out: list = []
    page = 1
    raw_dir = f"{cache_dir.rstrip('/')}/{domain}"
    utils.ensure_dir(raw_dir)

    while True:
        url = f"{base}/products.json?limit={page_size}&page={page}"
        status, body, _ = http_get(url, timeout, user_agent, logger=logger)
        if status != 200 or not body:
            if page == 1:
                return None  # échec total
            break  # plus de pages disponibles
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            if logger:
                logger.error("JSON invalide sur %s", url)
            return None if page == 1 else out
        products = data.get("products", [])
        if not products:
            break  # fin de pagination
        # cache brut de la page (pour audit et reprise sans re-scrape)
        utils.write_json_atomic(f"{raw_dir}/products_p{page:03d}.json", data)
        out.extend(products)
        if logger:
            logger.info("  page %d : %d produits (total %d)", page, len(products), len(out))
        if len(products) < page_size:
            break  # dernière page
        page += 1
        utils.polite_sleep(delay)
    return out


def load_manual(domain: str, cache_dir: str, logger=None) -> Optional[list]:
    """Fallback « collage manuel » : si data/raw/manual/<domaine>.json existe
    (liste de produits au format Shopify), on l'utilise. Pour les sites qui
    bloquent le bot, l'humain colle le JSON/HTML ici."""
    path = f"{cache_dir.rstrip('/')}/manual/{domain}.json"
    data = utils.read_json(path)
    if data is None:
        return None
    if logger:
        logger.info("Fichier manuel trouvé pour %s : %s", domain, path)
    return data.get("products", data) if isinstance(data, dict) else data
