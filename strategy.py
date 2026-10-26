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
    TOUR_FIN,
    TOUR_FIN_URGENTE,
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


#####################################################
# Actions
#####################################################


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

    for nom_prioritaire in PRIORITE_ACTION:

        for carte, quantite in moi.hand.quantities.items():

            if (
                quantite > 0
                and carte.value.lower()
                == nom_prioritaire
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

    # Jouer une Action consomme une Action.
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

    argent_tresor = calculer_argent_main(
        game
    )

    # L'arbitre peut retirer les Trésors de la main
    # après un achat : le budget est donc figé ici.
    etat["argent_restant"] = (
        argent_tresor
        + etat["bonus_pieces"]
    )

    etat["phase_achat"] = True


#####################################################
# Limites des Actions
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
# Witch
#####################################################


def prioriser_premiere_witch(
    priorite: list[str],
    game: Game,
    game_id: str,
) -> list[str]:
    """
    Jusqu'au tour 8 :

        Province
        Gold
        Witch
        Silver

    si nous n'avons pas encore acheté Witch
    et qu'il reste des Curse.

    La règle fonctionne même à 2 joueurs.
    """

    etat = obtenir_etat(game_id)

    if etat["tour"] > 8:
        return priorite

    if curses_restantes(game) <= 0:
        return priorite

    if (
        nombre_carte_achetee(
            game_id,
            "witch",
        )
        > 0
    ):
        return priorite

    priorite = priorite.copy()

    if "witch" in priorite:
        priorite.remove("witch")

    if "gold" in priorite:

        position_gold = priorite.index(
            "gold"
        )

        priorite.insert(
            position_gold + 1,
            "witch",
        )

    else:
        priorite.insert(
            0,
            "witch",
        )

    return priorite


#####################################################
# Priorité d'achat
#####################################################


def obtenir_priorite_achat(
    game: Game,
    game_id: str,
) -> list[str]:

    etat = obtenir_etat(game_id)

    tour = etat["tour"]

    provinces = provinces_restantes(
        game
    )

    nb_joueurs = len(
        game.players
    )

    nb_actions = (
        nombre_total_actions_achetees(
            game_id
        )
    )


    #################################################
    # Seuils selon le nombre de joueurs
    #################################################

    # Plus il y a de joueurs, plus les Provinces
    # peuvent disparaître entre deux de nos tours.

    seuil_fin = (
        nb_joueurs + 1
    )

    seuil_fin_urgente = max(
        1,
        nb_joueurs - 1,
    )


    #################################################
    # Fin urgente
    #################################################

    if (
        provinces <= seuil_fin_urgente
        or risque_fin_par_piles(game)
        or tour >= TOUR_FIN_URGENTE
    ):
        return PRIORITE_ACHAT_FIN_URGENTE


    #################################################
    # Fin normale
    #################################################

    if (
        provinces <= seuil_fin
        or tour >= TOUR_FIN
    ):
        return PRIORITE_ACHAT_FIN


    #################################################
    # Moteur déjà construit
    #################################################

    if (
        nb_actions
        >= NB_ACTIONS_AVANT_ECONOMIE
    ):

        priorite = (
            PRIORITE_ACHAT_ECONOMIE.copy()
        )

        return prioriser_premiere_witch(
            priorite,
            game,
            game_id,
        )


    #################################################
    # Début
    #################################################

    if tour <= 6:

        priorite = (
            PRIORITE_ACHAT_DEBUT.copy()
        )

        return prioriser_premiere_witch(
            priorite,
            game,
            game_id,
        )


    #################################################
    # Milieu
    #################################################

    priorite = (
        PRIORITE_ACHAT_MILIEU.copy()
    )

    return prioriser_premiere_witch(
        priorite,
        game,
        game_id,
    )


#####################################################
# Achat
#####################################################


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
        for carte, quantite
        in game.stock.quantities.items()
        if (
            quantite > 0
            and Card.class_(carte).cost
            <= argent
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

    # On n'achète volontairement ni Copper
    # ni Curse si rien d'intéressant n'est disponible.
    return None