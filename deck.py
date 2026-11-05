from collections import Counter

from dopynion.data_model import Game

from game_utils import (
    piles_presentes,
    provinces_restantes,
    trouver_mon_joueur,
)
from state import obtenir_etat


# =========================================================
# SUIVI DU DECK
# =========================================================
#
# Composition estimée de notre deck :
#
#   deck de départ (7 Copper + 3 Estate)
#   + cartes achetées
#   + cartes gagnées (Bandit -> Gold, Distant Shore ->
#     Estate, Bureaucrat -> Silver)
#   - cartes sorties du deck (Hireling jouée)
#   + Curses reçues
#
# Les Curses reçues n'ont pas de callback : on les DÉDUIT
# de notre score, qui est exact dans Dopynion (il compte
# toutes nos cartes, Curses comprises).
#
# Limite : un Bandit adverse qui écarte un de nos
# Silver/Gold ne se voit pas (pas de callback, pas d'effet
# sur le score).
# =========================================================

DECK_DE_DEPART = {
    "copper": 7,
    "estate": 3,
}

POINTS_VICTOIRE = {
    "province": 6,
    "duchy": 3,
    "estate": 1,
    "distantshore": 2,
    "curse": -1,
}

MAX_CURSES_RECHERCHE = 30


def composition_deck(
    game_id: str,
    avec_curses: bool = True,
) -> dict[str, int]:
    etat = obtenir_etat(
        game_id
    )

    deck = Counter(
        DECK_DE_DEPART
    )

    deck.update(
        etat.get(
            "cartes_achetees",
            {},
        )
    )

    deck.update(
        etat.get(
            "gains_estimes",
            {},
        )
    )

    deck.subtract(
        etat.get(
            "cartes_retirees",
            {},
        )
    )

    if avec_curses:
        deck["curse"] += int(
            etat.get(
                "curses_recues",
                0,
            )
        )

    return {
        carte: quantite
        for carte, quantite
        in deck.items()
        if quantite > 0
    }


def taille_deck(
    game_id: str,
) -> int:
    return sum(
        composition_deck(
            game_id
        ).values()
    )


def points_victoire(
    deck: dict[str, int],
) -> int:
    taille = sum(
        deck.values()
    )

    return (
        sum(
            POINTS_VICTOIRE.get(
                carte,
                0,
            )
            * quantite
            for carte, quantite
            in deck.items()
        )
        + deck.get(
            "gardens",
            0,
        )
        * (taille // 10)
    )


def deduire_curses_recues(
    game: Game,
    game_id: str,
) -> None:
    moi = trouver_mon_joueur(
        game
    )

    if moi is None:
        return

    etat = obtenir_etat(
        game_id
    )

    sans_curses = composition_deck(
        game_id,
        avec_curses=False,
    )

    deja = sans_curses.get(
        "curse",
        0,
    )

    # Plus petit nombre de Curses qui
    # explique exactement notre score.
    for curses in range(
        MAX_CURSES_RECHERCHE + 1
    ):
        deck = dict(
            sans_curses
        )

        deck["curse"] = (
            deja
            + curses
        )

        if (
            points_victoire(
                deck
            )
            == moi.score
        ):
            etat[
                "curses_recues"
            ] = curses

            etat[
                "deck_coherent"
            ] = True

            return

    # Aucun nombre ne colle : notre
    # suivi est faux quelque part.
    # On garde la dernière valeur.
    etat[
        "deck_coherent"
    ] = False


def observer_partie(
    game: Game,
    game_id: str,
) -> None:
    """
    À appeler au début de chaque /play,
    avant toute décision.
    """

    etat = obtenir_etat(
        game_id
    )

    if not etat.get(
        "piles_initiales"
    ):
        etat[
            "piles_initiales"
        ] = sorted(
            piles_presentes(
                game
            )
        )

    etat[
        "provinces_restantes"
    ] = provinces_restantes(
        game
    )

    etat[
        "nb_joueurs"
    ] = len(
        game.players
    )

    deduire_curses_recues(
        game,
        game_id,
    )


def enregistrer_carte_retiree(
    game_id: str,
    nom: str,
) -> None:
    retirees = obtenir_etat(
        game_id
    ).setdefault(
        "cartes_retirees",
        {},
    )

    retirees[nom] = (
        retirees.get(
            nom,
            0,
        )
        + 1
    )
