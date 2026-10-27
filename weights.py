from __future__ import annotations

from typing import Any

from dopynion.data_model import Game

from config import (
    CARTES_SUPPORT_ACTIONS,
    CARTES_TERMINALES,
    MALUS_PAR_COPIE_ACTION,
    MAX_CARTES_ACTION,
    MAX_TOTAL_ACTIONS,
    MAX_TOTAL_ACTIONS_BASE,
    NB_ACTIONS_AVANT_ECONOMIE,
    POIDS_BASE_ACHAT,
    SYNERGIES_ACHAT,
)

from game_utils import (
    curses_restantes,
    nombre_piles_vides,
    provinces_restantes,
    risque_fin_par_piles,
    trouver_mon_joueur,
)

from state import obtenir_etat


# =========================================================
# AJUSTEMENTS LOCAUX
# =========================================================
#
# On les place ici volontairement afin que le test de cette
# version ne dépende pas d'une modification oubliée dans
# config.py.
#
# Si les résultats sont bons, on pourra ensuite déplacer
# définitivement ces valeurs dans config.py.
# =========================================================

POIDS_BASE_EFFECTIFS = dict(
    POIDS_BASE_ACHAT
)

# Les dernières parties montrent que le bot manque
# fortement de cartes de pioche.
POIDS_BASE_EFFECTIFS.update(
    {
        "laboratory": 50,
        "smithy": 40,
    }
)


MALUS_PAR_COPIE_EFFECTIFS = dict(
    MALUS_PAR_COPIE_ACTION
)

# Une première Militia est intéressante.
# La deuxième doit être beaucoup moins automatique.
MALUS_PAR_COPIE_EFFECTIFS[
    "militia"
] = 22


# =========================================================
# GROUPES DE CARTES
# =========================================================

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


CARTES_MOTEUR = {
    "laboratory",
    "smithy",
    "councilroom",
    "market",
    "festival",
    "village",
    "farmingvillage",
    "witch",
    "distantshore",
}


CARTES_VICTOIRE = {
    "province",
    "duchy",
    "estate",
    "gardens",
}


CARTES_TRESOR = {
    "copper",
    "silver",
    "gold",
}


# =========================================================
# OUTILS GÉNÉRAUX
# =========================================================

def normaliser_nom(
    carte: Any,
) -> str:
    if hasattr(
        carte,
        "value",
    ):
        return str(
            carte.value
        ).lower()

    return str(
        carte
    ).lower()


def cartes_stock_disponibles(
    game: Game,
) -> set[str]:
    disponibles = set()

    for carte, quantite in (
        game.stock.quantities.items()
    ):
        if quantite <= 0:
            continue

        disponibles.add(
            normaliser_nom(
                carte
            )
        )

    return disponibles


def quantite_stock(
    game: Game,
    nom: str,
) -> int:
    nom = nom.lower()

    for carte, quantite in (
        game.stock.quantities.items()
    ):
        if (
            normaliser_nom(
                carte
            )
            == nom
        ):
            return quantite

    return 0


def quantite_achetee(
    game_id: str,
    nom: str,
) -> int:
    etat = obtenir_etat(
        game_id
    )

    return int(
        etat.get(
            "cartes_achetees",
            {},
        ).get(
            nom.lower(),
            0,
        )
    )


def quantite_gain_estime(
    game_id: str,
    nom: str,
) -> int:
    etat = obtenir_etat(
        game_id
    )

    return int(
        etat.get(
            "gains_estimes",
            {},
        ).get(
            nom.lower(),
            0,
        )
    )


def quantite_economique(
    game_id: str,
    nom: str,
) -> int:
    return (
        quantite_achetee(
            game_id,
            nom,
        )
        + quantite_gain_estime(
            game_id,
            nom,
        )
    )


def estimer_taille_deck(
    game_id: str,
) -> int:
    etat = obtenir_etat(
        game_id
    )

    achats = sum(
        int(quantite)
        for quantite
        in etat.get(
            "cartes_achetees",
            {},
        ).values()
    )

    gains = sum(
        int(quantite)
        for quantite
        in etat.get(
            "gains_estimes",
            {},
        ).values()
    )

    # Deck Dominion classique :
    # 7 Copper + 3 Estate.
    return (
        10
        + achats
        + gains
    )


