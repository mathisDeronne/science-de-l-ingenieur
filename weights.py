from typing import Any

from dopynion.data_model import Game

from config import (
    CARTES_SUPPORT_ACTIONS,
    CARTES_TERMINALES,
    EFFETS_ACTIONS,
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
    provinces_restantes,
    quantite_stock,
    risque_fin_par_piles,
    trouver_mon_joueur,
)
from state import (
    nombre_carte_achetee,
    nombre_gain_estime,
    nombre_total_actions_achetees,
    obtenir_etat,
)


def cartes_stock_disponibles(
    game: Game,
) -> set[str]:
    return {
        carte.value.lower()
        for carte, quantite
        in game.stock.quantities.items()
        if quantite > 0
    }


def quantite_achetee(
    game_id: str,
    nom: str,
) -> int:
    return nombre_carte_achetee(
        game_id,
        nom,
    )


def quantite_economique(
    game_id: str,
    nom: str,
) -> int:
    return (
        nombre_carte_achetee(
            game_id,
            nom,
        )
        + nombre_gain_estime(
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
        etat.get(
            "cartes_achetees",
            {},
        ).values()
    )

    gains = sum(
        etat.get(
            "gains_estimes",
            {},
        ).values()
    )

    return (
        10
        + achats
        + gains
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


def nombre_terminales_achetees(
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


def nombre_supports_achetes(
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


def nombre_terminales_main(
    game: Game,
) -> int:
    moi = trouver_mon_joueur(
        game
    )

    if (
        moi is None
        or moi.hand is None
    ):
        return 0

    return sum(
        quantite
        for carte, quantite
        in moi.hand.quantities.items()
        if carte.value.lower()
        in CARTES_TERMINALES
    )


def scores_strategies(
    game: Game,
    game_id: str,
) -> dict[str, int]:
    stock = cartes_stock_disponibles(
        game
    )

    gold = quantite_economique(
        game_id,
        "gold",
    )

    silver = quantite_economique(
        game_id,
        "silver",
    )

    smithy = quantite_achetee(
        game_id,
        "smithy",
    )

    witch = quantite_achetee(
        game_id,
        "witch",
    )

    village = quantite_achetee(
        game_id,
        "village",
    )

    farming = quantite_achetee(
        game_id,
        "farmingvillage",
    )

    laboratory = quantite_achetee(
        game_id,
        "laboratory",
    )

    festival = quantite_achetee(
        game_id,
        "festival",
    )

    council = quantite_achetee(
        game_id,
        "councilroom",
    )

    militia = quantite_achetee(
        game_id,
        "militia",
    )

    bandit = quantite_achetee(
        game_id,
        "bandit",
    )

    gardens = quantite_achetee(
        game_id,
        "gardens",
    )

    distantshore = quantite_achetee(
        game_id,
        "distantshore",
    )

    nb_actions = (
        nombre_total_actions_achetees(
            game_id
        )
    )

    taille_deck = estimer_taille_deck(
        game_id
    )

    scores = {
        "BIG_MONEY":
            20
            + gold * 3
            + silver
            - nb_actions * 2,

        "SMITHY_MONEY":
            8
            + smithy * 16
            + gold * 2,

        "WITCH_MONEY":
            8
            + witch * 17
            + gold * 2
            + max(
                0,
                len(game.players) - 2,
            ) * 3,

        "MILITIA_MONEY":
            8
            + militia * 18
            + gold * 2
            + max(
                0,
                len(game.players) - 2,
            ) * 3,

        "BANDIT_MONEY":
            10
            + bandit * 20
            + gold
            + max(
                0,
                len(game.players) - 2,
            ) * 2,

        "VILLAGE_SMITHY":
            village * 18
            + smithy * 18,

        "LAB_WITCH":
            laboratory * 15
            + witch * 18,

        "FESTIVAL_COUNCIL":
            festival * 16
            + council * 18,

        "FARMING_ENGINE":
            farming * 16
            + max(
                smithy,
                witch,
                council,
                militia,
                bandit,
            ) * 12,

        "GARDENS": (
            gardens * 9
            + max(
                0,
                taille_deck - 20,
            )
            + distantshore * 5
            + bandit * 3
        )
        if (
            "gardens" in stock
            or gardens > 0
        )
        else -100,
    }

    disponibilites = {
        "VILLAGE_SMITHY": (
            "village",
            "smithy",
        ),

        "LAB_WITCH": (
            "laboratory",
            "witch",
        ),

        "FESTIVAL_COUNCIL": (
            "festival",
            "councilroom",
        ),
    }

    for strategie, cartes in (
        disponibilites.items()
    ):
        if all(
            nom in stock
            for nom in cartes
        ):
            scores[
                strategie
            ] += 8

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

    return (
        strategie,
        scores,
    )


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
            "smithy": 7,
            "gold": 9,
        },

        "WITCH_MONEY": {
            "witch": 9,
            "gold": 8,
        },

        "MILITIA_MONEY": {
            "militia": 10,
            "gold": 7,
            "silver": 2,
        },

        "BANDIT_MONEY": {
            "bandit": 11,
            "gold": 5,
        },

        "VILLAGE_SMITHY": {
            "village": 10,
            "smithy": 10,
        },

        "LAB_WITCH": {
            "laboratory": 10,
            "witch": 12,
        },

        "FESTIVAL_COUNCIL": {
            "festival": 10,
            "councilroom": 12,
        },

        "FARMING_ENGINE": {
            "farmingvillage": 9,
            "smithy": 5,
            "witch": 6,
            "councilroom": 6,
            "militia": 5,
            "bandit": 5,
        },

        "GARDENS": {
            "gardens": 6,
            "distantshore": 6,
            "bandit": 4,
            "market": 3,
            "festival": 3,
            "councilroom": 3,
        },
    }

    return bonus.get(
        strategie,
        {},
    ).get(
        nom,
        0,
    )


def bonus_synergies(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    stock = cartes_stock_disponibles(
        game
    )

    total = 0

    for synergie in SYNERGIES_ACHAT:
        cartes = synergie[
            "cartes"
        ]

        if nom not in cartes:
            continue

        autre = (
            cartes[1]
            if cartes[0] == nom
            else cartes[0]
        )

        bonus = synergie[
            "bonus"
        ].get(
            nom,
            0,
        )

        deja_nom = quantite_achetee(
            game_id,
            nom,
        )

        deja_autre = quantite_achetee(
            game_id,
            autre,
        )

        if (
            autre not in stock
            and deja_autre <= 0
        ):
            continue

        if (
            deja_nom == 0
            and deja_autre == 0
        ):
            total += round(
                bonus * 0.20
            )

        elif deja_autre > 0:
            if deja_nom == 0:
                facteur = 1.0

            elif deja_nom == 1:
                facteur = 0.50

            else:
                facteur = 0.25

            total += round(
                bonus * facteur
            )

    return total


def seuil_actions_cible(
    game: Game,
    game_id: str,
) -> int:
    etat = obtenir_etat(
        game_id
    )

    cible = (
        NB_ACTIONS_AVANT_ECONOMIE
    )

    strategie, scores = (
        strategie_dominante(
            game,
            game_id,
        )
    )

    moteurs = {
        "VILLAGE_SMITHY",
        "LAB_WITCH",
        "FESTIVAL_COUNCIL",
        "FARMING_ENGINE",
    }

    if (
        strategie in moteurs
        and scores[strategie] >= 30
    ):
        cible += 1

    provinces = provinces_restantes(
        game
    )

    if (
        provinces
        <= len(game.players) + 2
    ):
        cible = min(
            cible,
            1,
        )

    if etat["tour"] >= 18:
        cible = min(
            cible,
            1,
        )

    return max(
        1,
        min(
            cible,
            3,
        ),
    )


def max_total_actions_dynamique(
    game: Game,
    game_id: str,
) -> int:
    etat = obtenir_etat(
        game_id
    )

    stock = cartes_stock_disponibles(
        game
    )

    actuel = (
        nombre_total_actions_achetees(
            game_id
        )
    )

    maximum = (
        MAX_TOTAL_ACTIONS_BASE
    )

    support_present = any(
        nom in stock
        for nom in (
            "village",
            "farmingvillage",
            "festival",
        )
    )

    terminal_present = any(
        nom in stock
        for nom in (
            "smithy",
            "witch",
            "councilroom",
            "militia",
            "bandit",
        )
    )

    if (
        support_present
        and terminal_present
    ):
        maximum += 1

    if (
        "laboratory" in stock
        and terminal_present
    ):
        maximum += 1

    strategie, scores = (
        strategie_dominante(
            game,
            game_id,
        )
    )

    if (
        strategie
        in {
            "VILLAGE_SMITHY",
            "LAB_WITCH",
            "FESTIVAL_COUNCIL",
            "FARMING_ENGINE",
        }
        and scores[
            strategie
        ] >= 40
    ):
        maximum += 1

    provinces = provinces_restantes(
        game
    )

    if (
        provinces
        <= len(game.players) + 2
    ):
        maximum = min(
            maximum,
            actuel,
        )

    elif etat["tour"] >= 18:
        maximum = min(
            maximum,
            actuel + 1,
        )

    maximum = min(
        maximum,
        MAX_TOTAL_ACTIONS,
    )

    return max(
        actuel,
        maximum,
    )


def malus_saturation(
    game_id: str,
    nom: str,
) -> int:
    quantite = quantite_achetee(
        game_id,
        nom,
    )

    if nom == "silver":
        malus = quantite * 3

        if quantite >= 6:
            malus += 8

        if quantite >= 9:
            malus += 12

        return malus

    if nom == "gold":
        return quantite

    if nom == "gardens":
        malus = quantite * 5

        if quantite >= 3:
            malus += (
                quantite - 2
            ) * 5

        return malus

    if nom in EFFETS_ACTIONS:
        return (
            quantite
            * MALUS_PAR_COPIE_ACTION.get(
                nom,
                8,
            )
        )

    return 0


def malus_proximite_limite(
    game_id: str,
    nom: str,
) -> int:
    limite = MAX_CARTES_ACTION.get(
        nom
    )

    if limite is None:
        return 0

    quantite = quantite_achetee(
        game_id,
        nom,
    )

    if quantite >= limite:
        return 10000

    return round(
        (
            quantite
            / limite
        )
        * 15
    )


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

    if nom == "gold":
        if gold <= 2:
            bonus += 8

        if (
            silver >= 5
            and gold <= 2
        ):
            bonus += 15

    if nom == "silver":
        if silver >= 6:
            bonus -= 8

        if silver >= 9:
            bonus -= 12

    return bonus


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

    vp_marginaux = points_apres

    if (
        points_apres
        > points_avant
    ):
        vp_marginaux += nb_gardens

    bonus = (
        vp_marginaux * 10
    )

    # Gardens trop tôt
    if taille < 20:
        bonus -= 20

    if (
        taille < 24
        and nb_gardens == 0
    ):
        bonus -= 10

    # Gardens devient plus intéressant
    # sur les gros decks
    if taille >= 30:
        bonus += 8

    if (
        len(game.players) >= 4
        and taille < 26
    ):
        bonus -= 10

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
def bonus_phase_partie(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    etat = obtenir_etat(
        game_id
    )

    tour = etat["tour"]

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
    )

    fin_normale = (
        provinces
        <= nb_joueurs + 1
    )

    if fin_urgente:
        if nom == "province":
            bonus += 500

        elif nom == "duchy":
            bonus += 350

        elif nom == "estate":
            bonus += 220

        elif nom == "gardens":
            bonus += 180

        elif nom in EFFETS_ACTIONS:
            bonus -= 150

        elif nom == "silver":
            bonus -= 30

        elif nom == "gold":
            bonus -= 15

        return bonus

    if fin_normale:
        if nom == "province":
            bonus += 300

        elif nom == "duchy":
            bonus += 120

        elif nom == "estate":
            bonus += 30

        elif nom == "gardens":
            bonus += 50

        elif nom in EFFETS_ACTIONS:
            bonus -= 60

        elif nom == "gold":
            bonus -= 5

    if (
        nom in EFFETS_ACTIONS
        and tour > 12
    ):
        bonus -= min(
            25,
            (tour - 12) * 2,
        )

    if (
        nom == "gold"
        and tour <= 10
    ):
        bonus += 6

    if nom == "hireling":
        if tour <= 5:
            bonus += 10

        elif tour <= 9:
            bonus += 4

        elif tour >= 12:
            bonus -= 15

        if (
            provinces
            <= nb_joueurs + 2
        ):
            bonus -= 25

    if nom == "distantshore":
        if tour <= 5:
            bonus -= 5

        if (
            provinces
            <= nb_joueurs + 3
        ):
            bonus += 12

    if nom == "witch":
        curses = curses_restantes(
            game
        )

        if curses <= 0:
            bonus -= 100

        elif curses <= 3:
            bonus -= 20

        elif (
            len(game.players) >= 3
            and quantite_achetee(
                game_id,
                "witch",
            ) == 0
        ):
            bonus += 7

    return bonus


def bonus_situation_score(
    game: Game,
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

    if (
        ecart <= -8
        and provinces
        > nb_joueurs + 2
    ):
        if nom == "gold":
            bonus += 10

        elif nom == "witch":
            bonus += 8

        elif nom == "bandit":
            bonus += 8

        elif nom == "militia":
            bonus += 6

        elif nom == "laboratory":
            bonus += 5

        elif nom == "smithy":
            bonus += 4

        elif nom == "estate":
            bonus -= 15

        elif nom == "duchy":
            bonus -= 8

    if (
        ecart >= 8
        and provinces
        <= nb_joueurs + 2
    ):
        if nom == "duchy":
            bonus += 25

        elif nom == "estate":
            bonus += 15

        elif nom == "gardens":
            bonus += 15

        elif nom in EFFETS_ACTIONS:
            bonus -= 12

    return bonus


def bonus_structure_deck(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    bonus = 0

    terminales = (
        nombre_terminales_achetees(
            game_id
        )
    )

    supports = (
        nombre_supports_achetes(
            game_id
        )
    )

    capacite_terminales = (
        1 + supports
    )

    if nom in CARTES_TERMINALES:
        if (
            terminales
            >= capacite_terminales
        ):
            excedent = (
                terminales
                - capacite_terminales
                + 1
            )

            bonus -= (
                excedent * 18
            )

    if nom in CARTES_SUPPORT_ACTIONS:
        if (
            supports
            > terminales + 1
        ):
            bonus -= 15

    cible = seuil_actions_cible(
        game,
        game_id,
    )

    nb_actions = (
        nombre_total_actions_achetees(
            game_id
        )
    )

    if (
        nom in EFFETS_ACTIONS
        and nb_actions >= cible
    ):
        bonus -= (
            12
            + (
                nb_actions
                - cible
            ) * 8
        )

    return bonus


def bonus_main(
    game: Game,
    nom: str,
) -> int:
    terminales = nombre_terminales_main(
        game
    )

    if (
        nom in CARTES_TERMINALES
        and terminales >= 2
    ):
        return -8

    if (
        nom in CARTES_SUPPORT_ACTIONS
        and terminales >= 1
    ):
        return 4

    return 0


def bonus_carte_specifique(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    bonus = 0

    etat = obtenir_etat(
        game_id
    )

    tour = etat["tour"]

    stock = cartes_stock_disponibles(
        game
    )

    if nom == "woodcutter":
        if stock & {
            "market",
            "festival",
            "councilroom",
        }:
            bonus -= 15

    if nom == "chancellor":
        if tour <= 7:
            bonus += 2

        if tour >= 12:
            bonus -= 10

    if nom == "militia":
        if tour <= 8:
            bonus += 7

        elif tour >= 16:
            bonus -= 8

        bonus += max(
            0,
            len(game.players) - 2,
        ) * 4

        if (
            quantite_achetee(
                game_id,
                "councilroom",
            ) > 0
            and nombre_supports_achetes(
                game_id
            ) > 0
        ):
            bonus += 10

    if nom == "bandit":
        gold_restant = quantite_stock(
            game,
            "gold",
        )

        if gold_restant <= 0:
            bonus -= 200

        elif tour <= 10:
            bonus += 9

        elif tour >= 16:
            bonus -= 12

        bonus += max(
            0,
            len(game.players) - 2,
        ) * 3

        if (
            quantite_economique(
                game_id,
                "gold",
            ) <= 2
        ):
            bonus += 6

    if nom == "laboratory":
        nb_lab = quantite_achetee(
            game_id,
            "laboratory",
        )

        if nb_lab == 1:
            bonus += 3

        elif nb_lab == 2:
            bonus += 2

    if (
        nom == "distantshore"
        and quantite_achetee(
            game_id,
            "farmingvillage",
        ) > 0
    ):
        bonus += 6

    if nom == "gardens":
        bonus += bonus_gardens(
            game,
            game_id,
        )

    return bonus


def calculer_poids_achat(
    game: Game,
    game_id: str,
    nom: str,
) -> dict[str, Any]:
    base = POIDS_BASE_ACHAT.get(
        nom,
        -10000,
    )

    strategie, scores = (
        strategie_dominante(
            game,
            game_id,
        )
    )

    composants = {
        "base":
            base,

        "synergies":
            bonus_synergies(
                game,
                game_id,
                nom,
            ),

        "bonus_strategie":
            bonus_strategie(
                nom,
                strategie,
            ),

        "economie":
            bonus_economie(
                game,
                game_id,
                nom,
            ),

        "phase":
            bonus_phase_partie(
                game,
                game_id,
                nom,
            ),

        "score":
            bonus_situation_score(
                game,
                nom,
            ),

        "structure":
            bonus_structure_deck(
                game,
                game_id,
                nom,
            ),

        "main":
            bonus_main(
                game,
                nom,
            ),

        "specifique":
            bonus_carte_specifique(
                game,
                game_id,
                nom,
            ),

        "saturation":
            -malus_saturation(
                game_id,
                nom,
            ),

        "limite":
            -malus_proximite_limite(
                game_id,
                nom,
            ),
    }

    total = sum(
        composants.values()
    )

    return {
        **composants,

        "total":
            total,

        "strategie":
            strategie,

        "scores_strategies":
            scores,
    }