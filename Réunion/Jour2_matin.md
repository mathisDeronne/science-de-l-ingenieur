# Compte rendu : Cartes disponibles, API et communication avec l'arbitre

- **Date** : 08/10/2026
- **Heure de début / fin** : 9h20 / environ 9h30
- **Lieu** : 302
- **Enregistrement** : réunion enregistrée

## Participants

- **Présents** : Client, Guillaume, Mathis, Damien, Léo
- **Absents** : Personne

## Ordre du jour initial

Clarifier les cartes actuellement disponibles dans le jeu ainsi que le fonctionnement de l'API permettant aux bots de communiquer avec l'arbitre.

## Sujets abordés

### 1. Version de Dominion utilisée et cartes disponibles

**Résumé**

- Le jeu est basé sur la version **2008 de Dominion**, avec quelques modifications.
- Cette version peut servir de référence pour connaître les cartes susceptibles d'être ajoutées.
- Toutes les cartes de la version 2008 ne sont cependant pas forcément disponibles.
- Certaines cartes présentes dans l'ancienne version, comme **Woodcutter**, sont actuellement implémentées.
- L'Atelier et l'Aventurier ne semblent pas être disponibles pour le moment.
- Actuellement, **5 cartes Action** sont présentes dans le pool.
- À terme, le pool doit comporter **10 cartes Action**.
- Les cartes Action citées pendant la réunion sont :
  - Festival ;
  - Laboratory ;
  - Village ;
  - Woodcutter ;
  - Market.
- Les cartes Trésor disponibles sont :
  - Copper ;
  - Silver ;
  - Gold.
- Les trois niveaux classiques de cartes Victoire sont également présents :
  - Estate ;
  - Duchy ;
  - Province.
- Les cartes Curse ne sont pas encore présentes, mais devraient être ajoutées ultérieurement.

**Décision / réponse**

- La liste complète des cartes qui seront utilisées ne sera pas communiquée immédiatement.
- La version 2008 de Dominion peut être utilisée comme référence pour identifier les cartes.
- Pour les premiers jours, le jeu reste volontairement simple afin de permettre aux équipes de mettre en place leur système de stratégie.

**Actions**

- Identifier les cartes réellement présentes dans la réserve à partir de l'état du jeu envoyé par le serveur.
- Rechercher ensuite les effets des cartes identifiées.
- Préparer progressivement une stratégie capable de prendre en compte les nouvelles cartes ajoutées au jeu.

---

### 2. Communication avec l'arbitre et identifiant de partie

**Résumé**

- La communication entre le bot et l'arbitre utilise une **API HTTP**.
- L'arbitre fournit un **identifiant de partie**.
- Cet identifiant doit être renvoyé dans la réponse du bot.
- Actuellement, les parties sont principalement exécutées les unes après les autres.
- À terme, plusieurs parties seront jouées **simultanément**.
- Le bot devra donc être capable de conserver un état différent pour chaque partie.
- Les informations mémorisées ne doivent pas être stockées comme si une seule partie existait.

**Décision / réponse**

- L'identifiant de partie doit être utilisé comme clé pour différencier les différents états de jeu.
- Le bot devra pouvoir prendre une décision en fonction de la partie concernée sans mélanger les informations provenant de plusieurs parties.

**Actions**

- Prévoir dès maintenant un stockage séparé des informations pour chaque `game_id`.
- Éviter les variables globales représentant l'état d'une seule partie.
- Préparer le bot à gérer plusieurs parties simultanément.

Exemple de structure possible :

```python
games = {
    "game_id_1": {...},
    "game_id_2": {...},
}
```

---

### 3. Tram `/name`

**Résumé**

- L'arbitre appelle une tram HTTP GET `/name`.
- Le serveur du bot doit répondre avec le nom de l'équipe sous forme de chaîne de caractères.
- Ce nom apparaît ensuite dans les logs des parties.

**Décision / réponse**

- Le nom actuellement présent dans le template (`Default player name`) doit être remplacé par le nom choisi par l'équipe.

**Actions**

- Choisir le nom de l'équipe.
- Modifier la réponse de `/name`.

---

### 4. Tram `start_game`

**Résumé**

- La tram `start_game` est appelée au début de chaque nouvelle partie.
- Elle reçoit notamment l'identifiant de la partie.
- Cette tram peut être utilisée pour initialiser les informations internes nécessaires au bot pour cette partie.

**Décision / réponse**

- À chaque début de partie, le bot peut créer un nouvel espace de stockage associé au `game_id`.
- Une réponse doit être renvoyée à l'arbitre afin de confirmer que le début de partie a bien été pris en compte.

**Actions**

- Initialiser les données propres à chaque partie dans `start_game`.
- Associer ces données au `game_id`.

---

### 5. Tram `start_turn`

**Résumé**

- Une tram de début de tour est appelée par l'arbitre lorsqu'un nouveau tour commence.
- Cette tram permet au bot de savoir qu'un nouveau tour débute.

**Décision / réponse**

- Cette tram pourra notamment servir à :
  - incrémenter le numéro du tour ;
  - réinitialiser certaines informations propres au tour ;
  - préparer la stratégie du bot.

**Actions**

- Ajouter si nécessaire un compteur de tours propre à chaque partie.

---

### 6. Tram principale `/play`

**Résumé**

- `/play` est la méthode principale utilisée pour demander une décision au bot.
- Il s'agit d'une requête HTTP POST.
- Le serveur reçoit dans cette requête l'état actuel de la partie.
- Le bot doit répondre avec une propriété `decision`.

Plusieurs types de décisions sont possibles.

#### Terminer le tour

Pour ne plus effectuer d'action :

```text
END_TURN
```

#### Acheter une carte