def nombre_total_actions(
    game_id: str,
) -> int:
    etat = obtenir_etat(
        game_id
    )

    total = 0

    for nom, quantite in (
        etat.get(
            "cartes_achetees",
            {},
        ).items()
    ):
        if nom.lower() in (
            MAX_CARTES_ACTION
        ):
            total += int(
                quantite
            )

    return total


def nombre_actions_terminales(
    game_id: str,
) -> int:
    return sum(
        quantite_achetee(
            game_id,
            nom,
        )
        for nom
        in CARTES_TERMINALES
    )


def nombre_supports_actions(
    game_id: str,
) -> int:
    return sum(
        quantite_achetee(
            game_id,
            nom,
        )
        for nom
        in CARTES_SUPPORT_ACTIONS
    )


def nombre_cartes_pioche(
    game_id: str,
) -> int:
    return sum(
        quantite_achetee(
            game_id,
            nom,
        )
        for nom
        in CARTES_PIOCHE
    )


def nombre_cartes_pioche_forte(
    game_id: str,
) -> int:
    return sum(
        quantite_achetee(
            game_id,
            nom,
        )
        for nom
        in CARTES_PIOCHE_FORTE
    )


def ecart_score(
    game: Game,
) -> int:
    moi = trouver_mon_joueur(
        game
    )

    if moi is None:
        return 0

    adversaires = [
        joueur.score
        for joueur
        in game.players
        if joueur is not moi
    ]

    if not adversaires:
        return 0

    return (
        moi.score
        - max(
            adversaires
        )
    )


# =========================================================
# STRATÉGIES
# =========================================================

def scores_strategies(
    game: Game,
    game_id: str,
) -> dict[str, int]:
    disponibles = (
        cartes_stock_disponibles(
            game
        )
    )

    nb_joueurs = len(
        game.players
    )

    taille_deck = (
        estimer_taille_deck(
            game_id
        )
    )

    silver = quantite_economique(
        game_id,
        "silver",
    )

    gold = quantite_economique(
        game_id,
        "gold",
    )

    smithy = quantite_achetee(
        game_id,
        "smithy",
    )

    witch = quantite_achetee(
        game_id,
        "witch",
    )

    militia = quantite_achetee(
        game_id,
        "militia",
    )

    bandit = quantite_achetee(
        game_id,
        "bandit",
    )

    village = quantite_achetee(
        game_id,
        "village",
    )

    laboratory = quantite_achetee(
        game_id,
        "laboratory",
    )

    festival = quantite_achetee(
        game_id,
        "festival",
    )

    councilroom = (
        quantite_achetee(
            game_id,
            "councilroom",
        )
    )

    farmingvillage = (
        quantite_achetee(
            game_id,
            "farmingvillage",
        )
    )

    distantshore = (
        quantite_achetee(
            game_id,
            "distantshore",
        )
    )

    gardens = quantite_achetee(
        game_id,
        "gardens",
    )

    scores = {
        "BIG_MONEY":
            20
            + min(
                16,
                gold * 2,
            )
            + min(
                8,
                silver,
            ),

        "SMITHY_MONEY":
            8
            + smithy * 16
            + gold * 2,

        "WITCH_MONEY":
            8
            + witch * 18
            + gold * 2
            + max(
                0,
                nb_joueurs - 2,
            ) * 3,

        # Réduit par rapport à l'ancienne version.
        # Une Militia reste intéressante,
        # mais ne doit plus aspirer la stratégie.
        "MILITIA_MONEY":
            8
            + militia * 14
            + gold * 2
            + max(
                0,
                nb_joueurs - 2,
            ),

        "BANDIT_MONEY":
            10
            + bandit * 16
            + gold * 2
            + max(
                0,
                nb_joueurs - 2,
            ) * 2,

        "VILLAGE_SMITHY":
            village * 12
            + smithy * 15,

        "LAB_WITCH":
            laboratory * 14
            + witch * 15,

        "FESTIVAL_COUNCIL":
            festival * 12
            + councilroom * 16,

        "FARMING_ENGINE":
            farmingvillage * 12
            + laboratory * 8
            + councilroom * 7
            + festival * 5,

        # Gardens reste possible,
        # mais ne s'auto-renforce plus violemment.
        "GARDENS":
            gardens * 9
            + max(
                0,
                taille_deck - 20,
            )
            + distantshore * 5
            + bandit * 3,
    }

    # -----------------------------------------------------
    # Les stratégies impossibles dans ce royaume
    # ne doivent pas devenir dominantes.
    # -----------------------------------------------------

    if "smithy" not in disponibles:
        scores[
            "SMITHY_MONEY"
        ] = -100

    if "witch" not in disponibles:
        scores[
            "WITCH_MONEY"
        ] = -100

    if "militia" not in disponibles:
        scores[
            "MILITIA_MONEY"
        ] = -100

    if "bandit" not in disponibles:
        scores[
            "BANDIT_MONEY"
        ] = -100

    if not (
        "village" in disponibles
        and "smithy" in disponibles
    ):
        scores[
            "VILLAGE_SMITHY"
        ] = -100

    if not (
        "laboratory" in disponibles
        and "witch" in disponibles
    ):
        scores[
            "LAB_WITCH"
        ] = -100

    if not (
        "festival" in disponibles
        and "councilroom" in disponibles
    ):
        scores[
            "FESTIVAL_COUNCIL"
        ] = -100

    if "farmingvillage" not in (
        disponibles
    ):
        scores[
            "FARMING_ENGINE"
        ] = -100

    if "gardens" not in disponibles:
        scores[
            "GARDENS"
        ] = -100

    return scores


