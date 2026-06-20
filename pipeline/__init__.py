"""BLOC 2 — Pipeline produit.

Transforme les nouveautés détectées (data/nouveaux.json) en fiches produits
prêtes pour la boutique : réécriture voix de marque, prix, mapping variantes,
puis CSV d'import Shopify. S'arrête à « prêt à valider » : ne publie pas seul,
ne génère aucune image en phase 1 (dry-run).
"""
