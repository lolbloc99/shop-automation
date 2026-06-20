"""Rendu de la fiche produit lisible (Markdown) déposée dans output/a_valider/.

Sert au point de validation humaine : l'humain lit la fiche, voit le prix, les
variantes, le prompt image (non généré en dry-run) et les avertissements, puis
décide. Rien n'est poussé sur Shopify ici.
"""

from __future__ import annotations


def _euro(x) -> str:
    return f"{x:.2f} €" if x is not None else "—"


def render(product, contenu, variantes, warnings, cfg, dry_run, used_template) -> str:
    ps = product.get("prix_source", {})
    lignes = []
    a = lignes.append

    a(f"# {contenu.get('titre','')}")
    a("")
    if dry_run:
        a("> **DRY-RUN — à valider.** Aucune image générée, rien poussé sur Shopify. "
          "Fiche + CSV en attente de ta validation manuelle (phase 1).")
        a("")
    if used_template:
        a("> ⚠️ **Rédaction manquante** : brouillon template affiché. "
          "Le contenu voix-de-marque doit être rédigé avant validation.")
        a("")

    a(f"- **Référence concurrent** (ne pas réutiliser) : {product.get('source_url','')}")
    a(f"- **Catégorie** : {product.get('categorie','')}  ·  **Type** : {contenu.get('type','')}")
    a(f"- **Handle** : `{contenu.get('handle','')}`")
    a("")

    a("## Description (voix de marque)")
    a(contenu.get("description_html", ""))
    a("")

    a("## SEO")
    a(f"- **Titre SEO** : {contenu.get('seo_title','')}")
    a(f"- **Meta description** : {contenu.get('seo_desc','')}")
    a(f"- **Tags** : {', '.join(contenu.get('tags', []))}")
    a("")

    a("## Prix")
    mult = cfg["prix"]["multiplicateur"]
    a(f"- Source concurrent : {_euro(ps.get('montant'))} "
      f"(barré source : {_euro(ps.get('compare_at'))})")
    a(f"- Règle appliquée : ×{mult}, arrondi .99  ·  "
      f"compare-at = `{cfg['prix']['compare_at']['strategie']}`")
    if variantes:
        a(f"- **Prix de vente : {_euro(variantes[0]['prix'])}** "
          f"(barré : {_euro(variantes[0]['compare_at'])})")
    a("")

    a("## Variantes")
    a("| Couleur | Taille | SKU | Prix | Barré | Stock |")
    a("|---|---|---|---|---|---|")
    for v in variantes:
        a(f"| {v['couleur'] or '—'} | {v['taille'] or '—'} | `{v['sku']}` | "
          f"{_euro(v['prix'])} | {_euro(v['compare_at'])} | {v.get('qty',0)} |")
    a("")

    a("## Image (NON générée en dry-run)")
    if contenu.get("image_prompt"):
        a("Prompt qui sera envoyé au BLOC 2 réel (recraft-v4-1, fond blanc, "
          "**sans logo ni texte**) :")
        a("")
        a("```")
        a(contenu["image_prompt"])
        a("```")
    else:
        a("_Aucun prompt image fourni._")
    a("")

    if warnings:
        a("## ⚠️ Avertissements")
        for w in warnings:
            a(f"- {w}")
        a("")

    return "\n".join(lignes)
