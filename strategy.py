from dopynion.cards import Card
from dopynion.data_model import CardName, Game

from config import (
    EFFETS_ACTIONS,
    MAX_CARTES_ACTION,
    MAX_TOTAL_ACTIONS,
    NB_ACTIONS_AVANT_ECONOMIE,
    PRIORITE_ACTION,
    PRIORITE_ACHAT_DEBUT,
    PRIORITE_ACHAT_ECONOMIE,
    PRIORITE_ACHAT_FIN,
    PRIORITE_ACHAT_FIN_URGENTE,
    PRIORITE_ACHAT_MILIEU,
)
from game_utils import (
    calculer_argent_main,
    curses_restantes,
    provinces_restantes,
    risque_fin_par_piles,
    trouver_mon_joueur,
)
from state import (
    nombre_carte_achetee,
    nombre_total_actions_achetees,
    obtenir_etat,
)


def choisir_action(
    game: Game,
    game_id: str,
) -> CardName | None:

    etat = obtenir_etat(game_id)

    if (
        etat["phase_achat"]
        or etat["actions_restantes"] <= 0
    ):
        return None

    moi = trouver_mon_joueur(game)

    if moi is None or moi.hand is None:
        return None

    for nom in PRIORITE_ACTION:
        for carte, quantite in moi.hand.quantities.items():

            if (
                quantite > 0
                and carte.value.lower() == nom
                and Card.class_(carte).is_action
            ):
                return carte

    return None


def appliquer_effet_action(
    game_id: str,
    carte: CardName,
) -> None:

    etat = obtenir_etat(game_id)

    effet = EFFETS_ACTIONS.get(
        carte.value.lower(),
        {
            "actions": 0,
            "achats": 0,
            "pieces": 0,
        },
    )

    etat["actions_restantes"] += (
        effet["actions"] - 1
    )

    etat["achats_restants"] += effet["achats"]
    etat["bonus_pieces"] += effet["pieces"]


def commencer_phase_achat(
    game: Game,
    game_id: str,
) -> None:

    etat = obtenir_etat(game_id)

    if etat["phase_achat"]:
        return

    etat["argent_restant"] = (
        calculer_argent_main(game)
        + etat["bonus_pieces"]
    )

    etat["phase_achat"] = True


def carte_action_autorisee(
    game_id: str,
    nom: str,
) -> bool:

    limite = MAX_CARTES_ACTION.get(
        nom,
        0,
    )

    return (
        limite > 0
        and nombre_total_actions_achetees(game_id)
        < MAX_TOTAL_ACTIONS
        and nombre_carte_achetee(game_id, nom)
        < limite
    )


def prioriser_premiere_witch(
    priorite: list[str],
    game: Game,
    game_id: str,
) -> list[str]:

    etat = obtenir_etat(game_id)

    if (
        etat["tour"] > 8
        or curses_restantes(game) <= 0
        or nombre_carte_achetee(
            game_id,
            "witch",
        ) > 0
        or "witch" not in priorite
    ):
        return priorite

    priorite = [
        nom
        for nom in priorite
        if nom != "witch"
    ]

    if (
        len(game.players) >= 3
        and etat["tour"] <= 3
    ):
        position = (
            priorite.index("province") + 1
            if "province" in priorite
            else 0
        )

    else:
        position = (
            priorite.index("gold") + 1
            if "gold" in priorite
            else 0
        )

    priorite.insert(
        position,
        "witch",
    )

    return priorite


def obtenir_priorite_achat(
    game: Game,
    game_id: str,
) -> list[str]:

    etat = obtenir_etat(game_id)

    nb_joueurs = len(game.players)
    provinces = provinces_restantes(game)

    if (
        provinces <= max(
            1,
            nb_joueurs - 1,
        )
        or risque_fin_par_piles(game)
    ):
        return PRIORITE_ACHAT_FIN_URGENTE

    if provinces <= nb_joueurs + 1:
        return PRIORITE_ACHAT_FIN

    if (
        nombre_total_actions_achetees(game_id)
        >= NB_ACTIONS_AVANT_ECONOMIE
    ):
        priorite = PRIORITE_ACHAT_ECONOMIE

    elif etat["tour"] <= 6:
        priorite = PRIORITE_ACHAT_DEBUT

    else:
        priorite = PRIORITE_ACHAT_MILIEU

    return prioriser_premiere_witch(
        priorite,
        game,
        game_id,
    )


def choisir_achat(
    game: Game,
    game_id: str,
) -> CardName | None:

    etat = obtenir_etat(game_id)

    if (
        etat["achats_restants"] <= 0
        or etat["argent_restant"] is None
    ):
        return None

    achetables = {
        carte.value.lower(): carte
        for carte, quantite
        in game.stock.quantities.items()
        if (
            quantite > 0
            and Card.class_(carte).cost
            <= etat["argent_restant"]
        )
    }

    for nom in obtenir_priorite_achat(
        game,
        game_id,
    ):
        carte = achetables.get(nom)

        if carte is None:
            continue

        if (
            Card.class_(carte).is_action
            and not carte_action_autorisee(
                game_id,
                nom,
            )
        ):
            continue

        return carte

    return None