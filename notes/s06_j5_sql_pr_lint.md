## PR solo — SQL Cookbook 3.2

### Contexte

Implémentation de la recette 3.2 « Combining Related Rows » du SQL Cookbook en GoogleSQL / BigQuery avec uniquement des données synthétiques.

### Modifications

- création de jeux de données `customers` et `orders` avec `WITH`, `UNNEST` et `STRUCT` ;
- jointure explicite avec `INNER JOIN` sur `customer_id` ;
- tri déterministe du résultat ;
- ajout d'un client sans commande ;
- ajout de plusieurs commandes pour un même client ;
- ajout d'une commande sans client correspondant.

### Tests effectués

- le résultat de la jointure contient 5 lignes ;
- Alice possède 2 commandes ;
- Eve n'apparaît pas car elle ne possède aucune commande ;
- la commande associée à `customer_id = 999` n'apparaît pas car aucun client correspondant n'existe.

### Auto-revue

- [x] données entièrement synthétiques ;
- [x] clé de jointure explicite ;
- [x] cardinalité 1→N vérifiée ;
- [x] cas sans correspondance vérifiés ;
- [x] aucun secret ni élément professionnel ;
- [x] requête reproductible dans BigQuery.