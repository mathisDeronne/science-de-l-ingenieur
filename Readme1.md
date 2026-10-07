# Pré-rapport — Première réunion client 
## Projet : Jeu de stratégie — Gestion d’un royaume

### 1. Équipe projet

- Léo
- Damien
- Mathis
- Guillaume

---

# 2. Objectif de la première réunion

Cette première réunion a pour objectif de comprendre précisément le besoin du client avant de commencer le développement.

Le client peut avoir une idée générale du projet sans être capable d'exprimer précisément toutes les fonctionnalités attendues. Notre rôle est donc de **transformer son besoin en exigences claires et vérifiables**.

À la fin de la réunion, nous devons notamment savoir :

- Quel est le fonctionnement général du jeu ?
- Quelles sont les règles précises ?
- Quelles sont les fonctionnalités indispensables ?
- Quelles fonctionnalités sont secondaires ?
- Comment se déroule une partie ?
- Comment les joueurs gagnent-ils ?
- Quel est le rôle de l'arbitre ?
- Quelles informations doivent être accessibles via l'API ?
- Quelles sont les contraintes techniques imposées ?
- Quelles sont les contraintes de délai ?
- Quel est le minimum nécessaire pour avoir une première version jouable ?
- Comment le client va-t-il évaluer le projet ?

L'objectif est de pouvoir ensuite construire un **MVP**, puis améliorer progressivement le projet par développement itératif et incrémental.

---

# 3. Méthode de travail envisagée

## Communication avec le client

Les réunions doivent rester courtes et efficaces.

- Éviter les réunions de plus d'une heure.
- Préparer un ordre du jour avant chaque réunion.
- Faire un compte rendu après chaque réunion.
- Envoyer le compte rendu au client avant la réunion suivante lorsque cela est pertinent.
- Vérifier régulièrement que notre compréhension du besoin correspond bien à celle du client.

Chaque compte rendu sera réalisé en **Markdown** et déposé sur GitHub.

Le compte rendu devra contenir :

1. Date et heure
2. Ordre du jour
3. Personnes réellement présentes
4. Sujets réellement abordés
5. Questions posées
6. Réponses apportées
7. Décisions prises
8. Points restant à clarifier
9. Actions à réaliser
10. Prochaine étape

---

# 4. Organisation du développement

Le développement sera réalisé de manière **itérative et incrémentale**.

L'objectif est de ne pas attendre la fin du projet pour présenter le résultat.

Nous chercherons à obtenir rapidement une première version fonctionnelle, même partielle, puis à l'améliorer progressivement.

Principe :

**Comprendre → développer → tester → présenter → recueillir les retours → améliorer.**

Il est important de pouvoir arriver rapidement à une version jouable afin de détecter tôt les problèmes de compréhension ou de conception.

---

# 5. Suivi quotidien

Chaque journée de développement devra permettre de mesurer l'avancement.

Prévoir :

- un rapport quotidien ;
- une démonstration d'environ 10 minutes en fin de journée ;
- un suivi des fonctionnalités réalisées ;
- un suivi des problèmes rencontrés ;
- un suivi des décisions techniques.

Un classement intermédiaire peut être réalisé régulièrement, notamment tous les trois jours, afin de mesurer l'évolution du projet.

---

# 6. Contraintes générales à clarifier avec le client

Avant de développer, nous devons connaître :

### Coûts

- Quels sont les coûts à respecter ?
- Y a-t-il des ressources ou services payants interdits ?
- L'hébergement est-il imposé ?

### Délais

- Quelle est la date limite ?
- Existe-t-il des jalons intermédiaires ?
- Quelle version doit être disponible à chaque étape ?

### Besoin

- Quelles fonctionnalités sont obligatoires ?
- Quelles fonctionnalités sont souhaitées mais non indispensables ?
- Quelles fonctionnalités peuvent être reportées ?

### Qualité

