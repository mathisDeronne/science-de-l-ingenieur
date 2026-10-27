# Compte rendu : Player de dev, parties simultanées, nouvelles cartes et nouveau protocole

- **Date** : 26/10/2026
- **Heure de début / fin** : 14h10 / 14h20
- **Lieu** : Salle 207 Bordeaux Ynov Campus
- **Enregistrement** : réunion enregistrée avec l'accord des participants

## Participants

- **Présents** : Client, Guillaume, Mathis, Damien, Léo
- **Absents** : Personne

## Ordre du jour initial

Présentation et implémentation des nouvelles routes liées aux cartes action.

## Sujets abordés

### 1. Délai maximal d'une requête

**Résumé**
- Question posée : combien de temps une équipe a-t-elle pour répondre à une requête de décision avant d'être pénalisée ?
- L'intervenant n'a pas trouvé la réponse sur le moment, la documentation de l'arbitre ayant été rédigée par d'autres.

**Décision / réponse**
- Pas de réponse pour l'instant. La question est reportée à la prochaine réunion. L'intervenant précise qu'il n'y a « pas le feu ».

### 2. Durée totale d'une partie

**Résumé**
- La durée d'une partie est variable et dépend de la vitesse de réponse des joueurs.
- Le nombre de tours limite le nombre de requêtes. Un tour peut durer longtemps : tant qu'une équipe renvoie des actions à `Play`, le tour continue.

**Décision / réponse**
- Pas de durée maximale d'une partie : la limitation se fait requête par requête.

### 3. Prochaines cartes et requêtes

**Résumé**
- De nouvelles cartes sont attendues « dès demain » (formulation prudente : « je pense »).
- Demain, les parties deviennent simultanées : des bugs à corriger sont possibles.

**Décision / réponse** : pas de liste précise des cartes à venir.

### 4. Route de fin de partie (`endgame`)

**Résumé**
- Route non évoquée jusqu'ici, rappelée pour éviter un oubli.
- Méthode HTTP GET, appelée à la fin de la partie avec l'identifiant de partie.
- Avec les parties simultanées, les informations sont stockées par partie : à la fin, la stratégie peut supprimer les données de cette partie.

**Décision / réponse**
- Réponse attendue : objet JSON avec la propriété `decision` valant `OK`. C'est le comportement par défaut du template.

**Actions**
- Prévoir cette route (suppression des données de la partie terminée).

### 5. Nouvelles routes déclenchées par des cartes action

**Résumé**
- Ces routes sont des méthodes HTTP POST, appelées automatiquement par l'arbitre quand certaines cartes action sont jouées.
- Elles complètent `CONFIRM_TRASH_CARD_FROM_HAND` (voir réunion précédente).

**Décision / réponse**

| Route | Rôle | Reçu | À renvoyer |
|---|---|---|---|
| `TRASH_CARD_FROM_HAND` | Choisir quelle carte de la main écarter (obligation d'en écarter une). | JSON avec `HAND`, la liste des cartes en main. | JSON avec `DECISION` = nom de la carte à écarter. |
| `CONFIRM_DISCARD_CARD_FROM_HAND` | Confirmer ou non la défausse d'une carte. | JSON avec la carte concernée et la main. | JSON avec `DECISION` booléen (oui/non). |
| `DISCARD_CARD_FROM_HAND` | Choisir quelle carte de la main défausser. | JSON avec la liste des cartes en main (propriété mal transcrite, probablement `HAND`). | JSON avec `DECISION` = nom de la carte à défausser. |
| `CONFIRM_DISCARD_DECK` | Confirmer ou non la défausse de toute la pioche. | Non précisé | JSON avec `DECISION` : `true` pour défausser le deck, `false` sinon. |
| `CHOOSE_CARD_TO_RECEIVE_IN_DISCARD` (nom à confirmer) | Choisir quelle carte recevoir dans la défausse. | JSON avec `possible_cards`, la liste des noms de cartes au choix. | JSON avec `DECISION` = nom de la carte choisie. |
| `CHOOSE_CARD_TO_RECEIVE_IN_DECK` | Même principe, la carte allant dans la pioche. | Liste de cartes possibles. | JSON avec `DECISION` = nom de la carte choisie. |

- Intérêt de `CONFIRM_DISCARD_DECK` : défausser toute la pioche vide la pioche. Elle est remélangée avec le reste de la défausse au prochain tirage. Cela peut servir si on sait que la pioche ne contient plus que de mauvaises cartes.
- Aucune carte action actuelle ne permet d'écarter une carte. Des cartes arriveront, puisque ces routes sont à implémenter. L'intervenant reviendra vers les équipes quand une carte ajoutera ces effets.
- L'intervenant suggère de commencer par les premières routes : les équipes seront tentées d'écarter des Malédictions.


## Prochaine réunion

- **Date** : 26/10/2026
- **Heure de début** : 16:40