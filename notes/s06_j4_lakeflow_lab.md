ingestion
    ↓
transformation
    ↓
quality_check
    ↓
aggregation


| Tâche | Entrée | Sortie | Dépendance | En cas d’échec |
|---|---|---|---|---|
| `ingestion` | fichiers JSON synthétiques | données brutes disponibles | aucune | le workflow s’arrête avant transformation |
| `transformation` | données brutes | données nettoyées / typées | `ingestion` | retry possible, sinon tâches downstream bloquées |
| `quality_check` | données transformées | statut qualité / données invalides identifiées | `transformation` | échec ou quarantaine selon la règle |
| `aggregation` | données valides | indicateur quotidien par catégorie | `quality_check` | pas d’agrégat produit si la qualité n’est pas validée |

## Incident contrôlé

| Signal | Cause probable | Vérification | Correction |
|---|---|---|---|
| `silver_json_events` en échec | Une ligne viole une expectation configurée en `FAIL` | Consulter les expectations et identifier `reasonable_event_id` | Modifier la stratégie de traitement de cette anomalie puis relancer |
| Gold non rafraîchie | Silver n'a pas terminé correctement | Vérifier le graphe de dépendances | Corriger Silver puis exécuter une reprise |

## Résultat final du pipeline

| Dataset | Type | Nombre de lignes | Rôle |
|---|---|---:|---|
| `bronze_json_events` | Streaming Table | 7 | Conserver les événements JSON reçus |
| `silver_json_events` | Streaming Table | 5 | Conserver uniquement les événements valides |
| `quarantine_json_events` | Streaming Table | 2 | Isoler les événements invalides |
| `gold_json_daily_metrics` | Materialized View | 2 | Produire les indicateurs quotidiens par catégorie |

### Arrivées incrémentales

Premier lot :

- `batch_01.json`
- 3 événements

Deuxième lot :

- `batch_02.json`
- 3 nouveaux événements
- une ligne invalide avec `amount = -200`

Troisième lot :

- `batch_03.json`
- une ligne volontairement invalide avec `event_id = 9999`

Le pipeline a traité progressivement les nouveaux fichiers via Auto Loader.

## Incident contrôlé et reprise

Une règle stricte a été ajoutée :

`event_id < 1000`

Elle a d'abord été configurée avec `expect_or_fail`.

La ligne `event_id = 9999` a provoqué l'échec de `silver_json_events`.

Diagnostic :

1. le fichier JSON a été correctement ingéré par Bronze ;
2. l'erreur se situait dans Silver ;
3. l'expectation `reasonable_event_id` était en échec ;
4. Gold ne pouvait pas être correctement rafraîchie en aval.

Correction :

La règle a été remplacée par `expect_or_drop`.

La quarantaine a été étendue pour identifier :

`event_id >= 1000`

Après reprise :

- Bronze : 7 lignes
- Silver : 5 lignes
- Quarantine : 2 lignes
- Gold : 2 lignes
- pipeline : SUCCESS

### Apprentissage

Une anomalie de données ne doit pas nécessairement provoquer l'arrêt complet d'un pipeline.

Le choix entre `warn`, `drop`, `quarantine` et `fail` dépend de la criticité de la règle.

## Orchestration Lakeflow Jobs

```text
prepare_json_source
        ↓
run_json_pipeline
        ↓
validate_quality
        ↓
validate_aggregation