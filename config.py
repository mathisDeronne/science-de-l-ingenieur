NOM_BOT_OFFICIEL = "Le 4ème Empire"
NOM_BOT_DEV = "Le 4ème Empire le Remake"

DOMAINE_BOT_OFFICIEL = "le-4eme-empire.alwaysdata.net"
DOMAINE_BOT_DEV = "le-4eme-empire-le-remake.alwaysdata.net"


def obtenir_nom_joueur(host: str) -> str:
    host = host.split(":")[0].lower()

    if host == DOMAINE_BOT_OFFICIEL:
        return NOM_BOT_OFFICIEL

    if host == DOMAINE_BOT_DEV:
        return NOM_BOT_DEV

    return NOM_BOT_DEV


EFFETS_ACTIONS = {
    "festival":       {"actions": 2, "achats": 1, "pieces": 2},
    "smithy":         {"actions": 0, "achats": 0, "pieces": 0},
    "laboratory":     {"actions": 1, "achats": 0, "pieces": 0},
    "village":        {"actions": 2, "achats": 0, "pieces": 0},
    "woodcutter":     {"actions": 0, "achats": 1, "pieces": 2},
    "market":         {"actions": 1, "achats": 1, "pieces": 1},
    "councilroom":    {"actions": 0, "achats": 1, "pieces": 0},
    "witch":          {"actions": 0, "achats": 0, "pieces": 0},
    "farmingvillage": {"actions": 2, "achats": 0, "pieces": 0},
    "distantshore":   {"actions": 1, "achats": 0, "pieces": 0},
    "hireling":       {"actions": 0, "achats": 0, "pieces": 0},

    # Nouvelles cartes
    "chancellor":     {"actions": 0, "achats": 0, "pieces": 2},
    "militia":        {"actions": 0, "achats": 0, "pieces": 2},
    "bandit":         {"actions": 0, "achats": 0, "pieces": 0},
}


GAINS_ACTIONS = {
    "bandit": {
        "gold": 1,
    },

    "distantshore": {
        "estate": 1,
    },
}


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
    "bandit",
    "militia",
    "smithy",
    "woodcutter",
    "chancellor",
]


MAX_CARTES_ACTION = {
    "laboratory": 4,
    "smithy": 2,
    "festival": 2,
    "market": 2,
    "village": 3,
    "woodcutter": 1,
    "witch": 2,
    "farmingvillage": 3,
    "councilroom": 2,
    "distantshore": 2,
    "hireling": 2,
    "chancellor": 1,
    "militia": 2,
    "bandit": 2,
}


MAX_TOTAL_ACTIONS = 6
MAX_TOTAL_ACTIONS_BASE = 4
NB_ACTIONS_AVANT_ECONOMIE = 2


POIDS_BASE_ACHAT = {
    "province": 1000,

    "gold": 70,
    "silver": 46,

    "bandit": 45,
    "militia": 43,
    "witch": 42,

    "laboratory": 38,
    "smithy": 34,
    "market": 33,
    "festival": 32,
    "distantshore": 31,
    "village": 30,
    "farmingvillage": 30,
    "councilroom": 28,
    "hireling": 27,

    "woodcutter": 18,
    "chancellor": 18,

    "duchy": 10,
    "gardens": 8,
    "estate": 0,
}


POIDS_MINIMUM_ACHAT = 1


CARTES_TERMINALES = {
    "smithy",
    "witch",
    "councilroom",
    "woodcutter",
    "hireling",
    "militia",
    "bandit",
    "chancellor",
}


CARTES_SUPPORT_ACTIONS = {
    "village",
    "farmingvillage",
    "festival",
}


MALUS_PAR_COPIE_ACTION = {
    "laboratory": 5,
    "smithy": 12,
    "festival": 8,
    "market": 7,
    "village": 8,
    "woodcutter": 15,
    "witch": 12,
    "farmingvillage": 8,
    "councilroom": 12,
    "distantshore": 9,
    "hireling": 14,
    "militia": 12,
    "bandit": 12,
    "chancellor": 18,
}


SYNERGIES_ACHAT = [
    {"cartes": ("village", "smithy"),              "bonus": {"village": 18, "smithy": 18}},
    {"cartes": ("village", "witch"),               "bonus": {"village": 14, "witch": 16}},
    {"cartes": ("village", "councilroom"),         "bonus": {"village": 15, "councilroom": 18}},
    {"cartes": ("village", "militia"),             "bonus": {"village": 12, "militia": 14}},
    {"cartes": ("village", "bandit"),              "bonus": {"village": 12, "bandit": 15}},
    {"cartes": ("village", "hireling"),            "bonus": {"village": 8, "hireling": 8}},

    {"cartes": ("festival", "smithy"),             "bonus": {"festival": 15, "smithy": 16}},
    {"cartes": ("festival", "witch"),              "bonus": {"festival": 12, "witch": 15}},
    {"cartes": ("festival", "councilroom"),        "bonus": {"festival": 18, "councilroom": 20}},
    {"cartes": ("festival", "militia"),            "bonus": {"festival": 10, "militia": 12}},
    {"cartes": ("festival", "bandit"),             "bonus": {"festival": 10, "bandit": 13}},
    {"cartes": ("festival", "hireling"),           "bonus": {"festival": 8, "hireling": 8}},

    {"cartes": ("farmingvillage", "smithy"),       "bonus": {"farmingvillage": 14, "smithy": 15}},
    {"cartes": ("farmingvillage", "witch"),        "bonus": {"farmingvillage": 15, "witch": 16}},
    {"cartes": ("farmingvillage", "councilroom"),  "bonus": {"farmingvillage": 16, "councilroom": 18}},
    {"cartes": ("farmingvillage", "militia"),      "bonus": {"farmingvillage": 13, "militia": 14}},
    {"cartes": ("farmingvillage", "bandit"),       "bonus": {"farmingvillage": 13, "bandit": 15}},
    {"cartes": ("farmingvillage", "distantshore"), "bonus": {"farmingvillage": 12, "distantshore": 10}},
    {"cartes": ("farmingvillage", "hireling"),     "bonus": {"farmingvillage": 8, "hireling": 8}},

    {"cartes": ("laboratory", "witch"),            "bonus": {"laboratory": 13, "witch": 17}},
    {"cartes": ("laboratory", "market"),           "bonus": {"laboratory": 10, "market": 10}},

    {"cartes": ("distantshore", "gardens"),        "bonus": {"distantshore": 4, "gardens": 10}},
    {"cartes": ("bandit", "gardens"),              "bonus": {"bandit": 3, "gardens": 7}},
]


PRIORITE_DEPARTAGE = [
    "province",
    "duchy",
    "gardens",
    "gold",

    "witch",
    "bandit",
    "militia",
    "laboratory",

    "silver",

    "market",
    "festival",
    "village",
    "farmingvillage",
    "smithy",
    "councilroom",
    "distantshore",
    "hireling",

    "woodcutter",
    "chancellor",

    "estate",
]