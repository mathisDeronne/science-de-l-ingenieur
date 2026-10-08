from dopynion.cards import Card
from dopynion.data_model import CardName, Game

from config import (
    EFFETS_ACTIONS,
    MAX_CARTES_ACTION,
    MAX_TOTAL_ACTIONS,
    PRIORITE_ACTION,
    PRIORITE_ACHAT_DEBUT,
    PRIORITE_ACHAT_MILIEU,
    PRIORITE_ACHAT_FIN,
    PRIORITE_ACHAT_FIN_URGENTE,
    TOUR_FIN,
    TOUR_FIN_URGENTE,
    PROVINCES_FIN,
    PROVINCES_FIN_URGENTE,
)
from game_utils import (
    calculer_argent_main,
    provinces_restantes,
    trouver_mon_joueur,
)
from state import (
    nombre_carte_achetee,
    nombre_total_actions_achetees,
    obtenir_etat,
)


#####################################################
# Actions
#####################################################


def choisir_action(
    game: Game,
    game_id: str,
) -> CardName | None:

    etat = obtenir_etat(game_id)

    if etat["phase_achat"] or etat["actions_restantes"] <= 0:
        return None

    moi = trouver_mon_joueur(game)

    if moi is None or moi.hand is None:
        return None

    main = moi.hand.quantities

    for nom_prioritaire in PRIORITE_ACTION:
        for carte, quantite in main.items():

            if (
                quantite > 0
                and carte.value.lower() == nom_prioritaire
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

    # Jouer une carte Action consomme une Action.
    etat["actions_restantes"] -= 1

    etat["actions_restantes"] += effet["actions"]
    etat["achats_restants"] += effet["achats"]
    etat["bonus_pieces"] += effet["pieces"]

    print(
        f">>> {carte.value} jouée | "
        f"Actions={etat['actions_restantes']} | "
        f"Achats={etat['achats_restants']} | "
        f"Bonus={etat['bonus_pieces']}",
        flush=True,
    )


#####################################################
# Phase achat
#####################################################


def commencer_phase_achat(
    game: Game,
    game_id: str,
) -> None:

    etat = obtenir_etat(game_id)

    if etat["phase_achat"]:
        return

    argent_tresor = calculer_argent_main(game)

    # On garde le budget localement car l'arbitre
    # peut retirer les Trésors après un premier achat.
    etat["argent_restant"] = (
        argent_tresor
        + etat["bonus_pieces"]
    )

    etat["phase_achat"] = True


#####################################################
# Limites des cartes Action
#####################################################


def carte_action_autorisee(
    game_id: str,
    nom_carte: str,
) -> bool:

    limite = MAX_CARTES_ACTION.get(
        nom_carte,
        0,
    )

    if limite <= 0:
        return False

    if (
        nombre_total_actions_achetees(game_id)
        >= MAX_TOTAL_ACTIONS
    ):
        return False

    return (
        nombre_carte_achetee(
            game_id,
            nom_carte,
        )
        < limite
    )


#####################################################
# Priorité des achats
#####################################################


def obtenir_priorite_achat(
    game: Game,
    game_id: str,
) -> list[str]:

    etat = obtenir_etat(game_id)

    tour = etat["tour"]
    provinces = provinces_restantes(game)
    nb_actions = nombre_total_actions_achetees(game_id)

    # Fin très proche : priorité maximale aux points.
    if (
        provinces <= PROVINCES_FIN_URGENTE
        or tour >= TOUR_FIN_URGENTE
    ):
        return PRIORITE_ACHAT_FIN_URGENTE

    # Fin de partie : Province puis Duché.
    if (
        provinces <= PROVINCES_FIN
        or tour >= TOUR_FIN
    ):
        return PRIORITE_ACHAT_FIN

    # Après 2 cartes Action, on renforce surtout l'économie.
    if nb_actions >= 2:
        return [
            "province",
            "gold",
            "silver",
            "laboratory",
            "smithy",
            "festival",
            "market",
            "village",
        ]

    if tour <= 6:
        return PRIORITE_ACHAT_DEBUT

    return PRIORITE_ACHAT_MILIEU


def choisir_achat(
    game: Game,
    game_id: str,
) -> CardName | None:

    etat = obtenir_etat(game_id)

    if etat["achats_restants"] <= 0:
        return None

    argent = etat["argent_restant"]

    if argent is None:
        return None

    achetables = [
        carte
        for carte, quantite in game.stock.quantities.items()
        if (
            quantite > 0
            and Card.class_(carte).cost <= argent
        )
    ]

    priorite = obtenir_priorite_achat(
        game,
        game_id,
    )

    for nom_prioritaire in priorite:
        for carte in achetables:

            nom = carte.value.lower()

            if nom != nom_prioritaire:
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

    # On préfère ne rien acheter plutôt qu'un Copper inutile.
    return None