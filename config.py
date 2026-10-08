NOM_JOUEUR = "Le 4ème Empire"


#####################################################
# Effets des cartes Action
#####################################################

EFFETS_ACTIONS = {
    "festival": {
        "actions": 2,
        "achats": 1,
        "pieces": 2,
    },
    "smithy": {
        "actions": 0,
        "achats": 0,
        "pieces": 0,
    },
    "laboratory": {
        "actions": 1,
        "achats": 0,
        "pieces": 0,
    },
    "village": {
        "actions": 2,
        "achats": 0,
        "pieces": 0,
    },
    "woodcutter": {
        "actions": 0,
        "achats": 1,
        "pieces": 2,
    },
    "market": {
        "actions": 1,
        "achats": 1,
        "pieces": 1,
    },
}


#####################################################
# Priorité de jeu des cartes Action
#####################################################

PRIORITE_ACTION = [
    "laboratory",
    "village",
    "market",
    "festival",
    "smithy",
    "woodcutter",
]


#####################################################
# Limites d'achat des cartes Action
#####################################################

MAX_CARTES_ACTION = {
    "laboratory": 3,
    "smithy": 2,
    "festival": 1,
    "market": 1,
    "village": 1,
    "woodcutter": 0,
}

MAX_TOTAL_ACTIONS = 5


#####################################################
# Priorités d'achat
#####################################################

# Début de partie : construire un petit moteur
PRIORITE_ACHAT_DEBUT = [
    "province",
    "gold",
    "laboratory",
    "smithy",
    "festival",
    "market",
    "silver",
    "village",
]

# Milieu : privilégier l'économie
PRIORITE_ACHAT_MILIEU = [
    "province",
    "gold",
    "laboratory",
    "silver",
    "smithy",
    "festival",
    "market",
    "village",
]

# Fin : prendre des points
PRIORITE_ACHAT_FIN = [
    "province",
    "duchy",
    "gold",
    "silver",
    "estate",
]

# Toute fin : même les petits points deviennent importants
PRIORITE_ACHAT_FIN_URGENTE = [
    "province",
    "duchy",
    "estate",
    "gold",
    "silver",
]


#####################################################
# Seuils de changement de stratégie
#####################################################

TOUR_FIN = 15
TOUR_FIN_URGENTE = 20

PROVINCES_FIN = 4
PROVINCES_FIN_URGENTE = 2