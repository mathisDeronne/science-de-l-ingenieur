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
    # Gagne un Silver sur le dessus du deck.
    "bureaucrat":     {"actions": 0, "achats": 0, "pieces": 0},
}


GAINS_ACTIONS = {
    "bandit": {
        "gold": 1,
    },

    "distantshore": {
        "estate": 1,
    },

    "bureaucrat": {
        "silver": 1,
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
    "bureaucrat",
    "woodcutter",
    "chancellor",
]


MAX_CARTES_ACTION = {
    "laboratory": 3,
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
    "bureaucrat": 1,
}


MAX_TOTAL_ACTIONS = 6
MAX_TOTAL_ACTIONS_BASE = 4
NB_ACTIONS_AVANT_ECONOMIE = 2


POIDS_BASE_ACHAT = {
    "province": 1000,

    "gold": 70,
    "silver": 46,

    "bandit": 43,
    "militia": 43,
    "witch": 45,

    # Valeur réellement utilisée (avant : 60 ici,
    # mais écrasée à 50 dans weights.py).
    "laboratory": 50,
    "smithy": 40,
    "market": 33,
    "festival": 32,
    "distantshore": 31,
    "village": 30,
    "farmingvillage": 30,
    "councilroom": 28,
    "hireling": 27,

    "woodcutter": 18,
    "chancellor": 18,

    # Aucune donnée : jamais acheté jusqu'ici.
    # Poids prudent, sous le Silver.
    "bureaucrat": 36,

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
    "militia",
    "bandit",
    "chancellor",
    "bureaucrat",
}


# Cartes +2 Actions : chacune permet
# de jouer une terminale de plus.
CARTES_SUPPORT_ACTIONS = {
    nom
    for nom, effet
    in EFFETS_ACTIONS.items()
    if effet["actions"] >= 2
}


CARTES_PIOCHE = {
    "laboratory",
    "smithy",
    "councilroom",
    "witch",
    "distantshore",
}


CARTES_PIOCHE_FORTE = {
    "laboratory",
    "smithy",
    "councilroom",
}


MALUS_PAR_COPIE_ACTION = {
    "laboratory": 9,
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
    # Une première Militia est intéressante, la
    # deuxième beaucoup moins (avant : 20 ici, mais
    # écrasé à 22 dans weights.py).
    "militia": 22,
    "bandit": 12,
    "chancellor": 18,
    "bureaucrat": 15,
}


SYNERGIES_ACHAT = [
    # =====================================================
    # VILLAGE
    # =====================================================

    {"cartes": ("village", "smithy"),
     "bonus": {"village": 18, "smithy": 18}},

    {"cartes": ("village", "witch"),
     "bonus": {"village": 14, "witch": 16}},

    {"cartes": ("village", "councilroom"),
     "bonus": {"village": 15, "councilroom": 18}},

    {"cartes": ("village", "militia"),
     "bonus": {"village": 12, "militia": 14}},

    {"cartes": ("village", "bandit"),
     "bonus": {"village": 12, "bandit": 15}},

    {"cartes": ("village", "hireling"),
     "bonus": {"village": 8, "hireling": 8}},

    {"cartes": ("village", "laboratory"),
     "bonus": {"village": 7, "laboratory": 9}},

    {"cartes": ("village", "distantshore"),
     "bonus": {"village": 8, "distantshore": 9}},

    {"cartes": ("village", "market"),
     "bonus": {"village": 5, "market": 6}},


    # =====================================================
    # FESTIVAL
    # =====================================================

    {"cartes": ("festival", "smithy"),
     "bonus": {"festival": 15, "smithy": 16}},

    {"cartes": ("festival", "witch"),
     "bonus": {"festival": 12, "witch": 15}},

    {"cartes": ("festival", "councilroom"),
     "bonus": {"festival": 18, "councilroom": 20}},

    {"cartes": ("festival", "militia"),
     "bonus": {"festival": 10, "militia": 12}},

    {"cartes": ("festival", "bandit"),
     "bonus": {"festival": 10, "bandit": 13}},

    {"cartes": ("festival", "hireling"),
     "bonus": {"festival": 8, "hireling": 8}},

    {"cartes": ("festival", "laboratory"),
     "bonus": {"festival": 9, "laboratory": 10}},

    {"cartes": ("festival", "market"),
     "bonus": {"festival": 6, "market": 7}},

    {"cartes": ("festival", "distantshore"),
     "bonus": {"festival": 8, "distantshore": 9}},


    # =====================================================
    # FARMING VILLAGE
    # =====================================================

    {"cartes": ("farmingvillage", "smithy"),
     "bonus": {"farmingvillage": 14, "smithy": 15}},

    {"cartes": ("farmingvillage", "witch"),
     "bonus": {"farmingvillage": 15, "witch": 16}},

    {"cartes": ("farmingvillage", "councilroom"),
     "bonus": {"farmingvillage": 16, "councilroom": 18}},

    {"cartes": ("farmingvillage", "militia"),
     "bonus": {"farmingvillage": 13, "militia": 14}},

    {"cartes": ("farmingvillage", "bandit"),
     "bonus": {"farmingvillage": 13, "bandit": 15}},

    {"cartes": ("farmingvillage", "distantshore"),
     "bonus": {"farmingvillage": 12, "distantshore": 10}},

    {"cartes": ("farmingvillage", "hireling"),
     "bonus": {"farmingvillage": 8, "hireling": 8}},

    {"cartes": ("farmingvillage", "laboratory"),
     "bonus": {"farmingvillage": 10, "laboratory": 11}},

    {"cartes": ("farmingvillage", "market"),
     "bonus": {"farmingvillage": 7, "market": 7}},


    # =====================================================
    # LABORATORY
    # =====================================================

    {"cartes": ("laboratory", "witch"),
     "bonus": {"laboratory": 13, "witch": 17}},

    {"cartes": ("laboratory", "market"),
     "bonus": {"laboratory": 10, "market": 10}},

    {"cartes": ("laboratory", "smithy"),
     "bonus": {"laboratory": 11, "smithy": 9}},

    {"cartes": ("laboratory", "militia"),
     "bonus": {"laboratory": 11, "militia": 8}},

    {"cartes": ("laboratory", "bandit"),
     "bonus": {"laboratory": 10, "bandit": 8}},

    {"cartes": ("laboratory", "councilroom"),
     "bonus": {"laboratory": 9, "councilroom": 10}},

    {"cartes": ("laboratory", "hireling"),
     "bonus": {"laboratory": 8, "hireling": 8}},

    {"cartes": ("laboratory", "distantshore"),
     "bonus": {"laboratory": 9, "distantshore": 9}},


    # =====================================================
    # MARKET
    # =====================================================

    {"cartes": ("market", "smithy"),
     "bonus": {"market": 10, "smithy": 10}},

    {"cartes": ("market", "witch"),
     "bonus": {"market": 9, "witch": 10}},

    {"cartes": ("market", "councilroom"),
     "bonus": {"market": 11, "councilroom": 12}},

    {"cartes": ("market", "militia"),
     "bonus": {"market": 8, "militia": 7}},

    {"cartes": ("market", "bandit"),
     "bonus": {"market": 8, "bandit": 7}},

    {"cartes": ("market", "hireling"),
     "bonus": {"market": 7, "hireling": 7}},

    {"cartes": ("market", "distantshore"),
     "bonus": {"market": 8, "distantshore": 8}},


    # =====================================================
    # SMITHY
    # =====================================================

    {"cartes": ("smithy", "hireling"),
     "bonus": {"smithy": 7, "hireling": 8}},

    {"cartes": ("smithy", "distantshore"),
     "bonus": {"smithy": 7, "distantshore": 8}},


    # =====================================================
    # COUNCIL ROOM
    # =====================================================

    {"cartes": ("councilroom", "hireling"),
     "bonus": {"councilroom": 8, "hireling": 7}},

    {"cartes": ("councilroom", "distantshore"),
     "bonus": {"councilroom": 8, "distantshore": 8}},


    # =====================================================
    # GARDENS
    # =====================================================

    {"cartes": ("distantshore", "gardens"),
     "bonus": {"distantshore": 4, "gardens": 10}},

    {"cartes": ("bandit", "gardens"),
     "bonus": {"bandit": 3, "gardens": 7}},
]


PRIORITE_DEPARTAGE = [
    "province",
    "duchy",
    "gardens",
    "gold",

    "laboratory",
    "witch",
    "bandit",
    "militia",

    "silver",

    "market",
    "festival",
    "village",
    "farmingvillage",
    "smithy",
    "councilroom",
    "distantshore",
    "hireling",

    "bureaucrat",
    "woodcutter",
    "chancellor",

    "estate",
]

# =========================================================
# PLAN DE PARTIE
# =========================================================
#
# Le plan est choisi au premier achat de la partie, d'après
# les cartes du royaume, puis conservé.
#
# Il ne peut changer qu'UNE seule fois, et seulement sur un
# déclencheur fort (voir plans.py) :
# - la carte clé du plan n'est plus disponible alors qu'on
#   ne l'a jamais obtenue ;
# - plan Witch : il n'y a plus de Curses à distribuer.
#
# Notes de départ calibrées sur les 384 parties V/D des logs
# du 27/10 (taux de victoire selon la stratégie suivie au
# tour 6, et Witch achetée avant le tour 6 : 69 % contre
# 53 %). Les plans VILLAGE_SMITHY (38 %) et les moteurs
# sans données suffisantes ne sont plus proposés.
# =========================================================

# "bonus_achat" : bonus ajouté au poids d'achat de ces
# cartes tant que le plan est suivi.
PLANS = {
    "WITCH_MONEY": {
        "requis": ("witch",),
        "carte_cle": "witch",
        "note": 100,
        # 2 et 3 joueurs : ~80 % avec Witch tôt.
        # 4 joueurs : seulement 56 %.
        "ajustement_joueurs": {4: -10},
        "bonus_achat": {"witch": 16, "laboratory": 8, "gold": 8},
    },
    "SMITHY_MONEY": {
        "requis": ("smithy",),
        "carte_cle": "smithy",
        "note": 85,
        "ajustement_joueurs": {},
        "bonus_achat": {"smithy": 15, "gold": 8, "silver": 2},
    },
    "MILITIA_MONEY": {
        "requis": ("militia",),
        "carte_cle": "militia",
        "note": 80,
        "ajustement_joueurs": {},
        "bonus_achat": {"militia": 8, "gold": 7, "silver": 1},
    },
    "BANDIT_MONEY": {
        "requis": ("bandit",),
        "carte_cle": "bandit",
        "note": 70,
        "ajustement_joueurs": {},
        "bonus_achat": {"bandit": 12, "gold": 5, "silver": 1},
    },
    # Toujours possible : plan de secours.
    "BIG_MONEY": {
        "requis": (),
        "carte_cle": None,
        "note": 60,
        "ajustement_joueurs": {},
        "bonus_achat": {"gold": 10, "silver": 3},
    },
}

PLAN_PAR_DEFAUT = "BIG_MONEY"

# Après ce tour, plus aucun changement de plan :
# la logique de fin de partie prend le relais.
TOUR_MAX_CHANGEMENT_PLAN = 18

# Bonus d'achat pour la carte clé du plan tant qu'on n'en
# possède aucun exemplaire (Witch à 5 pièces doit passer
# devant Laboratory et Silver).
BONUS_CARTE_CLE = 30


# =========================================================
# HIRELING
# =========================================================
#
# Dans le moteur Dopynion, une Hireling jouée quitte le deck
# et donne +1 carte à CHAQUE tour jusqu'à la fin de partie.
# Les parties durent ~25 tours : la première Hireling achetée
# tôt rapporte bien plus qu'une Gold.
#
# Logs du 27/10 : quand Hireling est sur le plateau, on gagne
# 56 % des parties contre 74 % sans (le bot n'en achetait
# jamais, les adversaires ~1 chacun).
# =========================================================

BONUS_PREMIER_HIRELING = 65
TOUR_MAX_PREMIER_HIRELING = 14


# =========================================================
# FIN DE PARTIE
# =========================================================
#
# Achat qui termine la partie (dernière Province ou 3e pile
# vide) :
# - si on gagne après l'achat : gros bonus ;
# - si on perd après l'achat : achat interdit.
#
# Avant-dernière Province : si un adversaire peut ensuite
# gagner en prenant la dernière, on préfère un Duchy.
# =========================================================

BONUS_FIN_GAGNANTE = 5000
MALUS_FIN_PERDANTE = 100000
MALUS_AVANT_DERNIERE_PROVINCE = 1300


# =========================================================
# CHANCELLOR
# =========================================================
#
# Défausser son deck accélère le prochain mélange, qui
# contiendra les cartes achetées récemment. Intéressant tant
# qu'on achète des cartes utiles, plus en fin de partie.
# =========================================================

TOUR_MAX_CHANCELLOR = 14


# =========================================================
# BUREAUCRAT À 4 JOUEURS
# Son attaque touche 3 adversaires : en simulation
# (900 parties), poids 55 au lieu de 36 donne +4,7
# points de victoire à 4 joueurs, et rien à 2-3 joueurs.
# =========================================================

BONUS_BUREAUCRAT_4_JOUEURS = 19
