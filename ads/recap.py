"""Récap lisible (Markdown) du draft de campagne, déposé dans output/a_valider/."""

from __future__ import annotations


def render(draft, cfg, dry_run, brouillon) -> str:
    c, aset, ad = draft["campaign"], draft["adset"], draft["ad"]
    afs = ad["creative"]["asset_feed_spec"]
    t = aset["targeting"]
    L = []
    a = L.append

    a(f"# Draft campagne — {draft['_meta']['titre_produit']}")
    a("")
    a("> **DRAFT — non créé sur Meta.** Préparé en dry-run. Création live (PAUSED) "
      "puis activation = actions humaines validées séparément. Aucun budget engagé.")
    a("")
    if brouillon:
        a("> ⚠️ **Créatives manquantes** : variations à rédiger avant validation.")
        a("")

    a("## Règles immuables (vérif)")
    a(f"- Objectif : **{c['objective']}**  ·  Conversion pixel : "
      f"**{aset['promoted_object']['custom_event_type']}**")
    a(f"- Multi-format (asset_feed_spec) : **{', '.join(afs['formats'])}**")
    a(f"- Variations : **{len(afs['bodies'])} bodies · {len(afs['titles'])} titles · "
      f"{len(afs['descriptions'])} descriptions**")
    a("")

    a("## Campagne / Ad set")
    a(f"- Campagne : `{c['name']}` — statut **{c['status']}**")
    a(f"- Ad set : `{aset['name']}`")
    a(f"- Budget : **{aset['daily_budget_eur']} €/jour**  ·  optimisation "
      f"{aset['optimization_goal']}")
    a(f"- Audience : {', '.join(t['geo_locations']['countries'])} · "
      f"genres {t['genders']} · {t['age_min']}-{t['age_max']} ans · advantage+")
    a("")

    a("## Créatives (voix de marque)")
    a("**Primary texts (bodies) :**")
    for i, b in enumerate(afs["bodies"], 1):
        a(f"{i}. {b}")
    a("")
    a("**Titles (headlines) :**")
    for i, ti in enumerate(afs["titles"], 1):
        a(f"{i}. {ti}")
    a("")
    a("**Descriptions :**")
    for i, d in enumerate(afs["descriptions"], 1):
        a(f"{i}. {d}")
    a(f"\n- CTA : **{afs['call_to_action']['type']}**")
    a("")

    a("## À remplir au GO de création (placeholders)")
    a(f"- Lien produit : `{afs['link_url']}` (produit Shopify pas encore publié)")
    a(f"- Visuels : `{afs['visuels_par_format']}` (images non générées en phase 1)")
    a(f"- Compte : `{draft['_meta']['compte_publicitaire']}` · Page : "
      f"`{draft['_meta']['page_fb']}` · IG : `{draft['_meta']['compte_ig']}` · "
      f"Pixel : `{aset['promoted_object']['pixel_id']}`")
    a("")
    a("**Pour activer** : valider ce draft → création live en PAUSED via MCP Meta → "
      "puis passage PAUSED→ACTIVE à la main.")
    return "\n".join(L)
