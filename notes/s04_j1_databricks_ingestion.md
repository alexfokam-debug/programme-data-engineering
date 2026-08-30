# Databricks — comprendre trois patterns d’ingestion

> Note pédagogique du lab S04 J1 — `COPY INTO`, Auto Loader et ingestion incrémentale par curseur.
>
> Environnement du lab : Databricks Free Edition, compute serverless, Unity Catalog, SQL et PySpark.

## Objectif

À la fin de cette note, je dois savoir répondre à quatre questions :

1. Quel pattern utiliser selon la nature de la source ?
2. Où chaque pattern conserve-t-il son état ?
3. Pourquoi une relance ne crée-t-elle normalement pas de doublons techniques ?
4. Quand choisir SQL ou PySpark dans un projet d’entreprise ?

---

## 1. La carte mentale générale

Les trois patterns ne sont pas trois syntaxes concurrentes pour un même problème. Ils répondent à trois situations différentes.

```text
PATTERN 1 — lots de fichiers

batch_001/ ─┐
batch_002/ ─┼──> COPY INTO ──> table Delta
batch_003/ ─┘
                 mémoire des fichiers déjà chargés
```

```text
PATTERN 2 — fichiers qui arrivent progressivement

stream_001/ ─┐
stream_002/ ─┼──> cloudFiles ──> table Delta
stream_003/ ─┘          │
                        └──> checkpoint = état du flux
```

```text
PATTERN 3 — lignes nouvelles ou modifiées dans une table/source

source_orders
     │
     │ WHERE updated_at > dernier_curseur
     ▼
lignes nouvelles ou modifiées
     │
     ▼
   MERGE ───────────────> table Delta cible
     │
     └── succès ────────> mise à jour du curseur
```

Raccourci de décision :

| Situation | Pattern naturel |
|---|---|
| Quelques dépôts de fichiers, ingestion déclenchée à la demande ou planifiée | `COPY INTO` |
| Beaucoup de fichiers, arrivées continues ou micro-batchs fréquents | Auto Loader |
| Une table, une base ou une API expose `updated_at`, `last_modified` ou un identifiant croissant | Curseur + `MERGE` |

---

## 2. Le décor : Unity Catalog, volume et table Delta

### 2.1 Hiérarchie Unity Catalog

```text
metastore
└── catalog : workspace
    └── schema : study_s04_ingestion
        ├── volume : landing
        ├── table  : copy_into_events
        ├── table  : autoloader_events
        └── table  : incremental_orders
```

Un schéma se nomme avec deux parties :

```text
catalog.schema
workspace.study_s04_ingestion
```

Une table ou un volume se nomme avec trois parties :

```text
catalog.schema.object
workspace.study_s04_ingestion.copy_into_events
workspace.study_s04_ingestion.landing
```

Le chemin physique d’un fichier dans un volume suit cette forme :

```text
/Volumes/<catalog>/<schema>/<volume>/<sous-dossier>/<fichier>
```

Dans le lab :

```text
/Volumes/workspace/study_s04_ingestion/landing/batch
/Volumes/workspace/study_s04_ingestion/landing/stream
/Volumes/workspace/study_s04_ingestion/landing/_checkpoints
```

### 2.2 Création du schéma

```sql
%sql
CREATE SCHEMA IF NOT EXISTS workspace.study_s04_ingestion;
```

Explication bloc par bloc :

- `%sql` indique que la cellule doit être interprétée comme du SQL.
- `CREATE SCHEMA` crée un conteneur logique dans Unity Catalog.
- `IF NOT EXISTS` rend la commande rejouable : si le schéma existe, la cellule ne doit pas échouer uniquement pour cette raison.
- `workspace` est le catalogue.
- `study_s04_ingestion` est le schéma.

### 2.3 Création du volume

```sql
%sql
CREATE VOLUME IF NOT EXISTS workspace.study_s04_ingestion.landing;
```

- `CREATE VOLUME` crée un espace gouverné par Unity Catalog pour stocker des fichiers.
- `workspace.study_s04_ingestion.landing` signifie `catalog.schema.volume`.
- Le volume contient les JSON sources et le checkpoint, mais pas les tables elles-mêmes.

### 2.4 Vérifications

```sql
%sql
SHOW SCHEMAS IN workspace;
```

Cette requête liste les schémas du catalogue `workspace`. On doit retrouver `study_s04_ingestion`.

```sql
%sql
SHOW VOLUMES IN workspace.study_s04_ingestion;
```

Cette requête liste les volumes du schéma. On doit retrouver `landing`.

### Erreur rencontrée — namespace Unity Catalog

Commande incorrecte :

```sql
CREATE SCHEMA IF NOT EXISTS workspace.default.study_s04_ingestion;
```

Erreur observée :

```text
REQUIRES_SINGLE_PART_NAMESPACE
spark_catalog requires a single-part namespace
```

Cause : `CREATE SCHEMA` attend ici `catalog.schema`, mais trois niveaux ont été fournis. `default` ajoutait un niveau inutile.

Même problème avec ce volume incorrect :

```sql
CREATE VOLUME IF NOT EXISTS workspace.default.study_s04_ingestion.landing;
```

Il contient quatre parties alors qu’un volume se nomme `catalog.schema.volume`.

Correction :

```sql
CREATE SCHEMA IF NOT EXISTS workspace.study_s04_ingestion;
CREATE VOLUME IF NOT EXISTS workspace.study_s04_ingestion.landing;
```

À retenir :

```text
schéma       = catalog.schema
table/volume = catalog.schema.object
```

---

## 3. Préparer des données synthétiques avec PySpark

### 3.1 Premier lot

