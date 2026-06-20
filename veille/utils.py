"""Utilitaires partagés du BLOC 1 : config, logs, IO JSON atomique, délais."""

from __future__ import annotations

import datetime as _dt
import json
import logging
import os
import time
from typing import Any
from urllib.parse import urlparse

import yaml

# Racine du dépôt = dossier parent de veille/
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def now_iso() -> str:
    """Horodatage ISO 8601 UTC (ex. 2026-06-20T05:00:00+00:00)."""
    return _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat()


def today_str() -> str:
    return _dt.datetime.now(_dt.UTC).strftime("%Y-%m-%d")


def repo_path(*parts: str) -> str:
    """Chemin absolu à partir de la racine du dépôt."""
    return os.path.join(ROOT, *parts)


def load_config(path: str = "config.yaml") -> dict:
    """Charge config.yaml (chemin relatif à la racine du dépôt si non absolu)."""
    if not os.path.isabs(path):
        path = repo_path(path)
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def read_json(path: str, default: Any = None) -> Any:
    """Lit un JSON ; renvoie `default` si le fichier est absent ou illisible."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json_atomic(path: str, obj: Any) -> None:
    """Écrit un JSON de façon atomique (tmp + os.replace) pour éviter la corruption
    si le run est interrompu en plein milieu (exigence de reprise)."""
    ensure_dir(os.path.dirname(path) or ".")
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def domain_of(url: str) -> str:
    """Domaine nu d'une URL (sans www.), sert de clé concurrent stable."""
    netloc = urlparse(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def polite_sleep(seconds: float) -> None:
    """Délai anti-blocage entre deux requêtes."""
    if seconds and seconds > 0:
        time.sleep(seconds)


def get_logger(name: str = "veille") -> logging.Logger:
    """Logger qui écrit à la fois sur stdout et dans logs/veille_<date>.log."""
    logger = logging.getLogger(name)
    if logger.handlers:  # déjà configuré
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S")

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    logs_dir = repo_path("logs")
    ensure_dir(logs_dir)
    fh = logging.FileHandler(os.path.join(logs_dir, f"veille_{today_str()}.log"),
                             encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    return logger
