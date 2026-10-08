# Compte rendu : Nom du jeu, cartes disponibles et routes de l'API

- **Date** : 07/10/2026
- **Heure de début / fin** : 9h20 / 9h30
- **Lieu** : Salle 302 Bordeaux Ynov Campus
- **Enregistrement** : réunion enregistrée avec l'accord des participants

## Participants

- **Présents** : Client, Guillaume, Mathis, Damien, (Léo et arrivé en fin de réunion)
- **Absents** : Personne

## Ordre du jour initial

Clarifier les cartes actuellement disponibles dans le jeu ainsi que le fonctionnement de l'API permettant aux bots de communiquer avec l'arbitre.

## Sujets abordés

### 1. Nom du jeu

**Résumé**
- Les équipes ont proposé un nom de jeu et demandé confirmation.
- Le jeu est **Dominion**. Il comporte quelques modifications par rapport au jeu d'origine, mais celui-ci sert de base.

**Décision / réponse** :Confirmé Dominion.

### 2. Cartes disponibles

**Résumé**
- L'équipe on comparé avec la liste de la version 2008 du jeu. Elles ont cité le Woodcutter, que l'intervenant dit avoir dans sa liste, puis l'Atelier et l'Aventurier, qu'il ne connaît pas encore.
- La liste des cartes action actuellement disponible, citée à l'oral : festival, « spaci » (nom mal transcrit), laboratoire, village, woodcutter.
- Trésors : cuivre, argent, or. Cartes point de victoire : Domaine, Duché, Province.
- Les Malédictions : l'intervenant n'a pas la connaissance de cette carte pour l'instant. Il en aura plus tard.

- Festival 5 ;
- Laboratory 5 ;
- Village 3 ;
- Woodcutter ;
- Market 5 ;

| Nom | Valeur d'achat | Réponse attendue |
|---|---|---|
|Village|3|+1 Card, +2 Actions|
|Woodcutter|3|+1 Buy, +2$|
|smithy|4|+3 Cards|
|Market|5|+1 Card, +1 Action, +1 Buy, +1$|
|Festival|5|+2 Actions, +1 Buy, +2$|
|Laboratory|5|+2 Cards, +1 Action|

- Les cartes Trésor disponibles sont :

| Nom | Valeur d'achat | Effet |
|---|---|---|
|Copper|0|1$|
|Silver|3|2$|
|Gold|6|3$|

- Les trois niveaux classiques de cartes Victoire sont également présents :

| Nom | Valeur d'achat | Effet |
|---|---|---|
|Estate|2|1 Valeur|
|Duchy|5|3 Valeur|
|Province|8|6 Valeur|

**Décision / réponse**
- Pour les premiers jours, 5 cartes action sont dans le pool, pour mettre en place les mécaniques et stratégies sur un jeu simple.

### 3. Routes de l'API HTTP

**Résumé**
- La plupart des routes, sauf la route `/name`, reçoivent un identifiant de partie que la stratégie doit mémoriser et renvoyer à l'arbitre. ?????
- Les parties se jouent actuellement à tour de rôle. Elles seront bientôt simultanées : il faut donc stocker les informations par partie, et non de façon globale.
- L'intervenant rappelle qu'il faut livrer au plus tôt ce soir une stratégie meilleure que celle des autres.

**Décision / réponse : routes décrites**

| Route | Rôle | Réponse attendue |
|---|---|---|
| `/name` (GET) | L'arbitre demande le nom de l'équipe. Il apparaît dans les logs des parties. | Le nom de l'équipe, sous forme de chaîne de caractères. Il faut remplacer le nom par défaut. |
| `StartGame` | Marque le début d'une partie. Reçoit notamment l'identifiant de partie, utilisable pour initialiser un espace de stockage dédié. | Objet JSON avec la propriété `decision` valant `OK`. |
| `StartTurn` | Marque le début d'un tour. | Objet JSON avec la propriété `decision` valant `OK`. |
| `Play` (POST) | Route principale. L'arbitre envoie l'état du jeu. | Objet JSON avec une propriété `decision`, voir ci-dessous. |

**Valeurs de `decision` pour `Play`** (texte en majuscules)
- `END_TURN` : plus aucune action à faire ce tour.
- `BUY <nom de la carte>` : acheter une carte. Le nom est celui de la carte telle qu'envoyée par le serveur.
- `ACTION <nom de la carte>` : jouer une carte action de sa main.

**Règles d'achat**
- Il n'a pas besoin de précisier quelles cartes servent à payer : l'arbitre dépense automatiquement la monnaie de la main.
- L'arbitre prend en compte la monnaie totale disponible pendant la phase d'achat, y compris les bonus des cartes action. Les dépenses peuvent se répartir sur plusieurs achats.
- Acheter une carte trop chère ou qui n'a pas de stock est une action invalide : le joueur est éjecté de la partie.

**État du jeu reçu par `Play`** (JSON)
- `finish` : booléen sans utilité (indique que la partie n'est pas finie).
- `players` : liste d'informations sur les joueurs. Seule la propriété `name` a été citée avant la fin de l'enregistrement.
- `stock` : quantité de cartes restantes dans la réserve.
- Les points des autres joueurs ne sont pas visibles.


## Sujets prévus mais non traités

- Malédictions : informations à venir.
- Liste complète des cartes de la version 2008 : non fournie pour l'instant.

## Prochaine réunion

- **Date** : 8/10/2026
- **Heure de début** : 14:20