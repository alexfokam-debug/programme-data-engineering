# S06 J1 — Lakeflow Jobs et Spark Declarative Pipelines

## Objectifs de la séance

1. Orchestrer un workflow avec Lakeflow Jobs.
2. Définir un pipeline déclaratif avec bronze, silver et gold.
3. Interpréter le monitoring d'un job et d'un pipeline.

## Architecture

source
  ↓
bronze
  ↓
silver
  ↓
gold
  ↓
validation

### Rôle des composants

- Lakeflow Jobs orchestre les tâches du workflow.
- Spark Declarative Pipelines décrit les transformations de données et leurs dépendances.
- Bronze, Silver et Gold peuvent être gérés dans un même pipeline déclaratif.
- Une tâche de validation peut être exécutée après le pipeline par Lakeflow Jobs.

| Tâche | Responsabilité | Entrée | Sortie | Condition de succès |
|---|---|---|---|---|
| ingestion | Générer/préparer les événements synthétiques | aucune | source d’événements | données disponibles |
| transformation | Construire bronze, silver et gold | source d’événements | tables transformées | pipeline terminé sans erreur |
| contrôle_qualité | Vérifier le résultat final | tables produites | statut de validation | contrôles réussis |

Hardcoding
→ valeur directement dans le code
→ moins flexible

Parameter
→ valeur fournie au moment de l'exécution
→ code réutilisable
→ plus simple à automatiser
→ plus simple pour les reruns

## Monitoring et diagnostic

### Incident simulé

Une ligne synthétique a été ajoutée avec :

- event_id = 7
- category = Phone
- amount = -500

### Signal observé

L'expectation `positive_amount` a détecté une nouvelle violation.

Le nombre de violations de cette règle est passé à 2 :

- amount = -200
- amount = -500

### Comportement du pipeline

- Bronze conserve les données reçues.
- Silver rejette les lignes dont `amount <= 0`.
- Gold ne reçoit donc pas ces données invalides.
- `quarantine_events` conserve les lignes rejetées ainsi que leur motif.

### Correction

La donnée doit être corrigée à la source ou via un processus de remédiation, puis retraitée.
La quarantaine permet d'identifier précisément les données nécessitant une correction.

## Exécution Lakeflow Jobs

Workflow final :

ingestion
    ↓
run_lakeflow_pipeline
    ↓
valide_gold

Résultat :
- ingestion : SUCCESS
- run_lakeflow_pipeline : SUCCESS
- valide_gold : SUCCESS
- job global : SUCCESS

### Observation de monitoring

Plusieurs exécutions intermédiaires du pipeline ont retourné
`InvalidClusterRequest`.

Des exécutions ultérieures ont réussi et le workflow final s'est terminé
avec le statut `Succeeded`.

Cela illustre la distinction entre :
- l'état d'une tentative individuelle ;
- l'état final de la tâche ;
- l'état final du Job.

## Triggers Lakeflow Jobs

Un trigger définit quand un Job démarre.

Principaux types :
- Scheduled : exécution planifiée dans le temps.
- Table update : exécution lorsqu'une table source est mise à jour.
- File arrival : exécution lorsqu'un nouveau fichier arrive.
- Continuous : exécution continue.

Dans ce lab, le Job est lancé manuellement avec `Run now`.

Le trigger suggéré sur `gold_daily_sales` n'a pas été utilisé car cette table
est produite par le Job lui-même. Un trigger doit idéalement être basé sur une
source amont ou sur une planification.

## Synthèse

### Trois apprentissages

1. Lakeflow Jobs orchestre le workflow alors que SDP gère le graphe déclaratif
   des transformations de données.

2. Les streaming tables sont adaptées aux traitements incrémentaux tandis que
   les materialized views sont adaptées aux résultats calculés et agrégés.

3. Les expectations permettent de mesurer, rejeter ou bloquer les données
   invalides, et une table de quarantaine permet de conserver les lignes à
   investiguer.

### Difficulté

Bien distinguer l'état FAILED d'une tâche réellement exécutée de l'état
UPSTREAM FAILED d'une tâche bloquée par une dépendance.

### Prochaine action

Approfondir les paramètres, triggers, retries et stratégies de monitoring
Lakeflow Jobs, puis reproduire l'architecture avec une source incrémentale.