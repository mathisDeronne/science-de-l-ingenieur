# Compte rendu : Player de dev, parties simultanées, nouvelles cartes et nouveau protocole

- **Date** : 26/10/2026
- **Heure de début / fin** : 9h40 / 9h50
- **Lieu** : Salle 207 Bordeaux Ynov Campus
- **Enregistrement** : réunion enregistrée avec l'accord des participants

## Participants

- **Présents** : Client, Guillaume, Mathis, Damien, Léo
- **Absents** : Personne

## Ordre du jour initial

Non précisé. La réunion a débuté par l'annonce de deux nouvelles informations « importantes pour aujourd'hui ».

## Sujets abordés

### 1. Player de dev (stratégie officieuse)

**Résumé**
- À partir d'aujourd'hui, chaque groupe peut avoir un « player de dev » : une stratégie officieuse, traitée par l'arbitre comme un joueur classique.
- L'arbitre lui fait jouer des parties, ce qui permet de tester de nouvelles stratégies.
- Il n'est pas compté dans le classement officiel des équipes.
- Un player de dev par groupe.

**Décision / réponse**
- Les équipes qui veulent un player de dev doivent envoyer son URL à l'intervenant.
- Aucun nom spécifique n'est exigé.
- Cas évoqué : une équipe mal intentionnée pourrait reprendre le nom d'une équipe adverse pour nuire à sa stratégie.

### 2. Parties simultanées

**Résumé**
- À partir de demain (27/10/2026), plusieurs parties se joueront en même temps.
- Aujourd'hui, une seule partie a lieu à la fois : cela n'a pas encore d'impact.
- Les stratégies doivent être capables de gérer plusieurs parties sans les confondre, grâce à l'identifiant de partie (game ID).

**Décision / réponse** : préparer la stratégie dès maintenant.

### 3. Nouvelles cartes

**Résumé**
- Plusieurs nouvelles cartes sont apparues aujourd'hui. Les coûts sont exprimés « en cuivres » à l'oral.

| Nom (VF / EN) | Coût | Effet |
|---|---|---|
| Chambre du conseil / Council Room | 5 | Pioche 4 cartes, +1 achat. Chaque adversaire pioche aussi 1 carte. Exemple donné : 4 ors piochés = 12 de pouvoir d'achat et 2 achats. |
| Malédiction / Curse | 0 | Compte pour moins d'un point de victoire (un point en moins). Stock au départ : 10 pour 2 joueurs, 20 pour 3, 30 pour 4 (soit 10 par adversaire). |
| Rivage lointain / Distant Shore | 6 | Pioche 2 cartes, +1 action. Chaque fois qu'elle est jouée, reçoit un Domaine. Compte elle-même pour 2 points de victoire. |
| Village agricole / Farming Village | 4 | Pioche 1 carte, +2 actions. La pioche se fait jusqu'à tomber sur une carte trésor ou action ; les autres cartes révélées sont défaussées. |
| Recrue / Hireling | 6 | À chaque tour suivant, au début de la phase action, reçoit 1 carte supplémentaire. Avec 1 Recrue jouée, le tour suivant démarre à 6 cartes ; avec 5, à 10 cartes. L'intervenant « encourage très fortement » à l'utiliser. |
| Sorcière / Witch | 5 | Pioche 2 cartes. Chaque fois qu'elle est jouée, les adversaires reçoivent une Malédiction depuis la réserve, dans la limite du stock, distribuées dans l'ordre des joueurs. Une Malédiction fait perdre un point de victoire et ajoute une carte inutilisable. |

**Décision / réponse**
- Pas de carte pour contrer la Sorcière à ce jour : une question a été posée sur une carte de défense, l'intervenant ne la connaît pas.
- Stratégie évoquée pour les Malédictions : vider trois piles (dont celle des Malédictions, gratuites) pour terminer la partie plus vite. Cela fait perdre des points de victoire, donc « il faut être sûr de ce qu'on fait ».

### 4. Règles et magasin

**Résumé**
- Aucun changement de règle : tout ce qui était actif le reste.
- Il y a désormais plus de 10 types de cartes action, assez pour démarrer chaque partie avec 10 piles de cartes action dans le magasin.

**Décision / réponse**
- Le magasin n'est plus toujours le même : à chaque partie, 10 types de cartes action sont tirés parmi toutes les cartes possibles (« roulement »).

### 5. Nouveau protocole : confirmation d'écartement d'une carte

**Résumé**
- Des protocoles de communication supplémentaires avec l'arbitre vont devenir utiles à partir de demain. L'intervenant en présente un.
- Dans certaines conditions, l'arbitre appelle une méthode HTTP POST nommée `CONFIRM_TRASH_CARD_FROM_HAND`. Elle se déclenche automatiquement quand certaines cartes action sont jouées, par soi-même ou par les adversaires. Elle permet de choisir si une carte de sa main est écartée.

**Décision / réponse**
- **Reçu** : un objet JSON dans le corps de la requête, avec deux propriétés : `CARD_NAME` (nom de la carte potentiellement écartée) et `HAND` (liste des noms des cartes de la main).
- **À renvoyer** : un objet JSON avec une propriété `DECISION` valant un booléen : `true` pour confirmer l'écartement de la carte, `false` sinon.

**Actions**
- Prévoir le traitement de cette méthode dans la stratégie. Cette action est implicite : l'intervenant dit que ces protocoles servent « à partir de demain ».

## Sujets prévus mais non traités

- Les autres protocoles de communication supplémentaires (seul `CONFIRM_TRASH_CARD_FROM_HAND` a été présenté).
- Cartes qui déclenchent précisément ce protocole : non précisées.
- Carte de défense contre la Sorcière : inconnue de l'intervenant.

## Tableau récapitulatif des actions

| Action | Responsable | Échéance |
|---|---|---|
| Envoyer l'URL du player de dev (facultatif) | Équipes (non nominatif) | Non précisé |
| Adapter la stratégie aux parties simultanées (game ID) | Équipes (non nominatif) | Avant demain (parties simultanées dès demain) |
| Prévoir le traitement de `CONFIRM_TRASH_CARD_FROM_HAND` | Équipes (non nominatif) | À partir de demain (implicite) |

## Prochaine réunion

- **Date** : 26/10/2026
- **Heure de début** : 14:10

## Point a voir 

- demandé pour le temps de la requette max ?
- combien de temps dure une partie ?

## Information Changement

- modification des nom de collone des tableaux de la réunion Jour2_matin.md "### 2. Cartes disponibles"

- Jour2_aprem.md a aussi était modifié pour mettre au propre le fichier car mon collége la fait vite fait.
