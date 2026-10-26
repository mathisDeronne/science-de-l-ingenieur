NOM_JOUEUR = "Le 4ème Empire"


#####################################################
# Effets locaux des cartes Action
#####################################################

# La pioche, les Curse, les gains d'Estate, Hireling...
# sont gérés directement par l'arbitre.
# On suit seulement Actions, Achats et pièces bonus.

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
    "councilroom": {
        "actions": 0,
        "achats": 1,
        "pieces": 0,
    },
    "witch": {
        "actions": 0,
        "achats": 0,
        "pieces": 0,
    },
    "farmingvillage": {
        "actions": 2,
        "achats": 0,
        "pieces": 0,
    },
    "distantshore": {
        "actions": 1,
        "achats": 0,
        "pieces": 0,
    },
    "hireling": {
        "actions": 0,
        "achats": 0,
        "pieces": 0,
    },
}


#####################################################
# Ordre de jeu des Actions
#####################################################

PRIORITE_ACTION = [
    "laboratory",
    "farmingvillage",
    "village",
    "market",
    "distantshore",
    "festival",

    "hireling",
    "witch",
    "councilroom",
    "smithy",
    "woodcutter",
]


#####################################################
# Limites des cartes Action
#####################################################

MAX_CARTES_ACTION = {
    "laboratory": 2,
    "smithy": 1,
    "festival": 1,
    "market": 1,
    "village": 1,
    "woodcutter": 0,

    "witch": 1,
    "farmingvillage": 1,
    "councilroom": 1,
    "distantshore": 1,
    "hireling": 1,
}

MAX_TOTAL_ACTIONS = 5

# Après 2 Actions achetées, on privilégie l'économie.
NB_ACTIONS_AVANT_ECONOMIE = 2


#####################################################
# Priorités d'achat
#####################################################

PRIORITE_ACHAT_DEBUT = [
    "province",
    "gold",

    "witch",
    "laboratory",
    "smithy",
    "farmingvillage",

    "silver",

    "hireling",
    "distantshore",
    "festival",
    "market",
    "village",
    "councilroom",
]


PRIORITE_ACHAT_MILIEU = [
    "province",
    "gold",

    "witch",
    "silver",

    "laboratory",
    "distantshore",
    "farmingvillage",
    "smithy",
    "festival",
    "market",
    "village",
    "councilroom",
    "hireling",
]


PRIORITE_ACHAT_ECONOMIE = [
    "province",
    "gold",
    "silver",

    "witch",
    "laboratory",
    "distantshore",
    "smithy",
    "farmingvillage",
    "festival",
    "market",
    "village",
    "councilroom",
    "hireling",
]


PRIORITE_ACHAT_FIN = [
    "province",
    "duchy",
    "gold",
    "estate",
    "silver",
]


PRIORITE_ACHAT_FIN_URGENTE = [
    "province",
    "duchy",
    "estate",
    "gold",
    "silver",
]


#####################################################
# Seuils temporels
#####################################################

TOUR_FIN = 15
TOUR_FIN_URGENTE = 20