from dopynion.cards import Card
from dopynion.data_model import Game

from config import NOM_JOUEUR


def trouver_mon_joueur(game: Game):
    """Notre joueur est normalement celui dont la main est visible."""

    moi = next(
        (
            joueur
            for joueur in game.players
            if joueur.hand is not None
        ),
        None,
    )

    if moi is None:
        moi = next(
            (
                joueur
                for joueur in game.players
                if NOM_JOUEUR.lower()
                in joueur.name.lower()
            ),
            None,
        )

    return moi


def calculer_argent_main(game: Game) -> int:
    """
    Calcule uniquement l'argent provenant des cartes Trésor.

    Les pièces données par les cartes Action sont gérées
    séparément dans l'état du tour.
    """

    moi = trouver_mon_joueur(game)

    if moi is None or moi.hand is None:
        return 0

    argent = 0

    for carte, quantite in moi.hand.quantities.items():

        infos = Card.class_(carte)

        if not infos.is_action:
            argent += infos.money * quantite

    return argent


def provinces_restantes(game: Game) -> int:
    """Nombre de Provinces encore présentes dans la réserve."""

    for carte, quantite in game.stock.quantities.items():

        if carte.value.lower() == "province":
            return quantite

    return 0