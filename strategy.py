from dopynion.cards import Card
from dopynion.data_model import CardName, Game

from config import (
    EFFETS_ACTIONS,
    MAX_CARTES_ACTION,
    MAX_TOTAL_ACTIONS,
    NB_ACTIONS_AVANT_ECONOMIE,
    PILES_VIDES_URGENCE,
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
    nombre_piles_vides,
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

    # Jouer une Action coûte 1 Action.
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

    # L'arbitre peut retirer les Trésors de la main
    # après un premier achat : on conserve donc le budget.
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
# Choix de la stratégie d'achat
#####################################################


def obtenir_priorite_achat(
    game: Game,
    game_id: str,
) -> list[str]:

    etat = obtenir_etat(game_id)

    tour = etat["tour"]

    nb_joueurs = len(game.players)

    provinces = provinces_restantes(game)
    curses = curses_restantes(game)
    piles_vides = nombre_piles_vides(game)

    nb_actions = nombre_total_actions_achetees(
        game_id
    )

    # Plus il y a de joueurs, plus les Provinces peuvent
    # disparaître rapidement entre deux de nos tours.
    seuil_fin = nb_joueurs + 1
    seuil_fin_urgente = max(
        1,
        nb_joueurs - 1,
    )


    #################################################
    # Fin urgente
    #################################################

    if (
        provinces <= seuil_fin_urgente
        or piles_vides >= PILES_VIDES_URGENCE
        or tour >= TOUR_FIN_URGENTE
    ):
        return PRIORITE_ACHAT_FIN_URGENTE


    #################################################
    # Fin de partie
    #################################################

    if (
        provinces <= seuil_fin
        or tour >= TOUR_FIN
    ):
        return PRIORITE_ACHAT_FIN


    #################################################
    # Moteur déjà construit
    #################################################

    if nb_actions >= NB_ACTIONS_AVANT_ECONOMIE:

        priorite = PRIORITE_ACHAT_ECONOMIE.copy()

        # Witch est particulièrement intéressante à
        # 3 ou 4 joueurs tant qu'il reste des Curses.
        if (
            nb_joueurs >= 3
            and curses > 0
            and nombre_carte_achetee(
                game_id,
                "witch",
            ) == 0
        ):

            priorite.remove("witch")

            # Province > Gold > Witch > Silver
            priorite.insert(
                2,
                "witch",
            )

        return priorite


    #################################################
    # Début
    #################################################

    if tour <= 6:
        return PRIORITE_ACHAT_DEBUT


    #################################################
    # Milieu
    #################################################

    return PRIORITE_ACHAT_MILIEU


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

    # Curse et Copper ne sont dans aucune priorité.
    # Si rien d'intéressant n'est disponible :
    # on termine le tour.
    return None