def strategie_dominante(
    game: Game,
    game_id: str,
) -> tuple[
    str,
    dict[str, int],
]:
    scores = scores_strategies(
        game,
        game_id,
    )

    strategie = max(
        scores,
        key=scores.get,
    )

    etat = obtenir_etat(
        game_id
    )

    etat[
        "strategie_actuelle"
    ] = strategie

    etat[
        "scores_strategies"
    ] = dict(
        scores
    )

    return (
        strategie,
        scores,
    )


# =========================================================
# BONUS DE STRATÉGIE
# =========================================================

def bonus_strategie(
    nom: str,
    strategie: str,
) -> int:
    bonus = {
        "BIG_MONEY": {
            "gold": 10,
            "silver": 3,
        },

        "SMITHY_MONEY": {
            "smithy": 15,
            "gold": 8,
            "silver": 2,
        },

        "WITCH_MONEY": {
            "witch": 16,
            "laboratory": 8,
            "gold": 8,
        },

        "MILITIA_MONEY": {
            # Réduit volontairement.
            "militia": 8,
            "gold": 7,
            "silver": 1,
        },

        "BANDIT_MONEY": {
            "bandit": 12,
            "gold": 5,
            "silver": 1,
        },

        "VILLAGE_SMITHY": {
            "village": 15,
            "smithy": 18,
        },

        "LAB_WITCH": {
            "laboratory": 16,
            "witch": 18,
        },

        "FESTIVAL_COUNCIL": {
            "festival": 16,
            "councilroom": 20,
        },

        "FARMING_ENGINE": {
            "farmingvillage": 15,
            "laboratory": 12,
            "councilroom": 10,
            "festival": 8,
        },

        "GARDENS": {
            # Anciennement beaucoup trop haut.
            "gardens": 6,
            "distantshore": 6,
            "bandit": 3,
        },
    }

    return bonus.get(
        strategie,
        {},
    ).get(
        nom,
        0,
    )


# =========================================================
# SYNERGIES
# =========================================================

