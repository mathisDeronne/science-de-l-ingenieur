# Compte rendu : Parties simultanées, nouvelles cartes et nouvelles routes

- **Date** : 27/10/2026
- **Heure de début / fin** : 9h10 / 9h20
- **Lieu** : Salle 207 Bordeaux Ynov Campus
- **Enregistrement** : réunion enregistrée avec l'accord des participants

## Participants

- **Présents** : Client, Guillaume, Mathis, Damien, Léo
- **Absents** : Personne

## Ordre du jour initial

quels sont les nouvelles cartes/informations/commandes.

## Sujets abordés

### 1. Parties simultanées et classement

**Résumé**
- Les parties simultanées sont lancées et fonctionnent.
- Environ 250 parties ont déjà été jouées depuis le matin (lancement à 8h50).
- Le serveur de dev est passé deuxiéme du classement, qui se met à jour en temps réel. Un autre joueur et premiéer avec 13 points Elo de plus.


### 2. Nouvelles cartes

Les coûts sont exprimés « en cuivres » à l'oral. Les noms français sont ceux entendus ; plusieurs sont mal transcrits.

| Carte (VF / EN) | Coût | Effet |
|---|---|---|
| Bandit « Bambi » | 5 | Chaque fois qu'elle est jouée : reçoit 1 or. Chaque adversaire dévoile les 2 premières cartes de sa pioche. S'il y a des trésors, le plus cher est écarté (jeté au rebut, pas à la défausse). Les autres cartes dévoilées sont défaussées. Le joueur ne récupère pas la carte écartée. |
| Bureaucrate / Bureaucrat | 4 | Reçoit 1 argent, placé sur le dessus du deck (prochaine carte piochée). Chaque adversaire qui a une carte victoire en main doit la remettre sur le dessus de son deck : il la repiochera au prochain tour. |
| Chancelier / Chancellor | 3 | +2 de pouvoir d'achat pour le tour. On peut choisir de défausser tout son deck : l'arbitre appelle alors `CONFIRM_DISCARD_DECK`. |
| Jardins / Gardens | 4 | Vaut 1 point de victoire par dizaine de cartes possédées, arrondi à l'inférieur. Exemple : 33 cartes = 3 points. Permet une stratégie différente : acheter beaucoup de cartes pas chères. |
| Milice / Militia | 4 | Donne un bon d'achat (montant non précisé). Chaque adversaire doit défausser jusqu'à n'avoir que 3 cartes en main : l'arbitre appelle `DISCARD_CARD_FROM_HAND` en boucle, une carte à la fois, jusqu'à 3 cartes. |

**Décision / réponse**
- La route `DISCARD_CARD_FROM_HAND` est facultative : par défaut, l'arbitre défausse la première carte de la main, sans erreur pour une équipe qui ne l'implémente pas.
- Précision sur la Recrue (réunion précédente) : sa carte supplémentaire est reçue **au début de chaque tour**, non à la fin du tour précédent. Un adversaire qui a une Recrue en jeu peut donc récupérer une carte après une Milice, ce qui atténue son effet.
- Pour l'instant, beaucoup d'attaques et peu de défenses : il n'y a pas de carte pour contrer (une carte de défense a été évoquée sous un nom inintelligible, l'intervenant la mentionne comme absente).
- Les Sorcières restent en jeu.

### 3. Nouvelles routes (pas encore nécessaires, mais « ça risque d'arriver »)

Méthodes HTTP POST, appelées automatiquement par l'arbitre quand certaines cartes action sont jouées.

| Route | Rôle | Reçu | À renvoyer |
|---|---|---|---|
| `SKIP_CARD_RECEPTION_IN_HAND` | Choisir d'ignorer ou non l'ajout automatique d'une carte. | JSON avec `CARD_NAME` (carte qu'on va potentiellement recevoir) et `HAND` (cartes en main). | JSON avec `DECISION` booléen : `true` pour ignorer, `false` pour recevoir la carte. |
| `TRASH_MONEY_CARD_FOR_BETTER_MONEY_CARD` | Choisir un trésor de la main à écarter pour en recevoir un autre coûtant jusqu'à 3 de plus (par exemple cuivre contre argent), dans la limite des stocks de la réserve. | JSON avec la liste des noms des trésors en main (propriété transcrite « MoneyInHand », forme exacte à confirmer). Seuls les trésors sont envoyés, pas toute la main. | JSON avec `DECISION` = nom du trésor à écarter. |

### 4. Informations sur les joueurs dans l'état du jeu

**Résumé**
- Dans les informations d'un joueur : la propriété `Hand` est nulle pour les autres joueurs. Pour soi, elle donne le contenu de la main (formulation peu claire : « quantité de cartes », « par type de cartes »).
- Une propriété `Score` donne le nombre de points de victoire actuellement possédés, y compris tous les points de victoire du joueur (formulation hésitante).

**Décision / réponse** : précisions données à la fin de la réunion, sans débat.

## Sujets prévus mais non traités

- Montant du bon d'achat de la Milice.
- Carte de défense (nom et date d'arrivée).
- La visibilité de `Score` pour les autres joueurs (voir « Points à vérifier »).

## Tableau récapitulatif des actions

| Action | Responsable | Échéance |
|---|---|---|
| Prévoir le traitement des routes `SKIP_CARD_RECEPTION_IN_HAND` et `TRASH_MONEY_CARD_FOR_BETTER_MONEY_CARD` (implicite) | Équipes (non nominatif) | Non précisé |

## Prochaine réunion

- **Date** : 27/10/2026
- **Heure de début** : 14:40

## Points à vérifier (transcription automatique)

- **Noms de cartes mal transcrits** : « Bambi » (l'effet décrit correspond à la carte Bandit du jeu d'origine, mais ce n'est pas dit à l'oral : à confirmer), « Gardens » (« caresse à lapin »), « Milice » (« Miliciard »), cartes de défense (« douves », « touffes »).
- **Jardins** : l'arrondi « à l'inférieur » est audible dans une transcription et déformé dans l'autre. La règle exacte est à confirmer.
- **`Score`** : la réunion du début indique qu'on ne voit pas les points des autres joueurs. Ici, la propriété `Score` est citée sans préciser si elle concerne les adversaires. À clarifier : c'est une information stratégique.
- Noms exacts des routes et des propriétés (casse, underscores) reconstitués d'après l'audio. À vérifier dans le template.
- Les intervenants ne sont pas distingués dans la transcription.