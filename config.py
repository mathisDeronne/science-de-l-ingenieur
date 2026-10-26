<<<<<<< HEAD
NOM_JOUEUR = "Le 4ème Empire"
=======
NOM_BOT_OFFICIEL = "Le 4ème Empire"
NOM_BOT_DEV = "Le 4ème Empire le Remake"

DOMAINE_BOT_OFFICIEL = "le-4eme-empire.alwaysdata.net"
DOMAINE_BOT_DEV = "le-4eme-empire-le-remake.alwaysdata.net"
>>>>>>> dev


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
    "smithy",
    "woodcutter",
]

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
NB_ACTIONS_AVANT_ECONOMIE = 2

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
    "silver",
    "estate",
]

PRIORITE_ACHAT_FIN_URGENTE = [
    "province",
    "duchy",
    "estate",
    "gold",
    "silver",
]