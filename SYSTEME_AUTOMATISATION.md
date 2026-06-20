# Spécification — Système d'automatisation e-commerce (mass testing)

> Document à donner à Claude Code. Il décrit le système complet à construire,
> dans l'ordre, avec les contraintes techniques et les points de validation humaine.
> Les champs `[À REMPLIR]` doivent être complétés avant le premier run.

---

## 0. Objectif global

Construire une chaîne d'automatisation pour du mass testing produit en e-commerce vêtements.
Le système surveille des boutiques concurrentes, détecte les nouveaux produits,
génère des fiches produits adaptées à ma marque (texte + images IA), prépare l'import
Shopify, et prépare les campagnes Facebook Ads.

**Principe directeur : la machine prépare tout, l'humain valide ce qui engage de l'argent.**
Je garde un œil sur la production. Le système me fait gagner du temps et de la vitesse
d'exécution, il ne me remplace pas sur les décisions à coût réel (mise en ligne, budget pub).

---

## 1. Architecture générale

### Un seul dépôt Git
Tout le système vit dans le dépôt `shop-automation` (déjà créé, privé).
Raison : les blocs partagent des données et les règles de marque (`CLAUDE.md`).

### Contraintes techniques imposées par les Routines Claude Code
- Une routine tourne sur l'infra cloud d'Anthropic, **pas en local**. Elle ne voit
  que le dépôt Git qu'on lui connecte. Donc toute donnée persistante (liste de
  concurrents, mémoire des produits vus) doit être **commitée dans le dépôt**.
- Une routine **n'a aucune mémoire** d'un run à l'autre. La persistance passe
  uniquement par des fichiers versionnés dans le dépôt.
- Fréquence minimale : **une fois par heure**. Pour ce système : **quotidien**.
- Plan Max : **15 runs/jour** disponibles. Suffisant pour la veille + déclenchements.
- Higgsfield (images) est **asynchrone** : on lance des jobs, on récupère des
  `job_id`, on attend les résultats avant de les rattacher aux produits.

### Arborescence cible
```
shop-automation/
├── CLAUDE.md              # Règles permanentes de la marque (lues à chaque session)
├── concurrents.txt        # Liste des URLs concurrents à surveiller (1 par ligne)
├── config.yaml            # Paramètres centraux (prix, style image, marque)
├── data/
│   ├── vus.json           # Mémoire : produits déjà détectés (persistance)
│   ├── nouveaux.json      # Sortie quotidienne : nouveautés détectées
│   └── raw/               # Data brute scrapée (cache, évite de re-scraper)
├── veille/                # BLOC 1 — détection + scraping
├── pipeline/              # BLOC 2 — fiche produit + images + import Shopify
├── ads/                   # BLOC 3 — création campagnes Facebook
├── analyse_ads/           # BLOC 4 — analyse performance + recommandations
├── output/
│   ├── imports/           # Fichiers CSV d'import Shopify prêts
│   └── a_valider/         # Tout ce qui attend ma validation (fiches, visuels, drafts ads)
└── logs/                  # Journaux de chaque run
```

---

## 2. Règles communes (CLAUDE.md à créer)

À placer à la racine. Remplir tous les `[À REMPLIR]`.

```markdown
# Boutique — règles permanentes

## Plateforme & import
- Plateforme : Shopify
- Format d'import CSV (en-têtes exacts) : [À REMPLIR — coller la 1re ligne d'un export Shopify réel]
- Granularité : une ligne par variante

## Concurrents
- Surveillés via concurrents.txt (1 URL de boutique/collection par ligne)

## Voix de marque
- Ton : [À REMPLIR]
- Langue : [À REMPLIR]
- Longueur description : [À REMPLIR, ex. 60-90 mots]
- À privilégier / à éviter : [À REMPLIR]

## Prix
- Règle : [À REMPLIR, ex. prix concurrent x1.4, arrondi .99]
- Devise : [À REMPLIR]

## Variantes
- Tailles : [À REMPLIR]
- Couleurs : [À REMPLIR]

## Images — via MCP Higgsfield
- Modèle : [À confirmer au 1er run, ex. marketing_studio_image]
- Style : [À REMPLIR — fond, ambiance, produit seul ou mannequin, dimensions]
- 1 image par produit (+ 1 par couleur si demandé)

## Facebook Ads — via MCP Meta Ads
- Compte publicitaire : [À REMPLIR]
- Page Facebook / IG : [À REMPLIR]
- Budget de test par produit : [À REMPLIR]
- Audience(s) par défaut : [À REMPLIR]

## Règle absolue
La data concurrente (textes, images) sert UNIQUEMENT de référence pour générer
mes propres contenus. Jamais réutilisée telle quelle (droit d'auteur).
```