```python
from datetime import datetime

batch_data = [
    (1, datetime(2026, 8, 30, 18, 0),  "A", 10.5, datetime(2026, 8, 30, 18, 1)),
    (2, datetime(2026, 8, 30, 18, 5),  "B", 20.0, datetime(2026, 8, 30, 18, 6)),
    (3, datetime(2026, 8, 30, 18, 10), "A", 15.0, datetime(2026, 8, 30, 18, 11)),
]

columns = [
    "event_id",
    "event_time",
    "category",
    "amount",
    "updated_at"
]

batch_df = spark.createDataFrame(batch_data, columns)
batch_df.display()
```

Explication :

- `from datetime import datetime` importe le type Python utilisé pour créer de vraies dates/heures.
- `batch_data` est une liste Python de trois événements synthétiques.
- Chaque tuple représente une ligne.
- L’ordre des cinq valeurs doit correspondre à l’ordre des cinq noms de `columns`.
- `spark.createDataFrame(...)` distribue ces données dans un DataFrame Spark et infère leur type à partir des objets Python.
- `batch_df.display()` permet une vérification visuelle dans Databricks. Ce n’est pas une étape d’ingestion.

Le schéma attendu est proche de :

```text
event_id    BIGINT/LONG
event_time  TIMESTAMP
category    STRING
amount      DOUBLE
updated_at  TIMESTAMP
```

### 3.2 Écriture JSON dans le volume

```python
batch_df.write \
    .mode("overwrite") \
    .json("/Volumes/workspace/study_s04_ingestion/landing/batch")
```

- `batch_df.write` ouvre l’API d’écriture batch de Spark.
- `.mode("overwrite")` remplace le contenu de ce chemin si la cellule est rejouée.
- `.json(...)` sérialise les lignes au format JSON.
- Spark écrit un **dossier** contenant un ou plusieurs fichiers `part-....json`, et non un fichier unique nommé `batch_001.json`.

Illustration :

```text
landing/batch/
├── part-00000-<identifiant>.json
├── part-00001-<identifiant>.json   # possible selon le partitionnement
└── _SUCCESS                        # possible selon la configuration
```

Attention : `overwrite` est pratique pour un lab, mais un dossier d’atterrissage de production est normalement **append-only** et ses fichiers sont immuables. Réécrire le dossier peut créer de nouveaux noms physiques ; un mécanisme qui suit les fichiers peut alors les considérer comme nouveaux.

### Erreur rencontrée — `DBFS_DISABLED`

Cellule qui a échoué dans le lab :

```python
dbutils.fs.mkdirs(batch_path)
dbutils.fs.mkdirs(stream_path)
dbutils.fs.mkdirs(checkpoint_path)
```

Erreur :

```text
[DBFS_DISABLED] Public DBFS root is disabled
```

Ce message ne signifie pas que le volume Unity Catalog n’existe pas. Dans ce contexte serverless, l’appel a été traité par une couche de système de fichiers soumise aux restrictions DBFS. Le DBFS root historique et un volume Unity Catalog ne doivent pas être confondus.

### Erreur rencontrée — `PermissionError: /volumes`

La tentative suivante a également échoué :

```python
os.makedirs(batch_path, exist_ok=True)
```

Erreur :

```text
PermissionError: [Errno 13] Permission denied: '/volumes'
```

Dans cet environnement, la création directe de dossiers par `os` était restreinte. La solution qui a fonctionné a été de laisser Spark créer le sous-dossier lors de l’écriture :

```python
batch_df.write.mode("overwrite").json(
    "/Volumes/workspace/study_s04_ingestion/landing/batch"
)
```

Si l’écriture Spark échoue aussi, vérifier les droits :

```sql
%sql
SHOW GRANTS ON VOLUME workspace.study_s04_ingestion.landing;
```

Pour écrire dans un volume, il faut notamment pouvoir utiliser le catalogue et le schéma, lire le volume et écrire dans le volume : `USE CATALOG`, `USE SCHEMA`, `READ VOLUME`, `WRITE VOLUME`.

---

## 4. Pattern 1 — ingestion batch avec `COPY INTO`

### 4.1 Ce que résout ce pattern

`COPY INTO` charge des fichiers dans une table Delta. Databricks conserve un historique des fichiers déjà chargés. Rejouer la même commande sur les mêmes fichiers est donc normalement idempotent.

```text
fichiers JSON
     │
     │ lecture + conversion de schéma
     ▼
 COPY INTO
     │
     ├── fichier déjà connu  → ignoré
     └── nouveau fichier     → chargé
     ▼
table Delta
```

### 4.2 Créer la table cible

```sql
%sql
CREATE TABLE IF NOT EXISTS workspace.study_s04_ingestion.copy_into_events (
    event_id BIGINT,
    event_time TIMESTAMP,
    category STRING,
    amount DOUBLE,
    updated_at TIMESTAMP
)
USING DELTA;
```

Explication :

- `CREATE TABLE` crée une table structurée.
- `IF NOT EXISTS` autorise la relance de la cellule si la table existe déjà.
- Le nom complet suit `catalog.schema.table`.
- Les colonnes imposent le contrat attendu.
- `USING DELTA` choisit Delta Lake : stockage transactionnel, historique de versions et support de `MERGE`.

Attention : `IF NOT EXISTS` ne corrige pas une table existante avec un mauvais schéma. Il ne fait alors rien.

### 4.3 Première tentative et erreur de type

Cellule initiale :

```sql
%sql
COPY INTO workspace.study_s04_ingestion.copy_into_events
FROM '/Volumes/workspace/study_s04_ingestion/landing/batch'
FILEFORMAT = JSON
FORMAT_OPTIONS ('inferSchema' = 'true');
```

- `COPY INTO <table>` désigne la cible.
- `FROM '<chemin>'` désigne le dossier source.
- `FILEFORMAT = JSON` choisit le lecteur de fichiers.
- `FORMAT_OPTIONS ('inferSchema' = 'true')` demande d’inférer les types.

Erreur rencontrée :

