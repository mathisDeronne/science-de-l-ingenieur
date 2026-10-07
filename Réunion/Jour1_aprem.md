# Compte rendu : Règles du jeu et protocole avec l'arbitre (2e réunion)

- **Date** : Non précisé
- **Heure de début / fin** : Non précisé (durée d'environ 9 min d'après l'enregistrement)
- **Lieu** : Non précisé
- **Enregistrement** : réunion enregistrée

## Participants

- **Présents** : Non précisé (l'enregistrement n'identifie pas les intervenants). Un « groupe 4 » est mentionné à l'oral : à confirmer.
- **Excusés** : Non précisé
- **Absents** : Non précisé

## Ordre du jour initial

Non précisé. La réunion a démarré par les questions des équipes survenues depuis le matin. En cours de réunion, trois sujets à traiter dans l'ordre ont été annoncés :

1. Informations générales sur le fonctionnement d'une partie
2. Liste des cartes et de leurs effets
3. Protocole de communication entre l'arbitre et la stratégie

## Sujets abordés

### 1. Format de l'état du jeu et actions possibles

**Résumé**
- L'arbitre envoie l'état du jeu au format JSON.
- L'intervenant n'a pas de modèle sous la main. Il suggère de stocker ou d'afficher le JSON reçu sur le serveur web pour l'examiner.
- C'est la stratégie de l'équipe qui choisit la prochaine action.

**Décision / réponse**
- Les équipes doivent inspecter elles-mêmes le JSON reçu.
- Réponse peu claire sur la question « l'arbitre fournit-il les actions possibles dans le JSON ? ». À confirmer.

**Actions**
- Enregistrer ou afficher le JSON reçu par le serveur pour en connaître la structure. Responsable : les équipes (non nominatif). Échéance : Non précisé.

### 2. Éjection de la partie et logs

**Résumé**
- Le motif d'une éjection n'est pas communiqué dans le protocole entre l'arbitre et la stratégie.
- Les logs visuels, auxquels les équipes auront accès plus tard, en donnent en grande partie les raisons.
- Aujourd'hui, une équipe peut donc être éjectée sans en connaître la cause.
- Exemple d'action invalide : deux achats dans le même tour alors qu'un seul est autorisé.

**Décision / réponse**
- Sont aussi invalides : jouer une carte action non autorisée, un achat sans argent suffisant ou au mauvais moment, un format de données non respecté.
- Un joueur éjecté est classé dernier de la partie, y compris derrière un joueur qui a joué toute la partie.

**Actions** : aucune.

### 3. Conditions de fin de partie

**Résumé**
- La partie s'arrête dès qu'une des trois conditions est remplie, même si un joueur n'a pas fini son tour.
- Conditions : (1) toutes les cartes Province (cartes point de victoire les plus chères) sont achetées ; (2) trois piles de la réserve sont vides ; (3) 150 tours de jeu ont été joués.

**Décision / réponse** : les trois conditions ci-dessus.

**Actions** : aucune.

### 4. Phase d'ajustement, pioche et deck vide

**Résumé**
- À la fin du tour, après les phases d'action et d'achat, la main et les cartes jouées vont à la défausse. L'arbitre pioche ensuite 5 cartes du dessus du deck.
- Cela se fait à la fin du tour, et non au début du tour suivant. L'intervenant indique que cela peut avoir une importance pour les cartes jouées ensuite par les autres joueurs.
- Certaines cartes spéciales peuvent modifier le nombre de cartes piochées.
- Si le deck est vide, l'arbitre mélange la défausse, qui devient le nouveau deck.

**Décision / réponse**
- Pioche par défaut : 5 cartes.
- Mélanger la défausse est automatique ; l'ordre des cartes n'est pas connu du joueur.
- Pistes stratégiques évoquées : connaître la composition de son deck et mettre des cartes au rebut pour garder celles qui servent. L'intervenant juge cette dernière stratégie « très efficace ».

**Actions** : aucune.

### 5. Décompte des points

**Résumé**
- Les points de victoire sont comptés sur l'ensemble des cartes : deck, main et défausse.
- Un joueur qui ne fait que passer son tour termine avec 3 points, ceux de ses 3 cartes Domaine de départ.

**Décision / réponse** : décompte sur toutes les cartes détenues.

**Actions** : aucune.

### 6. Actions par tour

**Résumé**
- Par défaut, une seule carte action peut être jouée par tour.
- Certaines cartes action donnent des pouvoirs supplémentaires (par exemple plus d'actions).

**Décision / réponse**
- Seules les cartes en main peuvent être jouées, pas celles du deck ou de la défausse.

**Actions** : aucune.

### 7. Composition de la réserve

**Résumé**
- Au démarrage, l'arbitre choisit la liste des cartes de la réserve, commune à tous les joueurs. Elle ne contient pas obligatoirement 20 cartes achetables.
- La réserve contient toujours des cartes trésor, des cartes point de victoire et des cartes action.

**Décision / réponse**
- Trésors : 60 cuivres, 40 argents, 30 ors.
- Cartes point de victoire par type (Domaine, Province, etc.) : 12 pour une partie à 3 ou 4 joueurs, 8 pour une partie à 2 joueurs.
- Cartes action : 10 types en temps normal, 10 exemplaires de chaque, soit 100 cartes. Les types sont choisis par l'arbitre.

**Actions** : aucune.

## Sujets prévus mais non traités

- Liste complète des cartes et de leurs effets.
- Protocole de communication entre l'arbitre et la stratégie : annoncé comme prochain sujet en fin de réunion, non traité sur l'enregistrement.
- Liste des commandes : demandée par une équipe, renvoyée aux sujets 2 et 3 ci-dessus.

## Tableau récapitulatif des actions

| Action | Responsable | Échéance |
|---|---|---|
| Enregistrer ou afficher le JSON reçu de l'arbitre pour en connaître la structure | Équipes (non nominatif) | Non précisé |

## Prochaine réunion

Non précisé. La suite sur le protocole était annoncée en fin d'enregistrement, sans date.

## Points à vérifier (transcription automatique)

- C'est quoi le NVP pour la prochaine fois 