- Quels sont les critères permettant de considérer le projet comme terminé ?
- Quels sont les critères de qualité attendus ?
- Comment les fonctionnalités seront-elles testées ?

### Marché / compétition

Le projet étant réalisé dans un contexte de compétition, il faut chercher à obtenir rapidement une version fonctionnelle.

Une stratégie possible est donc :

**avoir rapidement un produit minimal fonctionnel → le tester → l'améliorer → ajouter les fonctionnalités à forte valeur.**

---

# 7. Questions prioritaires à poser au client

## A. Comprendre le jeu

1. Pouvez-vous nous expliquer le jeu comme si nous étions de nouveaux joueurs ?
2. Quel est l'objectif principal d'une partie ?
3. Comment un joueur gagne-t-il ?
4. Combien de joueurs peuvent participer ?
5. Une partie dure combien de temps environ ?
6. Que se passe-t-il au début d'une partie ?
7. Que se passe-t-il pendant un tour ?
8. Que se passe-t-il à la fin d'un tour ?
9. Que se passe-t-il à la fin d'une partie ?

---

# 8. Règles du jeu

Nous avons actuellement compris que le joueur doit gérer un royaume et prendre les meilleures décisions possibles afin d'obtenir le plus de points de victoire.

À confirmer avec le client :

- Le jeu commence avec 10 cartes.
- Il existe des cartes trésor.
- Les cartes trésor permettent notamment d'acheter d'autres cartes.
- Certaines cartes donnent des points de victoire.
- Il existe au minimum 20 types de cartes différents.
- Une partie comporte entre 1 et 3 concurrents.
- Chaque tour comporte 3 phases successives.

### Questions importantes

1. Que représentent exactement les 10 cartes de départ ?
2. Les 10 cartes sont-elles identiques pour tous les joueurs ?
3. Combien de cartes un joueur possède-t-il au maximum ?
4. Peut-il perdre des cartes ?
5. Peut-il échanger des cartes ?
6. Comment gagne-t-on des trésors ?
7. Comment gagne-t-on des points de victoire ?
8. Peut-on acheter plusieurs cartes pendant un même tour ?
9. Quel est le prix de chaque carte ?
10. Les prix peuvent-ils changer ?
11. Comment détermine-t-on le gagnant ?
12. Que se passe-t-il en cas d'égalité ?

---

# 9. Les trois phases d'un tour

## Phase 1 — Cartes action

Nous avons compris que le joueur peut jouer des cartes d'action pouvant déclencher des événements ou avoir des effets sur les autres royaumes.

Questions :

- Combien de cartes d'action peut-on jouer ?
- Les cartes sont-elles choisies par le joueur ou tirées au hasard ?
- Une carte peut-elle agir sur plusieurs royaumes ?
- Peut-on choisir la cible d'une carte ?
- Les effets sont-ils immédiats ?
- Les effets peuvent-ils durer plusieurs tours ?
- Peut-on contrer une action ?
- Que se passe-t-il lorsqu'une action est impossible ?

---

## Phase 2 — Boutique

Le joueur peut acheter des cartes dans une boutique.

Questions :

- Comment fonctionne exactement la boutique ?
- Quelles cartes sont disponibles ?
- Les cartes disponibles sont-elles identiques pour tous les joueurs ?
- La boutique est-elle renouvelée ?
- Quand les cartes sont-elles remplacées ?
- Combien coûte chaque carte ?
- Peut-on acheter plusieurs cartes ?
- Que se passe-t-il si le joueur n'a pas assez de trésors ?
- Les autres joueurs peuvent-ils acheter les mêmes cartes ?

---

## Phase 3 — Automatique / Arbitre

Cette phase semble être gérée automatiquement par l'arbitre.

Nous avons compris que l'arbitre doit notamment :

- ranger les cartes ;
- tirer de nouvelles cartes ;
- faire avancer le jeu.

Questions :

