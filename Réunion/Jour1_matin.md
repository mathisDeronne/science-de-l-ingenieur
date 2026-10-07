# Compte rendu : Questions sur le projet de jeu (arbitre, règles, cartes)

- **Date** : 07/10/2026
- **Heure de début / fin** : 10h50 / 11h00
- **Lieu** : Salle 203 Bordeaux Ynov Campus
- **Enregistrement** : réunion enregistrée avec l'accord des participants

## Participants

- **Présents** : Client, Guillaume, Mathis, Damien, Léo
- **Absents** : Personne

## Ordre du jour initial

Réunion de lancement du projet et présentation des objectifs généraux du projet.

## Sujets abordés

### 1. Fonctionnement général d'une partie

**Résumé**
- L'arbitre tire au sort les équipes, lance la partie, puis interroge à chaque tour le serveur de chaque équipe avec l'état du jeu et demande la prochaine action.
- L'arbitre met à jour l'état du jeu et décide si la partie est terminée.
- Le template par défaut répond uniquement « je passe mon tour », ce qui est une action valide.
- Toute action invalide ou coup illégal entraîne l'éjection de la partie.

**Décision / réponse**
- Priorité n°1 : mettre en place un serveur HTTP et envoyer son URL à l'arbitre pour entrer dans la compétition.
- Les équipes qui entrent aujourd'hui seront normalement moins bien classées que celles déjà entrées.
- La stratégie doit respecter les règles du jeu.

**Actions**
- Mettre en place le serveur HTTP (à partir du template par défaut) et transmettre l'URL à l'arbitre. Responsable : l'équipe 4. Échéance : dès que possible.

### 2. Classement et évaluation

**Résumé**
- Classement de type Elo : battre un joueur fort rapporte beaucoup de points, battre un joueur faible peu. Perdre contre un joueur fort coûte peu, perdre contre un joueur faible coûte cher.
- Un joueur éjecté pour action invalide est dernier de la partie et perd des points.
- Le client regardera le classement en fin de journée.
- Les équipes qui ne sont pas en jeu ne sont pas classées (formulation à confirmer).

**Décision / réponse**
- Le rôle du joueur est de gagner les parties.
- MVP : répondre « je passe mon tour ». Objectif suivant : acheter des cartes point de victoire.

### 3. Règles du jeu et documentation

**Résumé**
- Il n'existe pas de document complet des règles. L'intervenant ne les connaît pas encore toutes et les découvrira au fil des jours.
- Les équipes demandent la liste des cartes (une vingtaine) et leurs effets. L'intervenant propose de donner le contexte général puis de répondre aux questions carte par carte.
- Il suggère que les équipes rédigent elles-mêmes une synthèse des points abordés.

**Décision / réponse**
- Pas de document de règles disponible pour l'instant.
- Le nom du template a été épelé à l'oral : «https://dopynion-template.lecalamar.fr/».

### 4. Structure du jeu : cartes et piles

**Résumé**
- Deck de départ : 10 cartes, soit 7 cuivres (« copper », la plus petite monnaie) et 3 domaines (les plus petits points de victoire).
- Piles propres à chaque joueur : deck (pioche), main, défausse.
- Piles communes : le rebut (cartes jetées définitivement hors de la partie) et la réserve (magasin où l'on achète des cartes ; une carte achetée n'est plus disponible pour les autres).
- Un tour comprend une phase action et une phase achat, puis une phase d'ajustement. La main par défaut est de 5 cartes, sans limite de cartes en main.

**Décision / réponse**
- Il n'est pas obligatoire de jouer toutes ses cartes pendant un tour.


## Sujets prévus mais non traités

- Liste complète des cartes et de leurs effets (reportée aux prochains jours).
- Délais du projet : évoqués comme « déjà plus ou moins » connus, non rediscutés. À confirmer.
- Détail de la phase d'ajustement de fin de tour : annoncée comme importante pour la suite, non développée.

## Tableau récapitulatif des actions

| Action | Responsable | Échéance |
|---|---|---|
| Mettre en place un serveur HTTP (template par défaut) et envoyer l'URL à l'arbitre | Équipes 4 | Dès que possible |
| Rédiger une synthèse des points abordés | Équipes 4 | Non précisé |

## Prochaine réunion

- **Date** : 07/10/2026
- **Heure de début** : 14h10

## Points à vérifier (transcription automatique)

- Phase d'ajustement : la transcription dit que l'arbitre prend « les cinq cartes du dessus » et que cela devient « votre nouvel magasin ». Il s'agit probablement de la nouvelle **main**. À confirmer.
- Les intervenants ne sont pas distingués dans la transcription.