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
| SQL Cookbook — recette 1.8 | À vérifier | Vérifier l'existence du fichier et son état Git |
| BigQuery lab | Partiel | Comparaison requête initiale / optimisée réalisée, réduction importante des octets traités, table source vérifiée comme non partitionnée |
| Git | Terminé | Commits séparés, nettoyage des caches Python, `.gitignore` mis à jour, working tree propre |

## Jalon

## Semaine suivante