1. Que fait exactement l'arbitre ?
2. Quelles décisions sont automatiques ?
3. Quelles décisions restent à la charge du joueur ?
4. Dans quel ordre les actions sont-elles exécutées ?
5. Que se passe-t-il lorsqu'une action provoque plusieurs effets ?
6. Comment gérer les erreurs ou les situations impossibles ?
7. L'arbitre doit-il vérifier que les règles sont respectées ?
8. L'arbitre doit-il calculer automatiquement les scores ?

---

# 10. Les cartes

Le projet doit comporter au minimum 20 types de cartes différents.

Questions :

- Quels sont les différents types de cartes ?
- Quelles informations contient une carte ?
- Chaque carte possède-t-elle un coût ?
- Chaque carte possède-t-elle un effet ?
- Certaines cartes sont-elles uniques ?
- Peut-on posséder plusieurs exemplaires d'une même carte ?
- Comment les cartes sont-elles tirées ?
- Comment sont-elles mélangées ?
- Existe-t-il une pioche ?
- Existe-t-il une défausse ?
- Que se passe-t-il lorsque la pioche est vide ?

Il faudra obtenir du client **la liste complète des cartes et leurs règles**, idéalement sous une forme suffisamment précise pour pouvoir les implémenter.

---

# 11. Interaction entre les royaumes

C'est un point important du projet.

Questions :

- Que signifie exactement « agir sur un autre royaume » ?
- Un joueur peut-il attaquer directement un autre joueur ?
- Peut-on voler des trésors ?
- Peut-on empêcher un joueur de jouer ?
- Peut-on modifier les cartes d'un autre joueur ?
- Les effets sont-ils visibles immédiatement ?
- Les joueurs connaissent-ils les cartes des autres royaumes ?
- Quelles informations sont publiques ?
- Quelles informations sont privées ?

---

# 12. API et arbitre

Le projet doit respecter les règles de la compétition concernant l'API.

À clarifier :

- Quelle API devons-nous fournir ?
- Quelle est la documentation officielle de l'API ?
- Quels endpoints sont obligatoires ?
- Quel format de données doit être utilisé ?
- Quelles informations l'arbitre nous envoie-t-il ?
- Quelles informations devons-nous renvoyer à l'arbitre ?
- Comment l'arbitre identifie-t-il un joueur ?
- Comment une partie est-elle créée ?
- Comment un tour est-il lancé ?
- Comment une action est-elle envoyée ?
- Comment les erreurs doivent-elles être retournées ?
- Comment l'authentification fonctionne-t-elle ?
- Existe-t-il des limites de temps pour les réponses de l'API ?

Nous devons obtenir l'adresse de l'API et les règles précises de communication HTTP avant d'implémenter cette partie.

---

# 13. Hébergement

L'hébergement prévu est **Alwaysdata**.

À confirmer :

- Le compte est-il déjà disponible ?
- Quelles technologies sont autorisées ?
- Quelle version de chaque technologie devons-nous utiliser ?
- Comment déployer le projet ?
- Quelles sont les limites du serveur ?
- Quelle base de données peut être utilisée ?
- Comment gérer les variables de configuration et les secrets ?
- Comment effectuer les mises à jour ?

---

# 14. Choix techniques

Les choix techniques sont réalisés par l'équipe.

Le client définit le besoin et les contraintes ; l'équipe choisit ensuite les technologies permettant de répondre au besoin.

Avant de choisir définitivement une technologie, nous devons connaître :

- les contraintes de l'API ;
- les contraintes du serveur ;
- les performances attendues ;
- les besoins en stockage ;
- les besoins en temps réel ;
- les besoins de sécurité ;
- les règles de la compétition.

---

# 15. Priorisation des fonctionnalités

Nous devons séparer les fonctionnalités en trois catégories.

### Priorité 1 — Indispensable

Fonctionnalités nécessaires pour obtenir une première partie jouable.

Exemples à confirmer :