```text
DELTA_FAILED_TO_MERGE_FIELDS
Failed to merge fields 'event_time' and 'event_time'
SQLSTATE: 22005
```

Cause : un `TIMESTAMP` Spark est sérialisé sous forme textuelle dans du JSON. Le lecteur a pu voir :

```text
source JSON : event_time = STRING
cible Delta : event_time = TIMESTAMP
```

Même nom de colonne, types incompatibles : le chargement refuse de deviner une conversion potentiellement dangereuse.

Diagnostic utile :

```python
source_df = spark.read.json(
    "/Volumes/workspace/study_s04_ingestion/landing/batch"
)
source_df.printSchema()
```

### 4.4 Version corrigée avec conversions explicites

```sql
%sql
COPY INTO workspace.study_s04_ingestion.copy_into_events
FROM (
    SELECT
        CAST(event_id AS BIGINT) AS event_id,
        CAST(event_time AS TIMESTAMP) AS event_time,
        category,
        CAST(amount AS DOUBLE) AS amount,
        CAST(updated_at AS TIMESTAMP) AS updated_at
    FROM '/Volumes/workspace/study_s04_ingestion/landing/batch'
)
FILEFORMAT = JSON;
```

Explication ligne par ligne :

- `FROM (` ouvre une transformation appliquée avant l’écriture dans la cible.
- `SELECT` choisit les colonnes sources.
- `CAST(event_id AS BIGINT)` impose le type de l’identifiant.
- `AS event_id` conserve le nom attendu dans la cible.
- `CAST(event_time AS TIMESTAMP)` transforme le texte JSON en horodatage.
- `category` est déjà une chaîne : aucun cast n’est nécessaire.
- `CAST(amount AS DOUBLE)` impose le type numérique.
- `CAST(updated_at AS TIMESTAMP)` convertit l’autre date.
- `FROM '<chemin>'` lit tous les fichiers compatibles sous le chemin.
- `FILEFORMAT = JSON` dit comment décoder les fichiers.

Pourquoi retirer `inferSchema` ?

```text
inferSchema → le moteur tente de deviner
CAST        → le pipeline impose son contrat
```

Quand le schéma métier est connu, les conversions explicites sont plus déterministes.

### 4.5 Contrôles après le premier chargement

```sql
%sql
SELECT *
FROM workspace.study_s04_ingestion.copy_into_events
ORDER BY event_id;
```

- `SELECT *` affiche toutes les colonnes.
- `ORDER BY event_id` rend le résultat lisible ; cela ne change pas le stockage physique.
- Résultat attendu : événements `1`, `2`, `3`.

```sql
%sql
SELECT COUNT(*) AS nb_lignes
FROM workspace.study_s04_ingestion.copy_into_events;
```

- `COUNT(*)` compte les lignes.
- `AS nb_lignes` donne un nom clair à la mesure.
- Résultat attendu : `3`.

Relancer ensuite **exactement le même `COPY INTO`**, sans modifier les fichiers, puis recompter. Résultat attendu : toujours `3`.

### 4.6 Deuxième lot

```python
from datetime import datetime

batch_data_2 = [
    (4, datetime(2026, 8, 30, 18, 15), "C", 30.0, datetime(2026, 8, 30, 18, 16)),
    (5, datetime(2026, 8, 30, 18, 20), "B", 12.5, datetime(2026, 8, 30, 18, 21)),
]

batch_df_2 = spark.createDataFrame(batch_data_2, columns)
batch_df_2.display()
```

Les cinq noms contenus dans `columns` sont réutilisés. Deux lignes nouvelles sont créées.

```python
batch_df_2.write \
    .mode("overwrite") \
    .json("/Volumes/workspace/study_s04_ingestion/landing/batch_002")
```

Le deuxième lot est placé dans un nouveau sous-dossier pour ne pas écraser le premier.

```sql
%sql
COPY INTO workspace.study_s04_ingestion.copy_into_events
FROM (
    SELECT
        CAST(event_id AS BIGINT) AS event_id,
        CAST(event_time AS TIMESTAMP) AS event_time,
        category,
        CAST(amount AS DOUBLE) AS amount,
        CAST(updated_at AS TIMESTAMP) AS updated_at
    FROM '/Volumes/workspace/study_s04_ingestion/landing/batch_002'
)
FILEFORMAT = JSON;
```

Contrôle :

```sql
%sql
SELECT COUNT(*) AS nb_lignes
FROM workspace.study_s04_ingestion.copy_into_events;
```

Résultat attendu : `5`, soit `3 + 2`.

### 4.7 Ce que signifie vraiment « idempotent » ici

L’idempotence de `COPY INTO` est **au niveau du fichier**, pas de la clé métier.

```text
même fichier relu                    → normalement ignoré
nouveau fichier, nouveaux event_id   → chargé
nouveau fichier, event_id déjà connu → chargé aussi si aucun autre contrôle
```

`COPY INTO` ne remplace pas une contrainte d’unicité et ne fait pas de `MERGE` automatique sur `event_id`. Deux fichiers distincts contenant le même événement peuvent donc produire un doublon métier.

Bonnes pratiques :

- rendre les fichiers d’atterrissage immuables ;
- utiliser des noms/chemins stables ;
- ne pas réécrire un ancien lot sous un nouveau nom ;
- imposer le schéma au lieu de dépendre uniquement de l’inférence ;
- ajouter des contrôles de qualité et de doublons sur les clés métier ;
- préférer Auto Loader lorsque le nombre de fichiers et la fréquence deviennent importants.

---

## 5. Pattern 2 — ingestion incrémentale de fichiers avec Auto Loader

### 5.1 Ce que résout ce pattern

Auto Loader fournit la source Structured Streaming `cloudFiles`. Elle détecte progressivement les nouveaux fichiers. Le checkpoint conserve l’état nécessaire pour reprendre après un arrêt ou un incident.

