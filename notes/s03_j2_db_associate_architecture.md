# S03 J2 — Databricks Associate Architecture

## Plateforme

Chaîne logique :

utilisateur → workspace / notebook → compute → tables Delta → Unity Catalog

- Workspace : espace de travail pour créer et organiser notebooks, requêtes et autres objets.
- Compute : ressources qui exécutent réellement le code.
- Delta Lake : couche de table fiable avec transactions, historique et Time Travel.
- Unity Catalog : gouvernance, organisation, permissions, découverte, audit et lineage.

## Compute

- Exploration PySpark interactive → Serverless notebook compute
- BI / analytique SQL → SQL Warehouse Serverless
- Job automatisé → Serverless job compute
- Besoin de configuration spécifique incompatible avec serverless → Classic compute

## Delta Lake

La table Delta permet notamment :
- des écritures transactionnelles ;
- le contrôle du schéma ;
- l’historique des opérations ;
- le Time Travel.

Commandes observées :

```sql
DESCRIBE HISTORY workspace.default.study_compute_events_s03;
```

```sql
SELECT *
FROM workspace.default.study_compute_events_s03
VERSION AS OF 0;
```

Règle à retenir :
Time Travel permet de consulter un ancien état d’une table Delta. Il ne mesure pas le temps d’exécution d’une requête.

## Unity Catalog

Hiérarchie :

catalog.schema.object

Exemple :

production.finance.transactions

- Catalog : production
- Schema : finance
- Table : transactions

Managed table :
Databricks gère les métadonnées et le cycle de vie des données.

External table :
les données restent dans un stockage externe contrôlé séparément, tandis que Unity Catalog gère notamment les métadonnées et la gouvernance.

Permissions importantes :
- USE CATALOG
- USE SCHEMA
- SELECT
- MODIFY

## Architecture médaillon

Bronze → Silver → Gold

### Bronze
Données brutes et proches de la source.

Dans le lab :
- 6 lignes
- présence volontaire d’un doublon
- présence volontaire d’un statut invalide

### Silver
Données nettoyées, validées et dédupliquées.

Transformations appliquées :
- suppression du doublon ;
- exclusion du statut INVALID ;
- conversion de la date.

Résultat :
- 4 lignes

### Gold
Données préparées pour un usage métier ou BI.

Agrégation :
- date ;
- statut ;
- nombre d’événements ;
- montant total.

Résultat :
- 3 lignes

## Questions de synthèse

1. Rôle de Delta Lake :
Fournir des tables fiables et transactionnelles, avec notamment historique et Time Travel.

2. Rôle de Unity Catalog :
Organiser, gouverner et contrôler l’accès aux données et objets Databricks.

3. Différence Silver / Gold :
Silver applique les règles de qualité et de nettoyage ; Gold prépare les données pour les usages métier et analytiques.

4. Rôle du Time Travel :
Consulter un ancien état d’une table Delta à partir d’une version ou d’un timestamp.

5. Compute pour une requête BI SQL :
SQL Warehouse Serverless.

## Confusion rencontrée

Confusion :
J’ai associé le Time Travel au temps d’exécution d’une requête.

Correction :
Le Time Travel concerne l’historique des données d’une table Delta. Le temps d’exécution se consulte dans le Query Profile ou les informations d’exécution.

Règle à retenir :
Query Profile = comment la requête s’est exécutée.
Time Travel = à quoi ressemblait la table auparavant.

## Flashcards

Q : Que contient Bronze ?
R : Les données brutes, proches de la source et rejouables.

Q : Quel est le rôle de Unity Catalog ?
R : Organiser, gouverner et contrôler l’accès aux données et objets.

Q : Quelle est la différence entre VERSION AS OF et RESTORE ?
R : VERSION AS OF consulte un ancien état ; RESTORE remet la table dans cet état.