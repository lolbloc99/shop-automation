"""Moteur de décision : applique les seuils config -> recommandation.

Ordre de priorité :
1. APPRENTISSAGE (trop tôt) -> LAISSER TOURNER (ne pas juger).
2. 0 vente + dépense >= 2×CPA cible -> COUPER.
3. ROAS >= roas_scaler_min -> SCALER (+scale_step_pct/jour).
4. ROAS dans [surveiller_min, scaler_min[ -> LAISSER TOURNER (surveiller).
5. ROAS < surveiller_min (avec ventes) ou CTR < ctr_min -> AJUSTER.
6. sinon -> LAISSER TOURNER.
"""

from __future__ import annotations


def evaluate(m: dict, cfg: dict) -> dict:
    aa = cfg["analyse_ads"]
    cpa_cible = aa.get("cpa_cible_eur")
    learn_days = aa.get("fenetre_apprentissage_jours", 3)
    learn_budget = aa.get("budget_apprentissage_jour_eur", 15)
    roas_scaler = aa.get("roas_scaler_min", 2.0)
    roas_surv = aa.get("roas_surveiller_min", 1.5)
    ctr_min = aa.get("ctr_min_pct", 1.0)
    step = aa.get("scale_step_pct", 20)

    spend = m.get("depense", 0.0)
    sales = m.get("conversions", 0)
    roas = m.get("roas")
    ctr = m.get("ctr", 0.0)
    days = m.get("jours_actifs", 0)
    budget = m.get("budget_jour", 0)

    # 1. apprentissage : ne pas juger trop tôt (trop peu de jours ET de dépense)
    if days < learn_days and spend < learn_budget * learn_days:
        return _r("LAISSER TOURNER", "apprentissage",
                  f"Apprentissage en cours ({days} j, {spend:.0f} € < "
                  f"{learn_budget*learn_days:.0f} € seuil). Attendre avant de juger.")

    # 2. couper
    if sales == 0 and cpa_cible and spend >= 2 * cpa_cible:
        return _r("COUPER", "zéro vente",
                  f"0 vente pour {spend:.0f} € dépensés (≥ 2×CPA cible "
                  f"{2*cpa_cible:.0f} €). Brûle sans convertir.")

    # 3. scaler
    if roas is not None and roas >= roas_scaler:
        new_budget = round(budget * (1 + step / 100), 2)
        return _r("SCALER", f"ROAS {roas} ≥ {roas_scaler}",
                  f"Performe (ROAS {roas}). Scaler +{step} %/jour : "
                  f"{budget:.0f} € → {new_budget:.0f} €/jour.")

    # 4. surveiller (proche du seuil de scale)
    if roas is not None and roas >= roas_surv:
        return _r("LAISSER TOURNER", f"ROAS {roas} proche seuil",
                  f"ROAS {roas} ∈ [{roas_surv}, {roas_scaler}[. Stable, surveiller "
                  f"sans toucher.")

    # 5. ajuster
    raisons = []
    if roas is not None and roas < roas_surv:
        raisons.append(f"ROAS {roas} < {roas_surv}")
    if ctr < ctr_min:
        raisons.append(f"CTR {ctr} % < {ctr_min} % (créative à retravailler)")
    if raisons:
        detail = "Marge d'amélioration : " + " ; ".join(raisons) + \
                 ". Tester nouvelle créative / resserrer l'audience avant de couper."
        return _r("AJUSTER", " + ".join(raisons), detail)

    # 6. défaut
    return _r("LAISSER TOURNER", "stable", "Pas de signal fort. Laisser tourner.")


def _r(action: str, niveau: str, detail: str) -> dict:
    return {"action": action, "niveau": niveau, "detail": detail}
