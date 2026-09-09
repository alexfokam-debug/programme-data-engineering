### Scénario 1 — Fichiers batch quotidiens

Choix : `COPY INTO`

Pourquoi :
- source sous forme de fichiers ;
- ingestion batch ;
- pas de besoin temps réel ;
- les fichiers déjà chargés ne doivent pas être retraités ;
- adapté à une alimentation simple de la couche bronze.

### Scénario 2 — Fichiers incrémentaux

Choix : Auto Loader

Pourquoi :
- nouveaux fichiers reçus plusieurs fois dans la journée ;
- arrivée imprévisible ;
- détection automatique des nouveaux fichiers ;
- évite de retraiter les anciens fichiers ;
- reprise possible grâce au checkpoint.

### Scénario 3 — Ingestion gérée depuis PostgreSQL

Choix : Lakeflow Connect

Pourquoi :
- source externe structurée ;
- ingestion récurrente ;
- moins de code personnalisé ;
- maintenance simplifiée ;
- adapté à un pipeline d’ingestion géré dans Databricks.

### Scénario 4 — Lecture contrôlée depuis PySpark

Choix : JDBC

Pourquoi :
- lecture depuis un notebook PySpark ;
- source relationnelle MySQL ;
- contrôle de la requête depuis le code ;
- adapté aux connexions programmatiques vers une base relationnelle.

ODBC serait plus naturel pour un outil BI ou un client SQL.

### Scénario 5 — Connexion depuis un outil BI

Choix : ODBC

Pourquoi :
- utilisation de Power BI Desktop ;
- connexion depuis un client BI ;
- usage d’un pilote standard ;
- pas de logique Spark ou applicative à coder.

ODBC est adapté aux outils BI et aux clients SQL.