```text
répertoire source /stream
        │
        ▼
spark.readStream.format("cloudFiles")
        │
        ├──────────────> checkpoint
        │                 - fichiers découverts
        │                 - progression du flux
        │                 - informations de reprise
        ▼
writeStream.toTable(...)
        │
        ▼
table Delta autoloader_events
```

### 5.2 Premier lot du flux

```python
stream_data_1 = [
    (101, datetime(2026, 8, 30, 19, 0), "A", 100.0, datetime(2026, 8, 30, 19, 1)),
    (102, datetime(2026, 8, 30, 19, 5), "B", 200.0, datetime(2026, 8, 30, 19, 6)),
]

stream_df_1 = spark.createDataFrame(stream_data_1, columns)
stream_df_1.display()
```

Deux événements sont créés avec le même contrat de colonnes que précédemment.

```python
stream_df_1.write \
    .mode("overwrite") \
    .json("/Volumes/workspace/study_s04_ingestion/landing/stream")
```

Spark crée les fichiers du premier lot sous le dossier surveillé par Auto Loader.

### 5.3 Définir la lecture Auto Loader

```python
stream_source = (
    spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .schema(stream_df_1.schema)
        .load("/Volumes/workspace/study_s04_ingestion/landing/stream")
)
```

Explication ligne par ligne :

- `spark.readStream` construit une lecture incrémentale, contrairement à `spark.read` qui lit un snapshot batch.
- `.format("cloudFiles")` active Auto Loader.
- `.option("cloudFiles.format", "json")` indique le format réel des fichiers découverts.
- `.schema(stream_df_1.schema)` fournit un schéma explicite à la lecture. Le lab réutilise le schéma du DataFrame synthétique.
- `.load(...)` indique le dossier source à surveiller.
- La variable `stream_source` décrit le flux ; aucun traitement n’a encore démarré.

### 5.4 Écrire le flux et définir son checkpoint

```python
query = (
    stream_source.writeStream
        .option(
            "checkpointLocation",
            "/Volumes/workspace/study_s04_ingestion/landing/_checkpoints/events"
        )
        .trigger(availableNow=True)
        .toTable("workspace.study_s04_ingestion.autoloader_events")
)
```

Explication :

- `writeStream` ouvre l’écriture streaming.
- `checkpointLocation` donne une adresse stable à la mémoire du flux.
- `.trigger(availableNow=True)` traite tout ce qui est disponible, éventuellement en plusieurs micro-batchs, puis arrête proprement le flux.
- `.toTable(...)` écrit le résultat dans une table Unity Catalog, au format Delta.
- `query` reçoit l’objet qui représente l’exécution en cours.

```python
query.awaitTermination()
```

Cette ligne bloque la cellule jusqu’à la fin propre du run `AvailableNow`. Sans elle, une cellule suivante peut effectuer les contrôles avant la fin de l’écriture.

Contrôle :

```sql
%sql
SELECT *
FROM workspace.study_s04_ingestion.autoloader_events
ORDER BY event_id;
```

Résultat attendu au premier passage : `2` lignes.

### 5.5 Deuxième arrivée de fichiers

```python
stream_data_2 = [
    (103, datetime(2026, 8, 30, 19, 10), "C", 300.0, datetime(2026, 8, 30, 19, 11)),
    (104, datetime(2026, 8, 30, 19, 15), "A", 150.0, datetime(2026, 8, 30, 19, 16)),
]

stream_df_2 = spark.createDataFrame(stream_data_2, columns)
stream_df_2.display()
```

```python
stream_df_2.write \
    .mode("overwrite") \
    .json("/Volumes/workspace/study_s04_ingestion/landing/stream/stream_002")
```

Le nouveau lot est écrit sous un nouveau chemin situé dans le dossier source.

Relancer ensuite la **même** définition Auto Loader avec la **même** cible et surtout le **même** checkpoint :

```python
stream_source = (
    spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .schema(stream_df_1.schema)
        .load("/Volumes/workspace/study_s04_ingestion/landing/stream")
)

query = (
    stream_source.writeStream
        .option(
            "checkpointLocation",
            "/Volumes/workspace/study_s04_ingestion/landing/_checkpoints/events"
        )
        .trigger(availableNow=True)
        .toTable("workspace.study_s04_ingestion.autoloader_events")
)

query.awaitTermination()
```

Contrôles :

```sql
%sql
SELECT COUNT(*) AS nb_lignes
FROM workspace.study_s04_ingestion.autoloader_events;
```

Résultat attendu : `4`, pas `6`.

```sql
%sql
SELECT *
FROM workspace.study_s04_ingestion.autoloader_events
ORDER BY event_id;
```

Résultat attendu : `101`, `102`, `103`, `104`.

### 5.6 Le rôle exact du checkpoint

Le checkpoint n’est pas un simple journal facultatif. Il contient l’état opérationnel du flux : progression, métadonnées des fichiers traités et informations nécessaires à la reprise.

```text
run 1
fichiers 001 → traités → état enregistré dans le checkpoint

run 2, même checkpoint
fichiers 001 → déjà connus → ignorés
fichiers 002 → nouveaux    → traités
```

Si le checkpoint est supprimé, le flux perd sa mémoire. Un nouveau démarrage peut alors reconsidérer les fichiers présents comme une nouvelle source à parcourir.

Règles importantes :

- un pipeline Auto Loader doit conserver un checkpoint stable ;
- ne pas partager le même checkpoint entre deux flux distincts ;
- ne pas placer le checkpoint à l’intérieur du dossier de données surveillé ;
- ne pas appliquer une politique automatique de suppression au checkpoint ;
- ne pas supprimer un checkpoint pour « réparer » un flux sans avoir évalué le risque de retraitement ;
- certaines modifications de source, de cible ou de logique ne sont pas compatibles avec la reprise depuis un ancien checkpoint.

