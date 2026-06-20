"""BLOC 4 — Analyse des ads (recommandation).

Routine : lit les métriques des campagnes actives (via MCP Meta en production),
applique les seuils de config.yaml, et recommande COUPER / SCALER / AJUSTER /
LAISSER TOURNER. Écrit un rapport dans output/a_valider/.

Phase 1 & 2 : RECOMMANDE seulement, n'agit jamais (pas de coupe/scale auto).
La phase 3 pourra autoriser les actions les moins risquées (couper) sous seuils.
"""
