# Compte rendu : Questions sur l'API, le déroulement d'un tour et les cartes

- **Date** : 07/10/2026
- **Heure de début / fin** : 14h10 / 14h20
- **Lieu** : Labo Bordeaux Ynov Campus
- **Enregistrement** : réunion enregistrée avec l'accord des participants

## Participants

- **Présents** : Client, Guillaume, Mathis, Damien, Léo
- **Absents** : Personne

## Ordre du jour initial

1. Échanges avec l'arbitre (format, actions légales, erreurs)
2. Déroulement exact d'un tour et fin de partie
3. Cartes : méthode et calendrier

## Sujets abordés

### 1. Échanges avec l'arbitre

**Résumé**
- L'arbitre envoie l'état de la partie au format JSON.
- Aucun modèle de ce JSON n'est disponible. L'intervenant suggère de le stocker dans un fichier ou de l'afficher depuis le serveur web pour en connaître la structure.
- Le motif d'une éjection n'est pas donné dans le protocole entre l'arbitre et la stratégie. Il est en grande partie visible dans les logs visuels, auxquels les équipes n'ont pas encore accès.
- Aujourd'hui, une équipe peut donc être éjectée sans en connaître la raison.

**Décision / réponse**
- Format exact des échanges : pas de document ni d'exemple complet fournis. Les équipes doivent inspecter elles-mêmes le JSON reçu.
- Liste des actions légales : réponse peu claire. L'intervenant dit que c'est l'équipe qui décide de la prochaine action. Il ne précise pas si la liste des actions possibles figure dans le JSON. À confirmer.
- Éjection : exemple donné, deux achats dans le même tour alors qu'un seul est autorisé. Sont aussi invalides : jouer une carte action non autorisée, un achat sans argent suffisant ou au mauvais moment, un format de données non respecté. Un joueur éjecté est classé dernier, derrière un joueur qui a joué toute la partie.
- Non traité : délai maximal de réponse du serveur, interrogation hors de son tour pour les cartes d'attaque et de réaction, visibilité des mains et défausses adverses.

**Actions**
- Enregistrer ou afficher le JSON reçu de l'arbitre pour en connaître la structure.

### 2. Déroulement d'un tour et fin de partie

**Résumé**
- Par défaut, une seule carte action peut être jouée par tour. Certaines cartes action donnent des pouvoirs supplémentaires. Un seul achat par tour est autorisé (déduit de l'exemple d'éjection ci-dessus).
- Phase d'ajustement, en fin de tour : la main et les cartes jouées vont à la défausse, puis l'arbitre pioche 5 cartes du deck. Cela se fait à la fin du tour, non au début du suivant. Certaines cartes spéciales modifient le nombre de cartes piochées.
- Si le deck est vide, l'arbitre mélange la défausse, qui devient le nouveau deck.
- Seules les cartes en main peuvent être jouées.

**Décision / réponse**
- Fin de partie dès qu'une condition est remplie, même en cours de tour : (1) toutes les cartes Province (point de victoire les plus chères) sont achetées ; (2) trois piles de la réserve sont vides ; (3) 150 tours de jeu ont été joués.
- Décompte des points : sur toutes les cartes détenues (deck, main, défausse). Une équipe qui ne fait que passer son tour termine avec 3 points, ceux de ses 3 Domaines de départ.
- Pistes stratégiques évoquées : connaître la composition de son deck et mettre des cartes au rebut. L'intervenant juge cette dernière stratégie « très efficace ».
- Non traité : désignation du gagnant en cas d'égalité.

### 3. Cartes : méthode et calendrier

**Résumé**
- La réserve ne contient pas obligatoirement 20 cartes achetables. L'arbitre choisit sa composition au démarrage de la partie. Elle est commune à tous les joueurs et contient toujours des cartes trésor, point de victoire et action.

**Décision / réponse**
- Trésors : 60 cuivres, 40 argents, 30 ors.
- Cartes point de victoire par type (Domaine, Province, etc.) : 12 pour une partie à 3 ou 4 joueurs, 8 pour une partie à 2 joueurs.
- Cartes action : 10 types en temps normal, 10 exemplaires de chaque, soit 100 cartes. Les types sont choisis par l'arbitre.
- Non traité : format et rythme de réception des cartes, tableau (nom, coût, type, effet) à faire valider par le client.

## Sujets prévus mais non traités

- Délai maximal de réponse du serveur par requête.
- Cartes d'attaque et de réaction : interrogation hors de son tour.
- Visibilité des mains et défausses adverses dans l'état du jeu.
- Désignation du gagnant et égalités.
- Format et calendrier de transmission des cartes, validation par le client.
- Liste complète des cartes et de leurs effets, et protocole de communication : annoncés à l'oral en fin de réunion, non traités sur l'enregistrement.

## Prochaine réunion

- **Date** : 07/10/2026
- **Heure de début** : 16h40
- **Ordre du jour** : Non précisé
