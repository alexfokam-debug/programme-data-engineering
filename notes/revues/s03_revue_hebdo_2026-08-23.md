# Revue hebdomadaire — Semaine 2
Date : 23 août 2026

## Erreurs

| Symptôme | Cause | Correction | Règle à retenir |
|---|---|---|---|
| `pytest: command not found` ou tests lancés avec le mauvais Python | Le test n'était pas exécuté avec l'interpréteur du venv | Utiliser `python -m pytest ...` après activation du venv | `python -m <module>` garantit qu'on utilise le module associé à l'interpréteur Python courant |
| ImportError sur `python.effective_python...` | Les dossiers Python n'étaient pas reconnus comme packages | Ajouter `python/__init__.py` et `python/effective_python/__init__.py` | Pour importer proprement depuis un package Python, vérifier la structure des modules et packages |
| Fichiers `__pycache__/*.pyc` ajoutés au commit | `git add` avait stagé des fichiers générés automatiquement avant la mise à jour du `.gitignore` | Retirer les fichiers du staging et ajouter `__pycache__/` et `*.pyc` au `.gitignore` | Toujours contrôler `git status` et `git diff --cached` avant un commit |

## Statut

| Bloc | Statut | Preuve |
|---|---|---|
| Python — Effective Python items 4 à 6 | Terminé | `python/effective_python/s02_items_04_06.py`, `test/test_s02_items_04_06.py`, tests pytest réussis, commit `dff49e1` |
| SQL Cookbook — recette 1.6 | Terminé | `sql/sql-cookbook/chapitre-01/recette-01-06-bigquery.sql`, commit `fe26e07` |
| SQL Cookbook — recette 1.8 | Non commencé / non conservé | Aucun fichier `recette-01-08-bigquery.sql` trouvé dans le dépôt |
| BigQuery lab | Partiel | Optimisation de requête réalisée et gains observés dans BigQuery, mais aucun fichier `s02_j4_bigquery_lab.sql` n'est présent dans le dépôt |
| Git | Terminé | Commits séparés, `.gitignore` nettoyé, caches Python ignorés, working tree propre |

## Jalon

### Décision
Partiellement atteint.

### Ce qui est validé
- Une requête BigQuery initiale a été comparée à une version optimisée.
- La réduction des colonnes a diminué le volume de données traité.
- Les informations de job ont été utilisées pour observer le coût d'exécution.
- La table source a été vérifiée comme non partitionnée.
- Le comportement du filtre temporel a été observé sur cette table non partitionnée.

### Ce qui manque
- Le fichier `sql/s02_j4_bigquery_lab.sql` n'est pas présent dans le dépôt.
- Aucune requête locale de création ou d'utilisation de `study_bigquery.mv_daily_category` n'a été retrouvée.
- Le jalon ne peut donc pas être déclaré complètement atteint avec preuve reproductible.

### Action corrective
Créer ou reconstruire le lab BigQuery dans un fichier SQL versionné, puis créer/tester `study_bigquery.mv_daily_category` et consigner :
- les octets traités ;
- les informations de slots ;
- l'intérêt de la vue matérialisée ;
- la comparaison avec la requête non matérialisée.

## Semaine suivante

| Priorité | Action | Premier créneau | Livrable | Risque principal |
|---|---|---|---|---|
| 1 | Databricks plateforme et compute | Fait | `notes/s03_j1_db_associate_plateforme_compute.md` | Confusion entre Jobs et Compute |
| 2 | Effective Python items 7 à 9 | Prochaine séance Python | Fichier d'exercices + tests | Aller trop vite sans comprendre les idiomes Python |
| 3 | SQL Cookbook — prochaine séance dédiée | Prochaine séance SQL | Nouvelle recette SQL versionnée | Mélanger SQL Cookbook et lab BigQuery |