### 5.7 Exactly-once ne signifie pas déduplication métier

Avec son checkpoint et une cible Delta, Auto Loader fournit une garantie de traitement exactement une fois des fichiers suivis. Mais il ne déduplique pas automatiquement le contenu selon `event_id`.

```text
fichier A contient event_id = 101
fichier B contient aussi event_id = 101

Auto Loader peut traiter A une fois et B une fois
→ deux lignes métier identiques sont possibles
```

Pour une unicité métier, ajouter une logique de déduplication ou un `MERGE` sur une clé fiable.

### 5.8 Schéma explicite et évolution de schéma

Dans le lab :

```python
.schema(stream_df_1.schema)
```

Le schéma est fixe. C’est simple et sûr, mais une nouvelle colonne n’est pas automatiquement acceptée.

Pour utiliser l’inférence et suivre l’évolution du schéma, Auto Loader peut conserver un historique dans `cloudFiles.schemaLocation` :

```python
schema_path = (
    "/Volumes/workspace/study_s04_ingestion/landing/"
    "_schemas/autoloader_events"
)

stream_source = (
    spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaLocation", schema_path)
        .load("/Volumes/workspace/study_s04_ingestion/landing/stream")
)
```

Ce choix demande une stratégie explicite pour les nouvelles colonnes, les types inattendus et les données « rescued ». En production, le contrôle du schéma est une décision de gouvernance, pas seulement une option technique.

---

## 6. Pattern 3 — ingestion incrémentale par curseur et `MERGE`

### 6.1 Le concept

Ici, la nouveauté n’est plus détectée par un fichier. La source possède une colonne qui évolue quand une ligne est créée ou modifiée :

```text
updated_at
```

Le pipeline mémorise sa dernière valeur traitée :

```text
last_updated_at
```

Au run suivant :

```sql
WHERE updated_at > last_updated_at
```

Cette valeur est souvent appelée :

- curseur d’ingestion ;
- high-water mark ;
- watermark d’ingestion dans certains projets.

Attention : ce n’est **pas** le watermark de Structured Streaming. La distinction complète se trouve en section 6.9.

### 6.2 Créer la source synthétique

```sql
%sql
CREATE OR REPLACE TABLE workspace.study_s04_ingestion.source_orders (
    order_id BIGINT,
    customer STRING,
    amount DOUBLE,
    updated_at TIMESTAMP
)
USING DELTA;
```

- `OR REPLACE` recrée la table et son contenu : cette syntaxe est pratique pour réinitialiser le lab, mais destructive pour les données précédentes.
- `order_id` sera la clé métier utilisée dans le `MERGE`.
- `updated_at` servira de curseur.
- `USING DELTA` permet les opérations transactionnelles.

```sql
%sql
INSERT INTO workspace.study_s04_ingestion.source_orders
VALUES
    (1, 'Alice', 100.0, TIMESTAMP '2026-08-30 20:00:00'),
    (2, 'Bob',   200.0, TIMESTAMP '2026-08-30 20:05:00'),
    (3, 'Chloe', 150.0, TIMESTAMP '2026-08-30 20:10:00');
```

- `INSERT INTO` ajoute des lignes.
- L’ordre des valeurs suit l’ordre des colonnes de la table.
- `TIMESTAMP '...'` crée des littéraux SQL correctement typés.

```sql
%sql
SELECT *
FROM workspace.study_s04_ingestion.source_orders
ORDER BY order_id;
```

Résultat attendu : trois commandes.

### 6.3 Créer la cible

```sql
%sql
CREATE OR REPLACE TABLE workspace.study_s04_ingestion.incremental_orders (
    order_id BIGINT,
    customer STRING,
    amount DOUBLE,
    updated_at TIMESTAMP
)
USING DELTA;
```

La cible a le même contrat que la source. Elle est vide au début.

### 6.4 Créer la table de contrôle du curseur

```sql
%sql
CREATE OR REPLACE TABLE workspace.study_s04_ingestion.ingestion_watermark (
    pipeline_name STRING,
    last_updated_at TIMESTAMP
)
USING DELTA;
```

- `pipeline_name` permet à la table de contrôle de contenir un curseur par pipeline.
- `last_updated_at` mémorise la dernière borne validée.

```sql
%sql
INSERT INTO workspace.study_s04_ingestion.ingestion_watermark
VALUES (
    'orders_pipeline',
    TIMESTAMP '1970-01-01 00:00:00'
);
```

La date de 1970 signifie ici « rien n’a encore été traité ». Toutes les dates du lab sont supérieures à cette valeur.

```sql
%sql
SELECT *
FROM workspace.study_s04_ingestion.ingestion_watermark;
```

Résultat attendu :

```text
orders_pipeline | 1970-01-01 00:00:00
```

### 6.5 Prévisualiser le delta à traiter

```sql
%sql
SELECT s.*
FROM workspace.study_s04_ingestion.source_orders AS s
WHERE s.updated_at > (
    SELECT last_updated_at
    FROM workspace.study_s04_ingestion.ingestion_watermark
    WHERE pipeline_name = 'orders_pipeline'
)
ORDER BY s.order_id;
```

Lecture de l’intérieur vers l’extérieur :

1. La sous-requête lit `last_updated_at` pour `orders_pipeline`.
2. Au premier run, elle retourne `1970-01-01`.
3. `s.updated_at > ...` ne conserve que les lignes plus récentes.
4. `SELECT s.*` retourne toutes les colonnes des lignes retenues.
5. Le premier run doit trouver les trois commandes.

La sous-requête doit retourner une seule valeur. Il faut donc garantir une seule ligne de contrôle par `pipeline_name`.

### 6.6 Appliquer les changements avec `MERGE`

