# Refonte Oria Studio — Spec design

> Source de vérité de la **structure de la boutique** Oria Studio (oriastudio.store).
> Toute génération de page produit / collection par le système d'automatisation
> (BLOC 2) doit suivre cette spec. Décidée avec Lucas le 2026-06-20.

## 1. Contexte & objectif
Refonte complète d'oriastudio.store (Shopify, plan Advanced, EUR/France). L'existant
est jugé sans structure, DA/branding/marketing non satisfaisants. Objectif : une
marque **quiet luxury minimaliste**, cohérente, gérable en solo + alimentée par le
système d'automatisation (mass-testing → capsules).

## 2. Positionnement & marque
- **Direction artistique** : quiet luxury minimaliste (réf. The Row, COS).
- **Nom** : « Oria Studio » conservé ; identité (logo, typo, couleurs, voix) refaite.
- **Prix** : premium accessible (~40–70 €). « Le luxe discret sans le prix ».
- **Marketing** : hybride — premium sobre au quotidien + offres ponctuelles (ventes
  privées / avant-premières de capsules par email). **Aucun prix barré permanent.**
- **Voix** : sobre, sensorielle, intemporelle. Phrases courtes. Zéro hype, zéro emoji,
  zéro urgence. Vend le geste juste et la durabilité.

## 3. Identité visuelle
### Palette (neutres chauds)
| Rôle | Nom | Hex |
|---|---|---|
| Fond principal | Papier | `#F5F2EC` |
| Surface secondaire | Sable | `#D8CFC2` |
| Séparateurs / bordures | Taupe | `#A89A87` |
| Accent discret | Moka | `#6E6253` |
| Texte / CTA | Encre | `#2A2622` |

- CTA = **Encre** (boutons noir chaud), texte CTA = Papier. Jamais de couleur criarde.
- Liens / petits détails = Moka.

### Typographie
- **Titres** : serif éditoriale haute lisibilité — **Fraunces** (défaut) ou Cormorant
  Garamond (alt plus délicate).
- **Texte** : sans neutre — **Inter** (ou Assistant).
- **Labels / nav** : capitales espacées (letter-spacing ~3px).

### Logo
- Wordmark typographique « ORIA STUDIO » en serif espacé, monochrome (Encre sur Papier
  + version inversée Papier sur Encre). **Pas d'icône.**
- Sous-ligne optionnelle : « PARIS · ESSENTIELS INTEMPORELS ».

