NOM_JOUEUR = "Le 4ème Empire"


#####################################################
# Effets locaux des cartes Action
#####################################################

# Les effets de pioche, Curse, gain d'Estate, Hireling...
# sont appliqués par l'arbitre.
#
# Nous suivons seulement ce que l'arbitre ne nous renvoie pas :
# Actions, Achats et pièces bonus.

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

    # Nouvelles cartes
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
# Ordre de jeu des cartes Action
#####################################################

# On joue d'abord les cartes qui conservent ou donnent
# des Actions, puis les cartes terminales.

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
# Limitation du moteur
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

# Evite de remplir le deck de cartes Action.
MAX_TOTAL_ACTIONS = 5

# Après ce nombre de cartes Action,
# on privilégie surtout Gold / Silver.
NB_ACTIONS_AVANT_ECONOMIE = 2


#####################################################
# Priorités d'achat
#####################################################

# Début : petit moteur + économie.
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

# Milieu de partie.
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

# Une fois le moteur construit.
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

# Fin de partie.
PRIORITE_ACHAT_FIN = [
    "province",
    "duchy",
    "gold",
    "estate",
    "silver",
]

# Toute fin de partie.
PRIORITE_ACHAT_FIN_URGENTE = [
    "province",
    "duchy",
    "estate",
    "gold",
    "silver",
]


#####################################################
# Seuils
#####################################################

TOUR_FIN = 15
TOUR_FIN_URGENTE = 20

# Avec 2 piles déjà vides, la partie peut se terminer
# rapidement si une troisième pile est épuisée.
PILES_VIDES_URGENCE = 2