```sql
%sql
MERGE INTO workspace.study_s04_ingestion.incremental_orders AS target
USING (
    SELECT s.*
    FROM workspace.study_s04_ingestion.source_orders AS s
    WHERE s.updated_at > (
        SELECT last_updated_at
        FROM workspace.study_s04_ingestion.ingestion_watermark
        WHERE pipeline_name = 'orders_pipeline'
    )
) AS source
ON target.order_id = source.order_id
WHEN MATCHED THEN
    UPDATE SET
        target.customer = source.customer,
        target.amount = source.amount,
        target.updated_at = source.updated_at
WHEN NOT MATCHED THEN
    INSERT (
        order_id,
        customer,
        amount,
        updated_at
    )
    VALUES (
        source.order_id,
        source.customer,
        source.amount,
        source.updated_at
    );
```

Explication bloc par bloc :

- `MERGE INTO ... AS target` désigne la table à mettre à jour.
- `USING (...) AS source` construit uniquement le delta depuis le dernier curseur.
- `ON target.order_id = source.order_id` définit la correspondance métier.
- `WHEN MATCHED` signifie que la commande existe déjà dans la cible.
- `UPDATE SET` remplace alors ses attributs par la version source.
- `WHEN NOT MATCHED` signifie que la clé n’existe pas dans la cible.
- `INSERT ... VALUES ...` crée alors la nouvelle ligne.

Cette combinaison « mise à jour si présente, insertion sinon » est un **upsert**.

```text
source.order_id existe dans target ?
             │
       ┌─────┴─────┐
      oui         non
       │            │
    UPDATE        INSERT
```

Contrôle :

```sql
%sql
SELECT *
FROM workspace.study_s04_ingestion.incremental_orders
ORDER BY order_id;
```

Résultat attendu : Alice, Bob et Chloe.

### 6.7 Mettre à jour le curseur seulement après le succès

Cellule du lab :

```sql
%sql
UPDATE workspace.study_s04_ingestion.ingestion_watermark
SET last_updated_at = (
    SELECT MAX(updated_at)
    FROM workspace.study_s04_ingestion.source_orders
)
WHERE pipeline_name = 'orders_pipeline';
```

- `MAX(updated_at)` trouve la date la plus récente.
- `UPDATE` l’enregistre pour ce pipeline.
- Cette cellule doit être exécutée **après** la réussite du `MERGE`.

Après le premier run, le curseur vaut :

```text
2026-08-30 20:10:00
```

Rejouer la requête de prévisualisation doit alors retourner `0` ligne.

Pourquoi l’ordre est indispensable :

```text
MERGE échoue
   │
   ├── curseur inchangé → prochain run peut retenter     ✅
   └── curseur avancé   → certaines lignes sont sautées  ❌
```

Amélioration simple pour ce lab : après un `MERGE` réussi, calculer le nouveau maximum depuis la **cible effectivement chargée** plutôt que depuis une source qui pourrait évoluer entre les deux cellules :

```sql
%sql
UPDATE workspace.study_s04_ingestion.ingestion_watermark
SET last_updated_at = (
    SELECT MAX(updated_at)
    FROM workspace.study_s04_ingestion.incremental_orders
)
WHERE pipeline_name = 'orders_pipeline';
```

En production, la méthode robuste consiste à capturer une borne supérieure au début du run, traiter uniquement l’intervalle `(ancien_curseur, borne_du_run]`, puis enregistrer **cette même borne** après le succès.

### 6.8 Test complet : Bob est modifié, David est ajouté

Faire évoluer la source :

```sql
%sql
UPDATE workspace.study_s04_ingestion.source_orders
SET
    amount = 225.0,
    updated_at = TIMESTAMP '2026-08-30 20:20:00'
WHERE order_id = 2;

INSERT INTO workspace.study_s04_ingestion.source_orders
VALUES (
    4,
    'David',
    175.0,
    TIMESTAMP '2026-08-30 20:25:00'
);
```

Le curseur vaut encore `20:10`. La requête incrémentale trouve donc exactement :

```text
Bob   | updated_at = 20:20 | ligne modifiée
David | updated_at = 20:25 | ligne nouvelle
```

Relancer le même `MERGE` :

- Bob correspond à `order_id = 2` → `WHEN MATCHED` → `UPDATE` ;
- David ne correspond à aucune clé → `WHEN NOT MATCHED` → `INSERT`.

Mettre ensuite le curseur à jour, puis vérifier :

```sql
%sql
SELECT *
FROM workspace.study_s04_ingestion.incremental_orders
ORDER BY order_id;
```

Résultat attendu :

```text
1 | Alice | 100.0 | 20:00
2 | Bob   | 225.0 | 20:20
3 | Chloe | 150.0 | 20:10
4 | David | 175.0 | 20:25
```

La cible contient quatre lignes, pas cinq : Bob a été mis à jour, pas inséré une deuxième fois.

La requête incrémentale suivante doit retourner `0` ligne.

### 6.9 Curseur d’ingestion versus watermark de Structured Streaming

Ces concepts portent parfois le même nom, mais ne jouent pas le même rôle.

| Concept | Curseur/high-water mark du Pattern 3 | Watermark Structured Streaming |
|---|---|---|
| But | Savoir quelles lignes lire au prochain run | Borner l’état d’une opération streaming et gérer les données tardives |
| Exemple | `WHERE updated_at > last_updated_at` | `.withWatermark("event_time", "10 minutes")` |
| État | Valeur mémorisée dans une table de contrôle ou par un connecteur | État interne d’une requête streaming |
| Risque principal | Rater une modification antidatée ou une égalité mal gérée | Écarter une donnée arrivée au-delà du seuil de retard |
| Utilisation | Ingestion incrémentale depuis table/base/API | Agrégations fenêtrées, jointures de streams, déduplication avec état |

Exemple de vrai watermark streaming :