## 4. Structure de la home (ordre de scroll)
1. **En-tête** : logo, nav épurée (Nouveautés · Capsules · L'Édit · À propos), recherche
   discrète, panier. Barre d'annonce sobre (« Livraison offerte · Retours gratuits »),
   sans compte à rebours.
2. **Hero éditorial** : image plein écran (lifestyle mannequin), titre serif court,
   1 CTA discret. Tourne avec la capsule en cours.
3. **Capsule du moment** : 3–4 pièces héros + « Voir la capsule ». (Point de jonction
   mass-testing ↔ premium : les produits testés gagnants deviennent la capsule.)
4. **Manifeste** : 2–3 lignes (conception intentionnelle, matières, intemporel) + image.
5. **Les essentiels** : sélection (pas tout le catalogue).
6. **Réassurance** : livraison offerte · retours gratuits · paiement sécurisé · support FR.
7. **Accès prioritaire aux drops** : capture email (moteur des offres ponctuelles).
8. **Footer** : capsules · aide · légal · réseaux.

Principe transverse : **aéré, éditorial, retenu** — grandes images, peu d'éléments/écran.

## 5. Capsules & navigation
- Une **capsule = une collection Shopify**. Métafields collection : `statut` (en_cours |
  archivée), `image_hero`, `manifeste` (texte court), `ordre`.
- « Capsule du moment » = collection marquée `statut=en_cours` (réglage thème ou metaobject).
- Les drops **tournent** : nouvelle capsule → on bascule le `statut`.
- **Alimentation par l'automatisation** : BLOC 2 tague les produits validés dans la
  collection-capsule cible (tag `capsule:<slug>`), set les métafields produit.
- Navigation : Nouveautés (derniers ajouts), Capsules (liste des collections actives),
  L'Édit (sélection éditoriale), À propos.

## 6. Page produit (PDP) — gabarit réutilisable
Colonne gauche : **galerie éditoriale** (porté mannequin + détails matière, plusieurs images).
Colonne droite (sticky) :
- Label capsule (caps espacées) `CAPSULE · <nom>`
- Titre (serif) — format `[vêtement] [coupe] en [matière]`
- Prix net (pas de barré permanent ; si offre active → badge sobre + prix offre)
- Description courte (voix : accroche + matière + coupe + entretien condensés)
- Couleur (pastilles) · Taille (XS–XXXL, ruptures grisées non masquées)
- « Guide des tailles »
- CTA **Ajouter au panier** (Encre, pleine largeur)
- Réassurance (livraison/retours)
- Accordéons **fermés** : Détails & matière · Le bon geste d'entretien · Livraison & retours
Sous le pli :
- **Storytelling matière & entretien** (grande image + texte voix de marque)
- **Compléter la capsule** : 3–4 pièces de la même capsule (pas un « vous aimerez aussi » générique)
- Avis : **réels uniquement** (discrets) ou absents. Jamais de faux avis.

Les accordéons et le storytelling se nourrissent de **métafields produit** : `matiere`,
`entretien`, `coupe`, `capsule`.

## 7. Page collection / capsule
- En-tête capsule : image hero + nom + manifeste (depuis métafields collection).
- Grille produits sobre (2 col mobile / 3–4 desktop), beaucoup de blanc.
- Filtres discrets (taille, couleur) si volume le justifie.

## 8. Mécanique marketing (hybride, conforme)
- **Aucun prix barré permanent.** `compare_at` utilisé UNIQUEMENT pendant une vraie
  promo time-boxée, avec prix de référence réel (Directive Omnibus / Code conso FR).
- **Offres** = ventes privées / avant-premières de capsules, diffusées par **email**
  (capture section 7). Sur le site : capsule promue proprement, badge sobre, durée limitée.
- Outils : Shopify Forms ou Klaviyo pour l'email ; codes de réduction Shopify pour les
  ventes privées.
- Pas d'urgence factice (pas de faux stock, pas de faux compteurs).

## 9. Implémentation technique
- **Plateforme** : Shopify OS2 (natif, géré depuis l'admin + l'automatisation).
- **Thème base** : **Dawn** (gratuit, OS2, performant, sections flexibles) fortement
  customisé. Alt : thème premium minimaliste si besoin.
- **Sections** : home en sections OS2 (hero, capsule à la une, manifeste, sélection,
  réassurance, email, footer). Templates produit + collection custom.
- **Métafields** : collection (`statut`, `image_hero`, `manifeste`, `ordre`) ; produit
  (`matiere`, `entretien`, `coupe`, `capsule`).
- **Fonts** : Fraunces (titres) + Inter (texte) via réglages typo du thème.
- **Perf** : mobile-first, LCP < 2,5 s, images en bon format (WebP), lazy-load.

## 10. Migration de l'existant
- Restyler les produits existants sous le nouveau thème.
- Re-taguer en capsules ; remplir les métafields.
- Remplacer les visuels par des shots **mannequin porté** (cf. flux Higgsfield validé).
- Réécrire les descriptions dans la voix raffinée.
- **URLs/handles conservés** (domaine gardé) → SEO préservé ; redirections seulement si
  une URL change.

## 11. Phasing (ordre de construction)
1. Identité + setup thème (palette, fonts, logo, réglages).
2. Sections home.
3. Gabarits PDP + collection + métafields.
4. Migration produits existants (restyle, capsules, images, copie).
5. Moteur marketing (capture email, mécanique d'offres).
6. QA (mobile, perf, légal, conversion) + mise en ligne (validée à la main).

## 12. Hors périmètre (YAGNI)
Headless/Next.js, checkout custom, programme de fidélité, multi-langue (FR seul pour
l'instant), blog (plus tard), wishlist.

## 13. Critères de succès
- Identité quiet luxury cohérente et appliquée partout.
- Structure en capsules fonctionnelle, alimentable par l'automatisation.
- Gabarit PDP réutilisable tel quel par le BLOC 2 pour générer des fiches conformes.
- Zéro barré permanent ; conformité prix de référence FR.
- Mobile-first performant (LCP < 2,5 s).