def bonus_synergies(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    disponibles = (
        cartes_stock_disponibles(
            game
        )
    )

    bonus = 0

    for synergie in (
        SYNERGIES_ACHAT
    ):
        cartes = tuple(
            carte.lower()
            for carte
            in synergie.get(
                "cartes",
                (),
            )
        )

        if nom not in cartes:
            continue

        bonus_carte = (
            synergie.get(
                "bonus",
                {},
            ).get(
                nom,
                0,
            )
        )

        if bonus_carte == 0:
            continue

        autres = [
            carte
            for carte
            in cartes
            if carte != nom
        ]

        synergie_active = False
        synergie_possible = False

        for autre in autres:
            if (
                quantite_achetee(
                    game_id,
                    autre,
                )
                > 0
            ):
                synergie_active = True

            if autre in disponibles:
                synergie_possible = True

        if synergie_active:
            bonus += bonus_carte

        elif synergie_possible:
            # On reconnaît le potentiel du royaume,
            # mais beaucoup moins qu'une vraie
            # synergie déjà construite.
            bonus += round(
                bonus_carte * 0.30
            )

    return bonus


# =========================================================
# OBJECTIF D'ACTIONS
# =========================================================

def seuil_actions_cible(
    game: Game,
    game_id: str,
) -> int:
    strategie, _ = (
        strategie_dominante(
            game,
            game_id,
        )
    )

    cible = (
        NB_ACTIONS_AVANT_ECONOMIE
    )

    if strategie in {
        "VILLAGE_SMITHY",
        "LAB_WITCH",
        "FESTIVAL_COUNCIL",
        "FARMING_ENGINE",
    }:
        cible += 2

    elif strategie in {
        "WITCH_MONEY",
        "MILITIA_MONEY",
        "BANDIT_MONEY",
        "SMITHY_MONEY",
    }:
        cible += 1

    if (
        estimer_taille_deck(
            game_id
        )
        >= 22
    ):
        cible += 1

    return min(
        cible,
        MAX_TOTAL_ACTIONS,
    )


def max_total_actions_dynamique(
    game: Game,
    game_id: str,
) -> int:
    cible = seuil_actions_cible(
        game,
        game_id,
    )

    maximum = max(
        MAX_TOTAL_ACTIONS_BASE,
        cible,
    )

    if (
        nombre_cartes_pioche(
            game_id
        )
        >= 2
    ):
        maximum += 1

    return min(
        maximum,
        MAX_TOTAL_ACTIONS,
    )


# =========================================================
# ÉCONOMIE
# =========================================================

def bonus_economie(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    bonus = 0

    silver = quantite_economique(
        game_id,
        "silver",
    )

    gold = quantite_economique(
        game_id,
        "gold",
    )

    total_actions = (
        nombre_total_actions(
            game_id
        )
    )

    # -----------------------------------------------------
    # Silver
    # -----------------------------------------------------

    if nom == "silver":
        if silver == 0:
            bonus += 6

        elif silver == 1:
            bonus += 4

        elif silver >= 6:
            bonus -= 8

    # -----------------------------------------------------
    # Gold
    # -----------------------------------------------------

    elif nom == "gold":
        if silver >= 2:
            bonus += 8

        if gold == 0:
            bonus += 6

        elif gold == 1:
            bonus += 4

    # -----------------------------------------------------
    # Éviter de construire 5 actions avant d'avoir
    # une économie correcte.
    # -----------------------------------------------------

    if (
        nom in MAX_CARTES_ACTION
        and total_actions
        >= NB_ACTIONS_AVANT_ECONOMIE
        and (
            silver
            + gold
        ) < 3
    ):
        bonus -= 8

    return bonus


# =========================================================
# GARDENS
# =========================================================

def bonus_gardens(
    game: Game,
    game_id: str,
) -> int:
    taille = estimer_taille_deck(
        game_id
    )

    nb_gardens = quantite_achetee(
        game_id,
        "gardens",
    )

    points_avant = (
        taille // 10
    )

    points_apres = (
        (taille + 1) // 10
    )

    # VP du nouveau Gardens.
    vp_marginaux = points_apres

    # Si on passe 19 -> 20,
    # 29 -> 30, etc.,
    # les Gardens déjà présents
    # gagnent également un point.
    if (
        points_apres
        > points_avant
    ):
        vp_marginaux += (
            nb_gardens
        )

    bonus = (
        vp_marginaux * 10
    )

    # Gardens beaucoup trop tôt.
    if taille < 20:
        bonus -= 20

    if (
        taille < 24
        and nb_gardens == 0
    ):
        bonus -= 10

    # Les gros decks commencent
    # réellement à valoriser Gardens.
    if taille >= 30:
        bonus += 8

    # En quatre joueurs,
    # on exige un peu plus de deck
    # avant de lancer Gardens.
    if (
        len(
            game.players
        ) >= 4
        and taille < 26
    ):
        bonus -= 10

    # Cartes qui font naturellement
    # grossir le deck.
    bonus += min(
        8,
        quantite_achetee(
            game_id,
            "distantshore",
        ) * 4,
    )

    bonus += min(
        6,
        quantite_achetee(
            game_id,
            "bandit",
        ) * 3,
    )

    return bonus


# =========================================================
# PHASE DE PARTIE
# =========================================================

def bonus_phase_partie(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    provinces = provinces_restantes(
        game
    )

    nb_joueurs = len(
        game.players
    )

    bonus = 0

    fin_urgente = (
        provinces
        <= max(
            1,
            nb_joueurs - 1,
        )
        or risque_fin_par_piles(
            game
        )
        or nombre_piles_vides(
            game
        ) >= 2
    )

    # Compromis trouvé après le test :
    # +3 verdissait beaucoup trop tôt.
    fin_normale = (
        provinces
        <= nb_joueurs + 2
    )

    if fin_urgente:
        if nom == "province":
            bonus += 300

        elif nom == "duchy":
            bonus += 350

        elif nom == "estate":
            bonus += 220

        elif nom == "gardens":
            bonus += 180

        elif nom in {
            "gold",
            "silver",
        }:
            bonus -= 35

        elif nom in (
            MAX_CARTES_ACTION
        ):
            bonus -= 40

    elif fin_normale:
        if nom == "province":
            bonus += 300

        elif nom == "duchy":
            bonus += 80

        elif nom == "estate":
            bonus += 15

        elif nom == "gardens":
            bonus += 50

        elif nom == "gold":
            bonus -= 8

        elif nom == "silver":
            bonus -= 12

        elif nom in (
            MAX_CARTES_ACTION
        ):
            bonus -= 15

    return bonus


# =========================================================
# SITUATION AU SCORE
# =========================================================

def bonus_situation_score(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    ecart = ecart_score(
        game
    )

    provinces = provinces_restantes(
        game
    )

    nb_joueurs = len(
        game.players
    )

    bonus = 0

    # -----------------------------------------------------
    # Nous sommes nettement devant :
    # convertir l'avantage en VP.
    # -----------------------------------------------------

    if ecart >= 8:
        if nom == "province":
            bonus += 20

        elif nom == "duchy":
            bonus += 10

        elif nom == "estate":
            bonus += 5

    # -----------------------------------------------------
    # Nous sommes nettement derrière.
    #
    # IMPORTANT :
    # cette logique ne doit fonctionner
    # que s'il reste réellement assez
    # de Provinces.
    # -----------------------------------------------------

    if (
        ecart <= -8
        and provinces
        > nb_joueurs + 4
    ):
        if nom == "gold":
            bonus += 10

        elif nom == "laboratory":
            bonus += 8

        elif nom == "smithy":
            bonus += 6

        elif nom == "duchy":
            bonus -= 8

        elif nom == "estate":
            bonus -= 10

    return bonus


# =========================================================
# STRUCTURE DU DECK
# =========================================================

def bonus_structure(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    bonus = 0

    terminaux = (
        nombre_actions_terminales(
            game_id
        )
    )

    supports = (
        nombre_supports_actions(
            game_id
        )
    )

    nb_pioche = (
        nombre_cartes_pioche(
            game_id
        )
    )

    nb_pioche_forte = (
        nombre_cartes_pioche_forte(
            game_id
        )
    )

    militia = quantite_achetee(
        game_id,
        "militia",
    )

    # =====================================================
    # NOUVEAU :
    # LE DECK N'A AUCUNE PIOCHE
    # =====================================================

    if nb_pioche == 0:
        if nom == "laboratory":
            bonus += 15

        elif nom == "smithy":
            bonus += 10

        elif nom == "councilroom":
            bonus += 10

        elif nom == "witch":
            bonus += 8

        elif nom == "distantshore":
            bonus += 8

        # On possède déjà notre attaque :
        # la deuxième Militia ne doit pas
        # remplacer notre première vraie
        # carte de pioche.
        if (
            nom == "militia"
            and militia >= 1
        ):
            bonus -= 12

    # =====================================================
    # Peu de pioche forte
    # =====================================================

    elif nb_pioche_forte == 0:
        if nom == "laboratory":
            bonus += 10

        elif nom == "smithy":
            bonus += 7

        elif nom == "councilroom":
            bonus += 7

    # =====================================================
    # Trop de terminaux
    # =====================================================

    if terminaux > supports:
        if nom in (
            CARTES_SUPPORT_ACTIONS
        ):
            bonus += min(
                18,
                (
                    terminaux
                    - supports
                ) * 6,
            )

        if (
            nom
            in CARTES_TERMINALES
        ):
            bonus -= min(
                28,
                (
                    terminaux
                    - supports
                ) * 8,
            )

    # =====================================================
    # Trop de supports sans payload
    # =====================================================

    if (
        supports
        > terminaux + 2
    ):
        if nom in (
            CARTES_SUPPORT_ACTIONS
        ):
            bonus -= 10

        if nom in {
            "laboratory",
            "smithy",
            "councilroom",
            "witch",
        }:
            bonus += 8

    return bonus


# =========================================================
# BONUS SELON LA MAIN
# =========================================================

def bonus_main(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    moi = trouver_mon_joueur(
        game
    )

    if (
        moi is None
        or moi.hand is None
    ):
        return 0

    quantites = getattr(
        moi.hand,
        "quantities",
        {},
    )

    cartes_main = {
        normaliser_nom(
            carte
        )
        for carte, quantite
        in quantites.items()
        if quantite > 0
    }

    bonus = 0

    # Si une carte terminale est
    # présente dans la main, les cartes
    # +Actions ont un petit intérêt
    # supplémentaire.
    if (
        cartes_main
        & CARTES_TERMINALES
    ):
        if nom in {
            "village",
            "farmingvillage",
            "festival",
        }:
            bonus += 5

    return bonus


# =========================================================
# BONUS SPÉCIFIQUES
# =========================================================

def bonus_carte_specifique(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    etat = obtenir_etat(
        game_id
    )

    tour = int(
        etat.get(
            "tour",
            0,
        )
    )

    bonus = 0

    # -----------------------------------------------------
    # Gardens
    # -----------------------------------------------------

    if nom == "gardens":
        bonus += bonus_gardens(
            game,
            game_id,
        )

    # -----------------------------------------------------
    # Militia
    # -----------------------------------------------------

    elif nom == "militia":
        if tour <= 8:
            bonus += 7

        elif tour >= 16:
            bonus -= 8

        # Anciennement *4.
        # Réduit après l'analyse des
        # défaites multijoueurs.
        bonus += max(
            0,
            len(
                game.players
            ) - 2,
        ) * 2

    # -----------------------------------------------------
    # Witch
    # -----------------------------------------------------

    elif nom == "witch":
        curses = curses_restantes(
            game
        )

        if curses > 0:
            bonus += min(
                14,
                curses // 3,
            )

        bonus += max(
            0,
            len(
                game.players
            ) - 2,
        ) * 3

        if curses <= 3:
            bonus -= 12

    # -----------------------------------------------------
    # Bandit
    # -----------------------------------------------------

    elif nom == "bandit":
        bonus += max(
            0,
            len(
                game.players
            ) - 2,
        ) * 3

        if quantite_stock(
            game,
            "gold",
        ) <= 5:
            bonus -= 12

    # -----------------------------------------------------
    # Laboratory
    # -----------------------------------------------------

    elif nom == "laboratory":
        # Très bon premier moteur.
        if (
            quantite_achetee(
                game_id,
                "laboratory",
            )
            == 0
        ):
            bonus += 5

    # -----------------------------------------------------
    # Smithy
    # -----------------------------------------------------

    elif nom == "smithy":
        # Smithy est forte,
        # mais terminale.
        if (
            nombre_supports_actions(
                game_id
            )
            >= 1
        ):
            bonus += 5

    # -----------------------------------------------------
    # Council Room
    # -----------------------------------------------------

    elif nom == "councilroom":
        if len(
            game.players
        ) >= 4:
            # Les adversaires piochent aussi.
            bonus -= 4

    # -----------------------------------------------------
    # Hireling
    # -----------------------------------------------------

    elif nom == "hireling":
        if tour <= 8:
            bonus += 7

        elif tour >= 16:
            bonus -= 12

    # -----------------------------------------------------
    # Distant Shore
    # -----------------------------------------------------

    elif nom == "distantshore":
        if quantite_stock(
            game,
            "estate",
        ) > 0:
            bonus += 5

        if tour >= 16:
            bonus -= 8

    # -----------------------------------------------------
    # Chancellor
    # -----------------------------------------------------

    elif nom == "chancellor":
        if tour <= 6:
            bonus += 4

        if tour >= 12:
            bonus -= 8

    # -----------------------------------------------------
    # Woodcutter
    # -----------------------------------------------------

    elif nom == "woodcutter":
        if tour >= 12:
            bonus -= 8

    return bonus


# =========================================================
# SATURATION
# =========================================================

def malus_saturation(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    quantite = quantite_achetee(
        game_id,
        nom,
    )

    # -----------------------------------------------------
    # Silver
    # -----------------------------------------------------

    if nom == "silver":
        return max(
            0,
            quantite - 2,
        ) * 5

    # -----------------------------------------------------
    # Gold
    #
    # IMPORTANT :
    # Bandit doit compter.
    # -----------------------------------------------------

    if nom == "gold":
        richesse = (
            quantite_economique(
                game_id,
                "gold",
            )
        )

        malus = max(
            0,
            richesse - 4,
        ) * 5

        if richesse >= 8:
            malus += 10

        return malus

    # -----------------------------------------------------
    # Gardens
    # -----------------------------------------------------

    if nom == "gardens":
        malus = (
            quantite * 5
        )

        if quantite >= 3:
            malus += (
                quantite - 2
            ) * 5

        return malus

    # -----------------------------------------------------
    # Actions
    # -----------------------------------------------------

    if nom in (
        MALUS_PAR_COPIE_EFFECTIFS
    ):
        return (
            quantite
            * MALUS_PAR_COPIE_EFFECTIFS[
                nom
            ]
        )

    return 0


# =========================================================
# LIMITES
# =========================================================

def malus_limite(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    # Copper / Curse ne sont normalement
    # même pas évalués dans choisir_achat(),
    # mais protection supplémentaire.
    if nom in {
        "copper",
        "curse",
    }:
        return 10000

    if nom not in (
        MAX_CARTES_ACTION
    ):
        return 0

    quantite = quantite_achetee(
        game_id,
        nom,
    )

    maximum_carte = (
        MAX_CARTES_ACTION.get(
            nom
        )
    )

    if (
        maximum_carte is not None
        and quantite
        >= maximum_carte
    ):
        return 10000

    total_actions = (
        nombre_total_actions(
            game_id
        )
    )

    maximum_total = (
        max_total_actions_dynamique(
            game,
            game_id,
        )
    )

    if (
        total_actions
        >= maximum_total
    ):
        return 10000

    return 0


# =========================================================
# CALCUL DU POIDS FINAL
# =========================================================

def calculer_poids_achat(
    game: Game,
    game_id: str,
    carte: Any,
) -> dict[str, Any]:
    nom = normaliser_nom(
        carte
    )

    strategie, scores = (
        strategie_dominante(
            game,
            game_id,
        )
    )

    base = (
        POIDS_BASE_EFFECTIFS.get(
            nom,
            0,
        )
    )

    synergies = bonus_synergies(
        game,
        game_id,
        nom,
    )

    bonus_strat = (
        bonus_strategie(
            nom,
            strategie,
        )
    )

    economie = bonus_economie(
        game,
        game_id,
        nom,
    )

    phase = bonus_phase_partie(
        game,
        game_id,
        nom,
    )

    score = bonus_situation_score(
        game,
        game_id,
        nom,
    )

    structure = bonus_structure(
        game,
        game_id,
        nom,
    )

    main = bonus_main(
        game,
        game_id,
        nom,
    )

    specifique = (
        bonus_carte_specifique(
            game,
            game_id,
            nom,
        )
    )

    saturation = (
        malus_saturation(
            game,
            game_id,
            nom,
        )
    )

    limite = malus_limite(
        game,
        game_id,
        nom,
    )

    total = (
        base
        + synergies
        + bonus_strat
        + economie
        + phase
        + score
        + structure
        + main
        + specifique
        - saturation
        - limite
    )

    return {
        "base":
            base,

        "synergies":
            synergies,

        # Important :
        # ne pas utiliser la clé
        # "strategie" pour ce nombre.
        "bonus_strategie":
            bonus_strat,

        "strategie":
            strategie,

        "economie":
            economie,

        "phase":
            phase,

        "score":
            score,

        "structure":
            structure,

        "main":
            main,

        "specifique":
            specifique,

        "saturation":
            -saturation,

        "limite":
            -limite,

        "total":
            total,

        "scores_strategies":
            scores,
    }