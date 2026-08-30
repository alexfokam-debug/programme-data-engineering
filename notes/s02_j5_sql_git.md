Principe appris
- Pourquoi total_price ne peut pas être utilisé dans le WHERE du même SELECT.

Erreur rencontrée
- Unrecognized name: total_price.

Correction
- Calculer total_price dans projected_orders.
- Filtrer ensuite dans la requête externe.
- Utiliser COALESCE(quantity, 0) pour gérer NULL.

Git appris
- git add place un fichier dans la staging area.
- git commit enregistre le contenu indexé.
- git commit --amend permet de corriger le dernier commit.
- toujours enregistrer le fichier dans VS Code avant git add.