---

## 3. BLOC 1 — Veille & scraping (routine quotidienne)

### Rôle
Chaque jour : détecter les nouveaux produits chez les concurrents, scraper leur data complète.
**Ne met rien en ligne. Ne dépense rien.** Il liste et prépare.

### Logique
1. Lire `concurrents.txt`.
2. Pour chaque boutique : lister les produits actuellement en ligne.
3. Comparer à `data/vus.json`.
4. Pour chaque NOUVEAU produit, scraper : titre, prix, description, matières,
   tailles disponibles, variantes couleur, URLs des images de référence.
5. Écrire les nouveautés dans `data/nouveaux.json`.
6. Mettre à jour `data/vus.json`.
7. Commit + résumé des nouveautés trouvées.

### Robustesse exigée
- Délai entre requêtes (anti-blocage).
- Fallback si la structure d'un site change + log clair de l'échec.
- Option « coller le HTML manuellement » pour un site qui bloque le bot.
- Cache du brut dans `data/raw/` pour ne pas re-scraper inutilement.

### Note
Le scraping en routine s'exécute depuis le cloud Anthropic (IP différente du local).
Tester chaque concurrent en session manuelle AVANT de l'ajouter à la routine.

---

## 4. BLOC 2 — Pipeline produit (préparation, déclenché)

### Rôle
Transformer les nouveautés détectées en fiches produits prêtes pour ma boutique.
**S'arrête à "prêt à valider". Ne publie pas seul en phase 1.**

### Logique
1. Lire `data/nouveaux.json` + `CLAUDE.md`.
2. Pour chaque produit :
   - Réécrire titre + description dans ma voix de marque (jamais de copier-coller).
   - Générer titre SEO, meta description, tags.
   - Appliquer ma règle de prix.
   - Mapper tailles + couleurs vers ma structure de variantes.
   - Générer les images via **MCP Higgsfield** (référence = data concurrente, pas réutilisation).
     Gérer l'asynchrone : lancer les jobs, suivre les `job_id`, rattacher au bon produit/couleur.
3. Construire le CSV d'import au format EXACT Shopify (une ligne par variante).
4. Déposer dans `output/a_valider/` : la fiche, les visuels, le CSV.
5. Me notifier : "X produits prêts à valider."

### Validation humaine (phase 1)
Le push Shopify ne se fait qu'après mon OK. Une fois validé, le bloc importe sur Shopify
(via MCP Shopify ou import CSV).

---

## 5. BLOC 3 — Facebook Ads (préparation, déclenché)

### Rôle
Pour un produit mis en ligne, préparer la campagne de test Facebook.
**Engage de l'argent réel → validation humaine obligatoire en phase 1 et 2.**