- création d'une partie ;
- gestion des joueurs ;
- gestion des royaumes ;
- gestion des cartes ;
- gestion des trésors ;
- système de points de victoire ;
- déroulement des trois phases ;
- boutique ;
- arbitre ;
- calcul du gagnant ;
- communication avec l'API.

### Priorité 2 — Importante

Fonctionnalités améliorant le jeu mais qui ne sont pas forcément nécessaires au premier prototype.

### Priorité 3 — Bonus

Fonctionnalités pouvant être ajoutées si le temps le permet.

---

# 16. Questions finales à poser au client

Avant de terminer la première réunion, nous devons obtenir des réponses à ces questions :

1. **Quel est exactement le minimum attendu pour la première version ?**
2. **Quelles fonctionnalités seront évaluées en priorité ?**
3. **Quelles sont les règles qui ne doivent absolument pas être interprétées ?**
4. **Existe-t-il une documentation officielle de la compétition ?**
5. **Existe-t-il un exemple de partie complète ?**
6. **Existe-t-il un exemple de requête/réponse API ?**
7. **Comment sera évaluée notre solution ?**
8. **Quels sont les critères de victoire ?**
9. **Quelles sont les contraintes de performance ?**
10. **Quelle est la date limite ?**
11. **Quels sont les jalons intermédiaires ?**
12. **Quelle fonctionnalité devons-nous développer en premier ?**
13. **Qui valide nos choix fonctionnels ?**
14. **Comment devons-nous gérer les changements de besoin ?**

---

# 17. Proposition de première stratégie

Nous proposons de commencer par le **cœur du jeu et l'arbitre**, avant de développer les fonctionnalités secondaires.

Ordre proposé :

### Étape 1 — Comprendre et formaliser les règles

- règles générales ;
- joueurs ;
- royaume ;
- cartes ;
- trésors ;
- points de victoire ;
- tours ;
- trois phases ;
- conditions de fin.

### Étape 2 — Implémenter l'arbitre

L'arbitre doit permettre de faire fonctionner une partie complète avec les règles principales.

### Étape 3 — Première version jouable

Créer une version minimale permettant :

- de commencer une partie ;
- de jouer un tour ;
- d'utiliser les cartes principales ;
- d'acheter des cartes ;
- de terminer un tour ;
- de calculer le score.

### Étape 4 — API

Connecter le jeu aux mécanismes imposés par la compétition.

### Étape 5 — Enrichissement

Ajouter progressivement :

- les différents types de cartes ;
- les interactions entre royaumes ;
- les règles avancées ;
- les améliorations d'interface ;
- les optimisations.

---

# 18. Principe stratégique

Le projet se déroule dans un contexte compétitif.

Notre stratégie doit donc éviter de chercher à réaliser immédiatement une version complète.

L'objectif est d'abord de disposer rapidement d'une **version minimale mais fonctionnelle**, permettant de :

- tester les règles ;
- détecter les erreurs ;
- mesurer les performances ;
- faire des démonstrations ;
- obtenir des retours ;
- commencer à être compétitif le plus tôt possible.

Principe retenu :

> **Entrer tôt sur le marché avec une version fonctionnelle, puis améliorer progressivement le produit.**

La priorité est donc de maîtriser simultanément :

**Coût + Délai + Besoin client + Qualité.**

---

# 19. Résultat attendu de la première réunion

À la fin de la réunion, l'équipe doit repartir avec :

- une compréhension commune du projet ;
- les règles principales validées ;
- la liste des fonctionnalités obligatoires ;
- la liste des fonctionnalités secondaires ;
- les contraintes techniques ;
- les contraintes de l'API ;
- les contraintes du serveur ;
- les critères d'évaluation ;
- les délais ;
- les premières tâches à réaliser ;
- les points encore à clarifier.

Le premier objectif n'est donc pas de coder immédiatement.

**Le premier objectif est de savoir exactement ce que nous devons construire.**