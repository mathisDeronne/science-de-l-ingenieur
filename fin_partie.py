from dopynion.data_model import Game

from config import (
    BONUS_FIN_GAGNANTE,
    MALUS_AVANT_DERNIERE_PROVINCE,
    MALUS_FIN_PERDANTE,
)
from deck import (
    composition_deck,
    points_victoire,
)
from game_utils import (
    nombre_piles_vides,
    provinces_restantes,
    quantite_stock,
    trouver_mon_joueur,
)
from state import obtenir_etat


# =========================================================
# FIN DE PARTIE
# =========================================================
#
# Dopynion termine la partie quand la pile de Provinces
# est vide ou quand 3 piles sont vides.
#
# Pour chaque achat possible, on regarde s'il termine la
# partie et, si oui, si on gagne après l'achat (nos scores
# et ceux des adversaires sont exacts dans Dopynion).
# =========================================================

SCORE_ELIMINE = -10000


def meilleur_score_adverse(
    game: Game,
) -> int | None:
    moi = trouver_mon_joueur(
        game
    )

    scores = [
        joueur.score
        for joueur
        in game.players
        if joueur is not moi
        and joueur.score
        > SCORE_ELIMINE
    ]

    return (
        max(scores)
        if scores
        else None
    )


def score_apres_achat(
    game: Game,
    game_id: str,
    nom: str,
) -> int | None:
    moi = trouver_mon_joueur(
        game
    )

    if moi is None:
        return None

    avant = composition_deck(
        game_id
    )

    apres = dict(
        avant
    )

    apres[nom] = (
        apres.get(
            nom,
            0,
        )
        + 1
    )

    # Score exact actuel + ce que
    # l'achat rapporte (Gardens compris).
    return (
        moi.score
        + points_victoire(
            apres
        )
        - points_victoire(
            avant
        )
    )


def achat_termine_partie(
    game: Game,
    game_id: str,
    nom: str,
) -> bool:
    if quantite_stock(
        game,
        nom,
    ) != 1:
        return False

    if nom == "province":
        return True

    return (
        nombre_piles_vides(
            game,
            game_id,
        )
        + 1
        >= 3
    )


def peut_acheter_deux_provinces(
    game_id: str,
) -> bool:
    etat = obtenir_etat(
        game_id
    )

    argent = etat.get(
        "argent_restant"
    ) or 0

    return (
        etat.get(
            "achats_restants",
            0,
        ) >= 2
        and argent >= 16
    )


def bonus_fin_partie(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    adverse = meilleur_score_adverse(
        game
    )

    mon_score = score_apres_achat(
        game,
        game_id,
        nom,
    )

    if (
        adverse is None
        or mon_score is None
    ):
        return 0

    # -----------------------------------------------------
    # L'achat termine la partie.
    # -----------------------------------------------------

    if achat_termine_partie(
        game,
        game_id,
        nom,
    ):
        if mon_score > adverse:
            return BONUS_FIN_GAGNANTE

        if mon_score < adverse:
            return -MALUS_FIN_PERDANTE

        # Égalité : ni bonus ni interdiction.
        return 0

    # -----------------------------------------------------
    # Avant-dernière Province : ne pas la
    # prendre si un adversaire peut ensuite
    # gagner en prenant la dernière.
    # -----------------------------------------------------

    if (
        nom == "province"
        and provinces_restantes(
            game
        ) == 2
        and adverse + 6
        > mon_score
        and not peut_acheter_deux_provinces(
            game_id
        )
    ):
        return -MALUS_AVANT_DERNIERE_PROVINCE

    return 0