### Logique
1. Récupérer le produit publié (lien Shopify, visuels, prix).
2. Construire le draft de campagne via **MCP Meta Ads** :
   - Créative (visuel + texte d'accroche dans ma voix de marque).
   - Audience par défaut (depuis CLAUDE.md).
   - Budget de test défini.
   - Campagne créée en **PAUSED**.
3. Déposer le récap dans `output/a_valider/`.
4. Me notifier : "Campagne prête, en pause. Valider pour activer."

### Règle de sécurité
Aucune campagne n'est activée automatiquement en phase 1 ni 2.
L'activation (passage PAUSED → ACTIVE) est une action humaine.

---

## 6. BLOC 4 — Analyse des ads (routine, recommande puis agit)

### Rôle
Surveiller les performances des campagnes actives et recommander des actions :
couper, améliorer, scaler, ou laisser tourner.

### Logique (phase recommandation)
1. Routine quotidienne : récupérer les métriques des campagnes actives via MCP Meta Ads
   (dépense, CTR, CPC, CPA, ROAS, conversions).
2. Évaluer selon des seuils définis (à fixer avec moi) :
   - Sous-performe → recommander COUPER.
   - Performe bien → recommander SCALER (et de combien).
   - Marge d'amélioration → recommander un ajustement (créative, audience, budget).
   - Stable / en apprentissage → LAISSER TOURNER.
3. Écrire un rapport dans `output/a_valider/` + me notifier.

### Évolution (phase 3, après validation du système)
Une fois que les recommandations se sont avérées fiables sur du réel, on autorise
le bloc à **agir seul** sur les actions les moins risquées (couper une campagne qui
brûle sans convertir), en gardant le scaling de budget sous contrôle plus longtemps.

---

## 7. Déploiement par phases (IMPORTANT)

Construire la chaîne complète, mais **activer l'automatisation progressivement** :

| Phase | Ce qui est auto | Ce que je valide à la main |
|-------|-----------------|----------------------------|
| **1 — Rodage** | Veille, scraping, fiche, images, CSV, draft ads | Mise en ligne Shopify + activation ads |
| **2 — Confiance** | + mise en ligne Shopify auto | Activation ads uniquement |
| **3 — Maturité** | + coupe ads auto sur seuils, scaling assisté | Scaling de gros budgets |

Raison : chaque maillon a un taux d'erreur. Enchaînés sans contrôle, les erreurs se
cumulent et finissent en budget pub dépensé sur une fiche fausse. On enlève les
validations une par une, en commençant par les moins risquées.

---

## 8. Exigences transverses

- **Langue du code et des commentaires** : commenté clairement, modulaire (un dossier par bloc).
- **config.yaml central** : toutes mes règles (prix, ton, style image, seuils ads) au même endroit.
- **Logs** : chaque run journalisé dans `logs/` (quoi détecté, quoi généré, quoi échoué).
- **Reprise** : un run interrompu doit pouvoir reprendre sans tout refaire.
- **Mode --dry-run** : tout préparer SANS générer d'images Higgsfield (coûteux) ni toucher Shopify/Ads.
- **MCP requis** : Higgsfield (images), Shopify (boutique), Meta Ads (pub). À connecter aux routines concernées.
- **Droit d'auteur** : données concurrentes = référence seulement, jamais de réutilisation directe.

---

## 9. Ordre de construction (ce que je te demande de faire, étape par étape)

1. **Lis CLAUDE.md et config.yaml.** Si vides, demande-moi les infos manquantes avant de coder.
2. **Propose l'arborescence** complète et attends mon OK.
3. **Construis le BLOC 1 (veille)** et teste-le sur **UN SEUL concurrent**. Montre-moi
   le `data/nouveaux.json` obtenu avant de généraliser.
4. Quand la veille est validée sur tous les concurrents → **on crée la routine quotidienne**.
5. **Construis le BLOC 2 (pipeline)** en `--dry-run` d'abord (1 produit, sans images réelles).
   Montre-moi la fiche + le format CSV. Puis active Higgsfield sur 1 produit test.
6. **Construis le BLOC 3 (ads)** : draft en PAUSED, déposé pour validation. Rien d'activé.
7. **Construis le BLOC 4 (analyse ads)** en mode recommandation seule.
8. À chaque bloc : logs, dry-run, et point de validation humaine respectés.

**Ne déclenche aucune dépense (images, budget pub) ni mise en ligne sans mon OK explicite
tant qu'on est en phase 1.**

---

## 10. À me demander avant de commencer

Si ces infos ne sont pas dans CLAUDE.md / config.yaml, demande-les-moi :
- En-têtes exacts d'un export Shopify réel
- Liste des URLs concurrents
- Ton, langue, longueur des descriptions
- Règle de prix + devise
- Référentiel tailles + couleurs
- Style d'image voulu (produit seul / mannequin, fond, dimensions)
- Compte pub Meta, page FB/IG, budget de test, audience par défaut
- Seuils ads (à partir de quand couper / scaler)
