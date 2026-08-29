## Synthèse — S03 J1 Databricks Platform & Compute

### 3 acquis

1. Je sais distinguer les principaux composants de la plateforme Databricks :
   - Workspace = espace de travail
   - Compute = ressources d'exécution
   - Unity Catalog = gouvernance et organisation des données
   - Delta Lake = gestion fiable et versionnée des tables

2. Je sais choisir le compute adapté selon le besoin :
   - Notebook interactif → Serverless notebook compute
   - BI / SQL analytique → SQL Warehouse Serverless
   - Pipeline automatisé → Serverless job compute
   - Configuration spécifique incompatible avec serverless → Classic compute

3. Je comprends les bases de Delta Lake :
   - `DESCRIBE DETAIL` permet d'inspecter les caractéristiques d'une table.
   - `DESCRIBE HISTORY` permet de consulter son historique.
   - `VERSION AS OF` permet de lire une ancienne version grâce au Time Travel.

### 2 limitations de Databricks Free Edition

1. Free Edition utilise principalement le compute serverless et ne permet pas de tester librement un Classic compute configuré manuellement.

2. L'environnement est limité par rapport à une édition Databricks complète, notamment concernant certains types de compute et certaines configurations avancées.

### Question à revoir

Quelle est la différence précise entre consulter une ancienne version avec `VERSION AS OF` et restaurer réellement une table Delta avec `RESTORE` ?

### Observation du lab

- Les données utilisées étaient entièrement synthétiques.
- La vue temporaire contenait 5 lignes.
- L'agrégation SQL et l'agrégation PySpark ont produit le même résultat : 3 catégories.
- PySpark a pris légèrement plus de temps que SQL sur ce très petit jeu de données.
- Cette différence n'est pas suffisante pour conclure que SQL est globalement plus performant que PySpark.
- La table persistante créée était au format Delta.
- Après un `UPDATE`, deux versions de la table étaient visibles dans l'historique.
- Le Time Travel a permis de consulter l'état précédent de la table sans modifier son état actuel.