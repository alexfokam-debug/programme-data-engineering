# Revue hebdomadaire — Semaine 5

Date de référence : 11/09/2026  
Phase : Phase 0  
Focus : DB Associate — transformations et modélisation SQL/PySpark  
Durée de revue : 45 minutes

> Note : cette revue est complétée lors de la reprise du programme.
> Les preuves Git et CI correspondent à l'état effectivement présent dans le dépôt.

---

## 1. Erreurs et hésitations

| Erreur / hésitation | Cause | Correction | Prévention |
|---|---|---|---|
| Penser qu'un tri sur `customer_id` et `order_total` suffisait pour garantir toujours le même ordre lorsque plusieurs commandes ont les mêmes valeurs | Une égalité sur toutes les clés de tri laisse plusieurs ordres possibles entre les lignes concernées | Ajouter une clé de départage déterministe, par exemple `order_id ASC` | Pour chaque `ORDER BY`, vérifier si les colonnes utilisées permettent d'identifier un ordre unique ; sinon ajouter une dernière clé stable |
| Confondre le rôle de `ruff check` et de `ruff format`, notamment en essayant d'utiliser `--fix` avec `ruff format` | Le linting et le formatting ont été abordés au même moment alors qu'ils correspondent à deux opérations différentes | Utiliser `ruff check ... --fix` pour les corrections de lint automatisables et `ruff format ...` pour appliquer le formatage ; utiliser `ruff format --check ...` en CI | Retenir la chaîne : `ruff format --check` = format, `ruff check` = lint, `pytest` = comportement |
| La CI GitHub fonctionnait localement mais échouait sur le runner car la commande référençait à la fois `test` et un dossier local `tests` vide | Git ne versionne pas les dossiers vides ; `tests/` existait sur le Mac mais pas après un checkout propre sur GitHub | Uniformiser la structure des tests et faire exécuter à la CI uniquement les chemins réellement versionnés | Avant de valider une CI, raisonner comme sur un clone neuf : tout fichier ou dossier nécessaire doit être versionné ou créé explicitement |

### Enseignements principaux

1. Un résultat SQL n'est déterministe que si le `ORDER BY` permet réellement de départager les lignes.
2. Un linter, un formatter et un framework de tests répondent à des problèmes différents.
3. Une CI doit être reproductible sur une machine vierge et ne doit pas dépendre d'éléments présents uniquement sur la machine locale.

---

## 2. Statut de la semaine

| Composante | Statut | Preuve identifiable | Prochaine action |
|---|---|---|---|
| Effective Python 13-15 | **Terminé** | `python/effective_python/s05_items_13_15.py`, `test/test_s05_items_13_15.py` puis structure de tests normalisée ; commit `33e21c5` | Continuer avec les items suivants prévus par le programme |
| SQL Cookbook chapitre 2 | **Partiel** | `sql/sql-cookbook/chapitre-02/recette-02-01-bigquery.sql` et `recette-02-05-bigquery.sql` existent ; principe de la recette 2.2 compris mais TP volontairement non réalisé | Traiter uniquement les recettes apportant une difficulté nouvelle ; vérifier le statut de la recette 2.6 |
| Recette 2.2 — tri multicolonne | **Acquis conceptuellement / TP non réalisé** | Validation manuelle du tri `customer_id ASC`, `order_total DESC`, `order_id ASC` | Ne pas consacrer une séance complète à ce TP ; réutiliser le concept dans une requête plus complexe |
| Mini-projet / Git | **Terminé pour le jalon actuel** | Historique Git nettoyé, `main` et `study` structurées, PR `study → main`, commits atomiques | Conserver `main` stable et utiliser `study` comme branche d'intégration |
| GitHub Action de qualité | **Terminé** | `.github/workflows/lint.yml`, `requirements-dev.txt`, CI exécutée avec Ruff et pytest | Ajouter progressivement d'autres contrôles seulement lorsqu'ils deviennent utiles |
| Ruff / formatage Python | **Terminé** | `ruff==0.16.8`, `ruff format --check`, `ruff check` | Appliquer les mêmes commandes avant chaque PR importante |
| Tests Python | **Terminé** | 14 tests pytest passés | Continuer à ajouter des tests avec les prochains exercices Python |
| Transformations Databricks | **Terminé / à consolider** | `databricks/notebooks/s05_j1_transformations_medallion_quality.ipynb` et `s05_j2_transformations_architecture.ipynb` | Refaire ultérieurement le pipeline sur un jeu de données différent sans suivre les notes |
| Notes transformations | **Présentes** | `notes/s05_j1_transformations_medaillon_quality.md` et `notes/s05_j2_transformations_architecture.md` | Compléter les notes si une capacité du jalon reste insuffisamment documentée |