```python
events_with_watermark = (
    stream_source
        .withWatermark("event_time", "10 minutes")
        .dropDuplicatesWithinWatermark(["event_id"])
)
```

Ici, les dix minutes représentent la tolérance au retard et bornent la durée de conservation de l’état de déduplication. Cela n’a pas la même fonction que la table `ingestion_watermark` du lab.

### 6.10 Risques et bonnes pratiques du curseur

1. **Égalités sur l’horodatage**  
   Avec `>`, une ligne arrivée tardivement avec exactement la dernière valeur peut être manquée. Selon la source, utiliser une borne composée `(updated_at, id)`, un chevauchement temporel suivi d’un `MERGE`, ou une source CDC.

2. **Mises à jour antidatées**  
   Si `updated_at` diminue ou n’est pas modifié lors d’un changement, le pipeline ne verra pas la ligne. Le curseur doit être fiable et monotone du point de vue du pipeline.

3. **Valeurs `NULL`**  
   `NULL > valeur` n’est pas vrai. Les lignes sans curseur sont ignorées : les interdire ou les traiter séparément.

4. **Course entre lecture et mise à jour du curseur**  
   Ne pas recalculer aveuglément `MAX(source.updated_at)` après une lecture non figée. Capturer une borne de run ou dériver la borne de ce qui a réellement été écrit.

5. **Doublons dans le delta source**  
   Plusieurs lignes source portant le même `order_id` peuvent rendre le `MERGE` ambigu. Dédupliquer la source, par exemple en conservant la version la plus récente par clé.

6. **Atomicité opérationnelle**  
   Le `MERGE` doit réussir avant l’avancement du curseur. Prévoir journal de run, statut, nombre de lignes et possibilité de reprise.

7. **Suppressions**  
   Un simple curseur `updated_at` ne découvre pas forcément les suppressions physiques. Utiliser soft delete, CDC, journal de changements ou snapshots comparés.

---

## 7. Comparaison détaillée des trois patterns

| Critère | `COPY INTO` | Auto Loader | Curseur + `MERGE` |
|---|---|---|---|
| Source typique | Fichiers déposés par lots | Fichiers arrivant en continu | Table, base ou API interrogeable |
| API principale du lab | SQL | PySpark Structured Streaming | SQL |
| Unité suivie | Fichier | Fichier + progression du flux | Valeur du curseur + clé métier |
| État conservé | Historique des fichiers chargés | Checkpoint | Table de contrôle du curseur |
| Écriture du lab | Append dans Delta | Append streaming dans Delta | Upsert par `MERGE` |
| Relance | Ignore les fichiers déjà connus | Reprend au checkpoint | Relit seulement `updated_at > curseur` |
| Mise à jour d’une ligne existante | Non, pas automatiquement | Non, pas en append simple | Oui, avec `WHEN MATCHED` |
| Déduplication métier | Non | Non | Possible grâce à une clé fiable, mais la source doit être propre |
| Fréquence naturelle | Ponctuelle ou planifiée | Fréquente, continue ou `AvailableNow` | Planifiée ou orchestrée |
| Scalabilité fichiers | Bonne pour des volumes raisonnables | Conçue pour de très grands volumes de fichiers | Dépend de la source et de l’indexation du curseur |
| Complexité d’exploitation | Faible | Moyenne : checkpoint, schéma, monitoring | Moyenne à forte : curseur, races, suppressions, clés |
| Erreur classique | Croire que les clés métier sont dédupliquées | Supprimer/réutiliser le checkpoint | Avancer le curseur avant le succès |

### Idempotence comparée

```text
COPY INTO
  idempotence technique = suivi des fichiers

Auto Loader
  idempotence technique = état du checkpoint + cible Delta

Curseur + MERGE
  idempotence logique = filtre du curseur + correspondance sur clé métier
```

Dans tous les cas, l’idempotence technique ne garantit pas à elle seule la qualité métier. Il faut définir les clés, contrôler les doublons et surveiller les volumes traités.

---

## 8. SQL ou PySpark en entreprise ?

### Réponse courte

Les deux sont utilisés. Le bon choix dépend surtout du type de traitement, de l’équipe et du mode d’exploitation. Dans ce lab, la combinaison la plus naturelle est :

```text
PySpark → générer les fichiers + définir Auto Loader
SQL     → DDL, COPY INTO, contrôles, MERGE et table de curseur
```

### Choisir SQL quand…

- le traitement s’exprime clairement avec `SELECT`, `JOIN`, `GROUP BY`, `MERGE`, `INSERT` ou `UPDATE` ;
- l’équipe est composée de data analysts, analytics engineers et data engineers maîtrisant SQL ;
- la lisibilité et la revue fonctionnelle sont prioritaires ;
- les transformations sont principalement relationnelles ;
- on utilise Databricks SQL ou des pipelines déclaratifs.

Exemples :

