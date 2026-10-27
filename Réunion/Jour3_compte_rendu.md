# Compte rendu d'avancement : projet « Le 4ème Empire »

- **Date** : 26/10/2026
- **Équipe** : Guillaume, Mathis, Damien, Léo
- **Nom de l'équipe** : Le 4ème Empire

## 1. Réalisé

### Infrastructure & code
- Recréation du serveur alwaysdata : l'ancien avait été supprimé après une période de suspension trop longue.
- Création d'un 2ème serveur de test pour essayer des stratégies différentes.
- Amélioration de la stratégie.
- Mise en place d'une stratégie de logs par victoire / défaite : les défaites sont analysées par une IA locale (Qwen 3.8 27B) pour améliorer la stratégie en continu.
- Résolution de problèmes Git.

### Analyse et organisation
- Préparation des questions pour les réunions.
- Rédaction des comptes rendus de réunion (Jour3_matin, Jour3_aprem).

## 2. Prochaines étapes

1. Adapter la stratégie aux parties simultanées (game ID), prévues à partir du 27/10/2026.
2. Implémenter les nouvelles routes de l'arbitre (`CONFIRM_TRASH_CARD_FROM_HAND`, `TRASH_CARD_FROM_HAND`, `CONFIRM_DISCARD_CARD_FROM_HAND`, `DISCARD_CARD_FROM_HAND`, `CONFIRM_DISCARD_DECK`, `CHOOSE_CARD_TO_RECEIVE_IN_DISCARD`, `CHOOSE_CARD_TO_RECEIVE_IN_DECK`) et gérer `ENDGAME`.
3. Poursuivre l'amélioration continue de la stratégie à partir de l'analyse des défaites.
4. Obtenir la réponse sur la durée maximale d'une requête.
5. Réunion suivante : 26/10/2026 à 16h40.