---

## 3. Vérification du jalon DB Associate

### Bronze → Silver → Gold

- [x] Capacité travaillée
- Preuve :
  - `databricks/notebooks/s05_j1_transformations_medallion_quality.ipynb`
  - `databricks/notebooks/s05_j2_transformations_architecture.ipynb`
- Compréhension attendue :
  - Bronze conserve les données sources avec un minimum de transformations.
  - Silver applique nettoyage, normalisation, enrichissement et contrôles.
  - Gold produit des données orientées usages métier et agrégations.

### Joins

- [x] Capacité travaillée
- Preuve : notebooks de transformations S05.
- Point important :
  - savoir choisir le type de jointure en fonction de la conservation ou non des lignes sources ;
  - éviter de perdre involontairement des événements lorsqu'une référence n'existe pas.

### Explode

- [x] Capacité travaillée
- Preuve : exercices de transformations SQL/PySpark de la semaine.
- Compréhension :
  - transformer une collection ou une structure imbriquée en plusieurs lignes lorsque le modèle cible l'exige.

### Déduplication

- [x] Capacité travaillée
- Preuve : pipeline de transformation de la semaine 5.
- Compréhension :
  - définir explicitement la clé métier ;
  - définir une règle permettant de choisir la ligne à conserver ;
  - ne pas utiliser une déduplication sans comprendre quel enregistrement est supprimé.

### Agrégations

- [x] Capacité travaillée
- Preuve : couche Gold des exercices de transformation.
- Compréhension :
  - produire des métriques à partir des données Silver ;
  - séparer les transformations techniques des indicateurs destinés aux usages métier.

### Qualité

- [x] Capacité travaillée
- Preuve :
  - notebook `s05_j1_transformations_medallion_quality.ipynb`
  - contrôles réalisés dans les transformations
  - introduction d'un quality gate Python avec Ruff + pytest dans le dépôt.
- Compréhension :
  - une ligne invalide ne doit pas nécessairement être supprimée silencieusement ;
  - les règles de qualité doivent être observables et testables ;
  - les données rejetées peuvent être isolées dans une zone de quarantaine.

---

## 4. Bilan du jalon

Le jalon principal de la semaine est atteint : le travail réalisé démontre les concepts nécessaires à une chaîne de transformation de type :

`Bronze → Silver → Gold`

avec :

- jointures ;
- transformations de structures imbriquées ;
- déduplication ;
- agrégations ;
- règles de qualité ;
- séparation des données rejetées lorsque nécessaire.

Le principal besoin de consolidation n'est plus la découverte des opérations, mais leur enchaînement autonome dans un pipeline complet sans suivre un exercice pas à pas.

Le second apprentissage important de la semaine concerne l'industrialisation du dépôt :

`code → format → lint → tests → pull request → CI`

La chaîne locale est maintenant :

`ruff format --check → ruff check → pytest`

et elle est reproduite par GitHub Actions.

---

## 5. Git et qualité logicielle

### Structure retenue

Branches permanentes :

- `main` : état stable et validé ;
- `study` : progression courante du programme.

Workflow :

`travail → commit atomique → push study → PR study vers main → CI → merge`

Des branches temporaires pourront être utilisées lorsqu'une modification justifie une isolation supplémentaire, puis supprimées après fusion.

### Contrôles actuellement utilisés

```bash
python -m ruff format --check python tests
python -m ruff check python tests
python -m pytest