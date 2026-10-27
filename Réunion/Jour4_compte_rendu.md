# Compte rendu d'avancement : projet « Le 4ème Empire »

- **Date** : 27/10/2026
- **Équipe** : Guillaume, Mathis, Damien, Léo
- **Nom de l'équipe** : Le 4ème Empire

## 1. Réalisé

### Infrastructure & code
- Parties simultanées opérationnelles : parties identifiées par game ID, logs par partie. Le serveur de dev est passé premier du classement ce matin.
- Nouveau fonctionnement du bot de test : un système de poids. Le bot analyse l'état de la partie et, selon les possibilités, donne un poids à chaque carte.
- Correction d'un problème de poids : le bot partait presque toujours sur les Jardins (environ 400 parties sur 500). Une carte censée baisser leur poids faisait l'inverse.
- Ajustement des poids pour un jeu plus équilibré : taux de victoire d'environ 70 % (65 % sur certains lots), contre 80 % avec la stratégie Jardins.

### Analyse et organisation
- Préparation des questions pour les réunions.
- Rédaction des comptes rendus de réunion (Jour4_matin, Jour4_aprem, Jour4_compt_rendu).

## 2. Prochaines étapes

1. Gérer les routes liées aux nouvelles cartes : `DISCARD_CARD_FROM_HAND` (Milice) et `CONFIRM_DISCARD_DECK` (Chancelier).
2. Prévoir `SKIP_CARD_RECEPTION_IN_HAND` et `TRASH_MONEY_CARD_FOR_BETTER_MONEY_CARD`.
3. Détecter la présence des Jardins et appliquer une stratégie dédiée (suggestion du client).
4. Étudier le combo Recrue / Bandit, signalé par le client comme efficace.
5. Analyser les parties gagnées et perdues avec les logs classés par victoire, et en tirer des statistiques.
6. Passer sur le serveur officiel ce qui marche sur le serveur de test (l'officiel a encore le code d'hier).
