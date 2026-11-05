import re

from dopynion.cards import Card
from dopynion.data_model import Game

from config import NOM_BOT_OFFICIEL
from state import obtenir_etat


def trouver_mon_joueur(
    game: Game,
):
    return next(
        (
            joueur
            for joueur
            in game.players
            if joueur.hand is not None
        ),
        None,
    )


def calculer_argent_main(
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
        Card.class_(
            carte
        ).money
        * quantite
        for carte, quantite
        in moi.hand.quantities.items()
        if not Card.class_(
            carte
        ).is_action
    )


def quantite_stock(
    game: Game,
    nom: str,
) -> int:
    # CardName est une chaîne en
    # minuscules : "province" == carte.
    return next(
        (
            quantite
            for carte, quantite
            in game.stock.quantities.items()
            if carte == nom
        ),
        0,
    )


def provinces_restantes(
    game: Game,
) -> int:
    return quantite_stock(
        game,
        "province",
    )


def curses_restantes(
    game: Game,
) -> int:
    return quantite_stock(
        game,
        "curse",
    )


def piles_presentes(
    game: Game,
) -> set[str]:
    return {
        str(carte)
        for carte, quantite
        in game.stock.quantities.items()
        if quantite > 0
    }


def nombre_piles_vides(
    game: Game,
    game_id: str | None = None,
) -> int:
    # Attention : Dopynion RETIRE les
    # piles vides de la réserve envoyée.
    # Compter les quantités à 0 donne
    # donc toujours 0. Il faut comparer
    # avec les piles vues au premier
    # /play de la partie.
    vides_explicites = sum(
        quantite == 0
        for quantite
        in game.stock.quantities.values()
    )

    if game_id is None:
        return vides_explicites

    initiales = obtenir_etat(
        game_id
    ).get(
        "piles_initiales"
    )

    if not initiales:
        return vides_explicites

    return len(
        set(initiales)
        - piles_presentes(
            game
        )
    )


def risque_fin_par_piles(
    game: Game,
    game_id: str | None = None,
) -> bool:
    vides = nombre_piles_vides(
        game,
        game_id,
    )

    if vides >= 3:
        return True

    manquantes = 3 - vides

    plus_petites = sorted(
        quantite
        for quantite
        in game.stock.quantities.values()
        if quantite > 0
    )[:manquantes]

    return (
        len(plus_petites)
        == manquantes
        and sum(
            plus_petites
        ) <= len(
            game.players
        )
    )


def nom_simple(
    nom: str,
) -> str:
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


def bot_officiel_en_face(
    game: Game,
) -> bool:
    moi = trouver_mon_joueur(
        game
    )

    if moi is None:
        return False

    if (
        nom_simple(
            moi.name
        ).casefold()
        == NOM_BOT_OFFICIEL.casefold()
    ):
        return False

    return any(
        joueur is not moi
        and nom_simple(
            joueur.name
        ).casefold()
        == NOM_BOT_OFFICIEL.casefold()
        for joueur
        in game.players
    )