```sql
COPY INTO target FROM ...;

MERGE INTO target
USING source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

### Choisir PySpark quand…

- on utilise directement `readStream`/`writeStream` et Auto Loader ;
- la logique nécessite des fonctions, boucles de configuration ou traitements dynamiques ;
- les transformations sont complexes, imbriquées ou semi-structurées ;
- on intègre des bibliothèques Python, des tests ou du code réutilisable ;
- on traite de nombreux flux/tables à partir de métadonnées.

Exemple :

```python
query = (
    spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .schema(expected_schema)
        .load(source_path)
        .writeStream
        .option("checkpointLocation", checkpoint_path)
        .trigger(availableNow=True)
        .toTable(target_table)
)
```

### Recommandation pratique

1. Commencer en SQL si le problème est naturellement relationnel.
2. Utiliser PySpark lorsque le streaming, la complexité ou la réutilisation du code le justifient.
3. Ne pas convertir une logique simple en Python uniquement « parce que c’est du data engineering ».
4. Ne pas forcer SQL si le code devient une suite illisible de SQL dynamique.
5. Dans un pipeline réel, faire exécuter le code par un job/pipeline orchestré, versionné et testé ; le notebook interactif sert surtout au développement et au diagnostic.

### Choix pour les trois patterns du lab

| Pattern | Choix conseillé pour ce lab | Possibilités en entreprise |
|---|---|---|
| `COPY INTO` | SQL | Très souvent SQL ; orchestration par job/pipeline |
| Auto Loader | PySpark | PySpark classique, ou SQL/Python dans Lakeflow selon l’architecture |
| Curseur + `MERGE` | SQL | SQL pour le `MERGE`, Python possible pour capturer les bornes et orchestrer de nombreuses sources |

Le mélange SQL + PySpark est donc normal. Le critère professionnel n’est pas « un seul langage partout », mais : code compréhensible, testé, observable, rejouable et sûr.

---

## 9. Contrôles de production à ajouter

### Contrôles de volume

```sql
SELECT COUNT(*) FROM table_cible;
```

Comparer le nombre lu, inséré, mis à jour, rejeté et attendu.

### Contrôle de doublons métier

```sql
SELECT event_id, COUNT(*) AS occurrences
FROM workspace.study_s04_ingestion.autoloader_events
GROUP BY event_id
HAVING COUNT(*) > 1;
```

Zéro résultat est attendu si `event_id` doit être unique.

### Contrôle du curseur

```sql
SELECT *
FROM workspace.study_s04_ingestion.ingestion_watermark
WHERE pipeline_name = 'orders_pipeline';
```

Vérifier qu’il n’existe qu’une ligne de contrôle et que la valeur ne régresse pas.

### Contrôle de fraîcheur

```sql
SELECT MAX(updated_at) AS derniere_mise_a_jour
FROM workspace.study_s04_ingestion.incremental_orders;
```

Comparer cette date avec le SLA attendu.

### Contrôles opérationnels

- journaliser l’identifiant du run ;
- conserver les compteurs de lignes ;
- alerter sur un volume nul ou anormal ;
- séparer données entrantes, checkpoints, schémas et données rejetées ;
- ne jamais inclure de secret ou de donnée professionnelle dans un lab personnel ;
- versionner le notebook exporté et les requêtes SQL ;
- tester la reprise après échec, pas seulement le chemin nominal.

---

## 10. Fiche de révision rapide

### Question 1

Je relance `COPY INTO` sans nouveau fichier. Que doit-il se passer ?

**Réponse :** les fichiers déjà enregistrés comme chargés sont ignorés ; le nombre de lignes reste stable.

### Question 2

`COPY INTO` empêche-t-il deux fichiers différents de contenir le même `event_id` ?

**Réponse :** non. Son idempotence porte sur les fichiers, pas sur la clé métier.

### Question 3

Que signifie `.format("cloudFiles")` ?

**Réponse :** cette source active Auto Loader pour découvrir et traiter progressivement de nouveaux fichiers.

### Question 4

Pourquoi le checkpoint est-il indispensable ?

**Réponse :** il conserve l’état et la progression du flux, permet la reprise et évite de retraiter normalement les mêmes fichiers.

### Question 5

Que fait `availableNow=True` ?

**Réponse :** il traite toutes les données actuellement disponibles en mode incrémental, puis arrête proprement la requête.

### Question 6

Que fait un `MERGE` avec `WHEN MATCHED` et `WHEN NOT MATCHED` ?

**Réponse :** il met à jour les clés existantes et insère les nouvelles : c’est un upsert.

### Question 7

Quand faut-il mettre à jour le curseur ?

**Réponse :** uniquement après la réussite de l’écriture ou du `MERGE`, avec la borne exacte réellement traitée.

### Question 8

Le curseur `updated_at` est-il un watermark Structured Streaming ?

**Réponse :** non. Le curseur sélectionne les changements entre deux runs ; le watermark streaming borne l’état et définit la tolérance aux événements tardifs.

### Question 9

SQL ou PySpark ?

**Réponse :** SQL pour les traitements relationnels et `MERGE`; PySpark pour le streaming et la logique programmatique complexe. Un pipeline hybride est courant.

---

## 11. Résumé en une minute

```text
COPY INTO
  source : fichiers batch
  mémoire : historique des fichiers chargés
  piège : ne déduplique pas les clés métier

Auto Loader
  source : nouveaux fichiers continus
  mémoire : checkpoint
  piège : supprimer ou partager le checkpoint

Curseur + MERGE
  source : lignes nouvelles/modifiées
  mémoire : dernière valeur du curseur
  piège : avancer le curseur avant le succès ou utiliser un updated_at non fiable
```

La question à se poser n’est pas d’abord « SQL ou Python ? », mais :

> Quelle est ma source, quelle unité représente la nouveauté, et où mon pipeline conserve-t-il son état ?

---

## 12. Documentation officielle utile

- [Référence `COPY INTO`](https://docs.databricks.com/aws/en/sql/language-manual/delta-copy-into)
- [Présentation d’Auto Loader](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/)
- [Inférence et évolution du schéma avec Auto Loader](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/schema)
- [Déclencheurs Structured Streaming et `AvailableNow`](https://docs.databricks.com/aws/en/structured-streaming/triggers)
- [Upsert dans une table Delta avec `MERGE`](https://docs.databricks.com/aws/en/delta/merge)
- [Watermarks Structured Streaming](https://docs.databricks.com/aws/en/structured-streaming/watermarks)
- [Volumes Unity Catalog et chemins `/Volumes`](https://docs.databricks.com/gcp/volumes/)
- [Privilèges des volumes Unity Catalog](https://docs.databricks.com/gcp/en/volumes/privileges)
- [Ingestion pilotée par une colonne curseur](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/query-based-pipeline)

