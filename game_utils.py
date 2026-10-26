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
    Calcule uniquement les cartes Trésor.

    Les bonus de Festival, Market, Woodcutter...
    sont comptés séparément.
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


def quantite_stock(
    game: Game,
    nom_carte: str,
) -> int:

    for carte, quantite in game.stock.quantities.items():

        if carte.value.lower() == nom_carte:
            return quantite

    return 0


def provinces_restantes(game: Game) -> int:
    return quantite_stock(
        game,
        "province",
    )


def curses_restantes(game: Game) -> int:
    return quantite_stock(
        game,
        "curse",
    )


def nombre_piles_vides(game: Game) -> int:
    """Nombre de piles de la réserve complètement épuisées."""

    return sum(
        1
        for quantite in game.stock.quantities.values()
        if quantite == 0
    )