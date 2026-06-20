"""Rendu du rapport d'analyse (Markdown) -> output/a_valider/."""

from __future__ import annotations

_ICONE = {"COUPER": "🔴", "SCALER": "🟢", "AJUSTER": "🟠", "LAISSER TOURNER": "⚪"}


def render(evaluated: list[dict], cfg, date_str: str) -> str:
    aa = cfg["analyse_ads"]
    L = []
    a = L.append

    a(f"# Rapport analyse ads — {date_str}")
    a("")
    a("> **Recommandation seule (phase 1).** Aucune action appliquée : ni coupe, "
      "ni scale, ni changement de budget. Décisions à valider à la main.")
    a("")
    a(f"Seuils : CPA cible {aa['cpa_cible_eur']} € · couper si dépense ≥ "
      f"{2*aa['cpa_cible_eur']} € & 0 vente · scaler si ROAS ≥ {aa['roas_scaler_min']} "
      f"(+{aa['scale_step_pct']} %/j) · apprentissage {aa['fenetre_apprentissage_jours']} j"
      f"/{aa['budget_apprentissage_jour_eur']} €/j.")
    a("")

    a("## Synthèse")
    a("| Campagne | Jours | Dépense | Ventes | ROAS | CPA | CTR | Reco |")
    a("|---|---|---|---|---|---|---|---|")
    for e in evaluated:
        m = e["m"]
        nom = m["campagne"].replace("|", "/")  # éviter de casser les colonnes du tableau
        roas = m["roas"] if m["roas"] is not None else "—"
        cpa = f"{m['cpa']:.0f} €" if m["cpa"] is not None else "—"
        a(f"| {nom} | {m['jours_actifs']} | {m['depense']:.0f} € | "
          f"{m['conversions']} | {roas} | {cpa} | {m['ctr']} % | "
          f"{_ICONE[e['action']]} **{e['action']}** |")
    a("")

    a("## Détail des recommandations")
    for e in evaluated:
        a(f"### {_ICONE[e['action']]} {e['m']['campagne']} → {e['action']}")
        a(f"- {e['detail']}")
        a("")

    # compteur par action
    from collections import Counter
    c = Counter(e["action"] for e in evaluated)
    a("## Bilan")
    a(" · ".join(f"{_ICONE[k]} {k} : {v}" for k, v in c.items()))
    return "\n".join(L)
