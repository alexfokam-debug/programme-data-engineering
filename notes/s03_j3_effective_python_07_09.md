# Effective Python — Items 7 à 9

## Item 7 — Conditional expression

Règle :
Utiliser une expression conditionnelle seulement quand la logique reste immédiatement lisible.

Bon cas d'usage :
Retourner une valeur selon une condition simple.

Exemple :
return "ready" if score >= 80 else "review"

Piège :
Empiler plusieurs conditions ternaires et rendre le code difficile à lire.

## Item 8 — Assignment expression :=

Règle :
Utiliser := lorsqu'une valeur doit être calculée une fois puis utilisée immédiatement.

Bon cas d'usage :
Nettoyer une chaîne puis tester le résultat sans répéter strip().

Exemple :
if normalized := raw_topic.strip():
    return normalized

Piège :
Utiliser := partout simplement pour réduire le nombre de lignes.

## Item 9 — match

Règle :
Utiliser match lorsqu'on traite plusieurs formes ou structures de données.

Bon cas d'usage :
Traiter différents types d'événements représentés par des tuples.

Exemple :
case ("study", subject, duration) if duration > 0:

Piège :
Utiliser match pour une condition très simple qu'un if exprime plus clairement.
