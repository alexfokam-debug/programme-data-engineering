# S06 J1 — Quiz Lakeflow Jobs et SDP

## 1. Quel est le rôle de Lakeflow Jobs et de SDP ?

Lakeflow Jobs orchestre les tâches, leurs dépendances et leur exécution.

Spark Declarative Pipelines permet de définir déclarativement les transformations
et les dépendances entre les datasets d'un pipeline.

## 2. Streaming table vs Materialized View

Une streaming table est adaptée à l'ingestion incrémentale de nouvelles données.

Une materialized view maintient le résultat calculé d'une requête, par exemple
une agrégation métier.

Dans le lab :
- bronze_events : streaming table
- gold_daily_sales : materialized view

## 3. Expectations

- warn : conserve la ligne et enregistre la violation.
- drop : élimine la ligne invalide.
- fail : fait échouer l'update concerné.

## 4. Que se passe-t-il si une tâche upstream échoue ?

Une tâche dépendante qui exige le succès de sa tâche upstream ne démarre pas.

Elle peut apparaître avec l'état UPSTREAM FAILED plutôt que FAILED.

## 5. Queue et concurrence

Avec Maximum concurrent runs = 1 et Queue = ON, un deuxième run demandé pendant
l'exécution du premier reste en file d'attente.

Il peut démarrer lorsque l'exécution précédente est terminée.