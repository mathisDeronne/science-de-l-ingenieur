# Compte rendu : Logs, système de poids, Jardins et combo Recrue / Bandit

- **Date** : 27/10/2026
- **Heure de début / fin** : 14h40 / 14h50
- **Lieu** : Salle 207 Bordeaux Ynov Campus
- **Enregistrement** : réunion enregistrée avec l'accord des participants

## Participants

- **Présents** : Client, Guillaume, Mathis, Damien, Léo 
- **Absents** : Personne

## Ordre du jour initial

avancement.

## Sujets abordés

avancement.

### 1. Logs des parties sur la page d'accueil

**Résumé**
- Le client a modifié la page d'accueil : les logs des joueurs sont maintenant classés par victoire.
- Objectif : retrouver rapidement les parties gagnées et perdues, pour analyser les situations.

### 2. Classement

**Résumé**
- Le classement bouge beaucoup : l'équipe a un peu reculé.
- Le « remake » a perdu des places (3e), mais les écarts se jouent à très peu de points d'Elo.
- Le serveur officiel utilise encore le code d'hier.

### 3. Bot de test : système de poids

**Résumé**
- Pas de question sur les réunions précédentes.
- Le bot de test utilise maintenant un programme par poids. Le client demande de montrer comment les poids sont adaptés.
- **Problème d'avant** : sur 500 parties, environ 400 étaient jouées avec les Jardins. Une carte était censée faire baisser le poids des Jardins, mais faisait l'inverse : dès qu'une partie avec Jardins était possible, le bot partait sur les Jardins.
- **Résultats** : avec les Jardins, le taux de victoire était de 80 %. Après ajustement des poids pour un jeu plus équilibré, il est d'environ 70 %, voire 65 % sur certains lots.
- Conclusion de l'équipe : les Jardins marchaient bien, mais c'est une stratégie à une seule idée (« one trick pony »).

**Décision / réponse**
- Le client propose de détecter quand les Jardins sont présents dans le magasin et d'appliquer alors une stratégie dédiée.

### 4. Élément de protocole : quantités de cartes

**Résumé**
- Le client rappelle un élément qu'il n'avait pas évoqué : quand l'arbitre envoie une quantité de cartes (réserve ou main), elle est donnée sous forme de table associative (nom de la carte → quantité).
- Le nom exact de la propriété n'est pas audible (quelque chose comme « quantities »).

### 5. Nouvelles cartes

**Décision / réponse** : pas de nouvelles cartes aujourd'hui.

### 6. Discussion stratégique : combo Recrue / Bandit

**Résumé**
- Le client a vu par hasard une partie entre deux groupes forts. Un joueur utilisait une stratégie Recrue + Bandit : les Bandits ramenaient vite de l'Or dans son deck, et les Recrues lui faisaient piocher beaucoup de cartes, avec toujours plusieurs Ors en main. La partie s'est terminée très vite.
- Selon le client, c'est un combo intéressant : en jouant le Bandit dès le début, on fait entrer vite de l'Or dans son deck, et on peut acheter rapidement des Recrues.
- L'équipe a vu un cas semblable avec les Bandits. Son calcul se basait sur l'Or acheté et non sur l'Or restant dans la réserve. Elle a fini la partie avec 15 Ors encore en réserve et l'a perdue.

**Décision / réponse**
- Conseil du client : regarder ce qui se passe dans les parties et faire des statistiques de ce genre. Il ne va pas plus loin, car il n'est pas le mieux classé en stratégie.

## Sujets prévus mais non traités

- Aucun.

## Tableau récapitulatif des actions

| Action | Responsable | Échéance |
|---|---|---|
| Détecter la présence des Jardins et appliquer une stratégie dédiée (suggestion du client) | Équipes (non nominatif) | Non précisé |
| Analyser les parties gagnées / perdues (logs classés par victoire) et en tirer des statistiques | Équipes (non nominatif) | Non précisé |

## Prochaine réunion

- **Date** : 27/10/2026
- **Heure de début** : 16h40

