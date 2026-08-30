## S02 — Première table Delta

### Objectif

Construire un flux Databricks reproductible avec PySpark, SQL et Delta Lake.

### Architecture

Données synthétiques
→ DataFrame PySpark
→ Table Delta source
→ Transformation PySpark
→ Table Delta transformée
→ Contrôles SQL

### Tables

- `workspace.default.commandes_s02_source`
- `workspace.default.commandes_s02_transformees`

### Exécution

1. Ouvrir `S02_Premiere_table_Delta`.
2. Sélectionner le calcul serverless.
3. Exécuter `Run all`.
4. Vérifier le message final de succès.

### Contrôles réalisés

- Comptage des lignes.
- Agrégation par statut.
- Filtrage des commandes.
- Contrôle des valeurs nulles.
- Contrôle du montant calculé.
- Contrôle de la seconde table.

### Difficultés rencontrées

- À compléter après la séance.

### Résultat

Le notebook peut supprimer et recréer les deux tables sans intervention manuelle.