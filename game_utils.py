import re

from dopynion.cards import Card
from dopynion.data_model import Game

from config import (
    NOM_BOT_OFFICIEL,
    NOM_JOUEUR,
)


def trouver_mon_joueur(game: Game):
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
    moi = trouver_mon_joueur(game)

    if moi is None or moi.hand is None:
        return 0

    return sum(
        Card.class_(carte).money * quantite
        for carte, quantite
        in moi.hand.quantities.items()
        if not Card.class_(carte).is_action
    )


def quantite_stock(
    game: Game,
    nom: str,
) -> int:

    nom = nom.lower()

    return next(
        (
            quantite
            for carte, quantite
            in game.stock.quantities.items()
            if carte.value.lower() == nom
        ),
        0,
    )


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
    return sum(
        quantite == 0
        for quantite
        in game.stock.quantities.values()
    )


def risque_fin_par_piles(game: Game) -> bool:
    trois_piles = sorted(
        game.stock.quantities.values()
    )[:3]

    return (
        len(trois_piles) == 3
        and sum(trois_piles) <= len(game.players)
    )


def nom_simple(nom: str) -> str:
    nom = re.sub(
        r"^\[[^\]]+\]\s*",
        "",
        nom,
    )

    nom = re.sub(
        r"\s*\([^()]+\)\s*$",
        "",
        nom,
    )

    return nom.strip()


def bot_officiel_en_face(game: Game) -> bool:
    moi = trouver_mon_joueur(game)

    if moi is None:
        return False

    mon_nom = nom_simple(moi.name)

    if mon_nom.casefold() == NOM_BOT_OFFICIEL.casefold():
        return False

    return any(
        joueur is not moi
        and nom_simple(joueur.name).casefold()
        == NOM_BOT_OFFICIEL.casefold()
        for joueur in game.players
    )