Pour acheter une carte :

```text
BUY NomDeLaCarte
```

Exemple :

```text
BUY Gold
```

Le nom de la carte doit correspondre exactement à celui communiqué par le serveur.

#### Jouer une carte Action

Pour jouer une carte Action présente dans la main :

```text
ACTION NomDeLaCarte
```

Exemple :

```text
ACTION Village
```

**Décision / réponse**

- Le bot doit utiliser les noms des cartes tels qu'ils sont envoyés par le serveur.
- Il n'est pas nécessaire d'indiquer quelles cartes Trésor sont utilisées lors d'un achat.

**Actions**

- Commencer par analyser l'objet `Game` reçu par `/play`.
- Afficher son contenu dans les logs afin de comprendre précisément les données disponibles.
- Ajouter progressivement les premières règles de décision.

---

### 7. Gestion de l'argent et des achats

**Résumé**

- Lors d'un achat, il n'est pas nécessaire de préciser quels Copper, Silver ou Gold sont utilisés.
- L'arbitre calcule automatiquement la quantité totale d'argent disponible pendant la phase d'achat.
- Le joueur peut ensuite effectuer plusieurs achats si son nombre d'achats le permet.
- Les bonus provenant éventuellement des cartes Action sont également pris en compte dans le total disponible.

**Décision / réponse**

- Le bot doit uniquement choisir la carte à acheter.
- L'arbitre se charge de vérifier que le joueur possède suffisamment d'argent et suffisamment d'achats disponibles.

---

### 8. Gestion des actions invalides

**Résumé**

- L'arbitre vérifie la validité de chaque décision envoyée par le bot.
- Une tentative d'achat d'une carte trop chère constitue une décision invalide.
- Une décision invalide peut entraîner l'éjection immédiate du bot de la partie.

**Décision / réponse**

- La stratégie doit toujours vérifier qu'une décision est valide avant de l'envoyer à l'arbitre.

**Actions**

- Vérifier notamment :
  - l'argent disponible ;
  - les cartes présentes dans la réserve ;
  - les cartes présentes dans la main ;
  - les actions disponibles ;
  - les achats disponibles.

---

### 9. Informations disponibles dans l'état du jeu

**Résumé**

Lors de l'appel à `/play`, le bot reçoit un objet JSON contenant l'état actuel du jeu.

Plusieurs propriétés ont été précisées pendant la réunion.

#### `Finish`

- Cette propriété indique l'état de fin de partie.
- Elle semble actuellement avoir peu d'utilité pendant le déroulement normal de la partie.

#### `Players`

- Contient une liste d'informations relatives aux joueurs.
- Les informations d'un joueur comportent notamment une propriété `Name`.
- Toutes les informations privées des autres joueurs ne sont pas accessibles.
- En particulier, le bot ne connaît pas directement le nombre de points de victoire des adversaires.

#### `Stock`

- Contient la quantité de cartes disponibles dans la réserve.
- Cette propriété permet donc de déterminer quelles cartes sont actuellement présentes dans la partie.

**Décision / réponse**

- `Stock` est une information importante pour découvrir automatiquement les cartes disponibles.
- Dans un premier temps, le bot peut simplement afficher cette propriété dans ses logs.

**Actions**

- Ajouter un `print` de `Stock`.
- Observer les parties lancées automatiquement par l'arbitre.
- Recenser les noms des cartes rencontrées.
- Utiliser cette liste pour documenter progressivement les effets et les coûts des cartes.

---

### 10. Première stratégie à mettre en place

**Résumé**

- L'objectif immédiat n'est pas de construire une stratégie complexe.
- Il faut d'abord disposer d'un bot fonctionnel capable de communiquer correctement avec l'arbitre.
- Le template fourni répond actuellement principalement par `END_TURN`.
- Une première stratégie plus performante doit être livrée rapidement.

**Décision / réponse**

La progression envisagée est :

1. communiquer correctement avec l'arbitre ;
2. afficher et comprendre l'état du jeu ;
3. identifier les cartes présentes grâce à `Stock` ;
4. connaître leurs coûts et leurs effets ;
5. mettre en place une stratégie d'achat simple ;
6. ajouter progressivement les cartes Action et leurs décisions particulières.

**Actions**

- Dans un premier temps, afficher dans les logs :
  - l'état général de la partie ;
  - le contenu de `Stock` ;
  - éventuellement les informations sur les joueurs et la main.
- Construire ensuite les premières règles déterministes du bot.

## Sujets prévus mais non traités

- Liste définitive des 10 cartes Action.
- Effets précis de toutes les cartes disponibles.
- Coût précis de chaque carte dans l'implémentation.
- Fonctionnement détaillé des futures cartes Curse.
- Informations complètes disponibles dans l'objet `Players`.
- Structure exacte de tous les champs de l'objet `Game`.
- Stratégie optimale à adopter face aux autres bots.
- Gestion détaillée des choix spécifiques provoqués par certaines cartes Action.

## Tableau récapitulatif des actions

| Action | Responsable | Échéance |
|---|---|---|
| Afficher le contenu de `Stock` dans les logs | Équipe | Dès que possible |
| Recenser les cartes réellement présentes dans les parties | Équipe | Dès que possible |
| Rechercher les effets et coûts des cartes identifiées | Équipe | Après identification |
| Remplacer le nom par défaut du bot | Équipe | Dès que possible |
| Préparer un stockage séparé pour chaque `game_id` | Équipe | Avant les parties simultanées |
| Mettre en place une première stratégie d'achat | Équipe | Au plus tôt |
| Vérifier systématiquement la validité des décisions avant leur envoi | Équipe | Permanent |

## Prochaine réunion

- **Date** : 8/10/2026
- **Heure de début** : 14:20