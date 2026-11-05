from typing import Any

from dopynion.cards import Card

from config import (
    CARTES_SUPPORT_ACTIONS,
    CARTES_TERMINALES,
    TOUR_MAX_CHANCELLOR,
)


# =========================================================
# RÉACTIONS AUX CARTES
# =========================================================


# Valeur approximative d'une carte en main, en "pièces".
VALEUR_EN_MAIN = {
    "copper": 1.0,
    "silver": 2.0,
    "gold": 3.0,

    # Non terminales
    "laboratory": 2.5,
    "market": 2.5,
    "festival": 2.5,
    "distantshore": 1.5,
    "village": 1.0,
    "farmingvillage": 1.2,

    # Terminales
    "hireling": 4.0,
    "witch": 3.5,
    "councilroom": 3.5,
    "smithy": 3.0,
    "militia": 2.5,
    "bandit": 2.5,
    "woodcutter": 2.2,
    "chancellor": 2.0,
    "bureaucrat": 1.8,
}

# Hireling n'est pas dans CARTES_TERMINALES
# (elle quitte le deck une fois jouée) mais
# consomme bien une action ce tour-là.
TERMINALES_EN_MAIN = (
    CARTES_TERMINALES
    | {"hireling"}
)


def valeur_main(
    noms: list[str],
) -> float:
    terminales = sorted(
        (
            VALEUR_EN_MAIN.get(
                nom,
                0.0,
            )
            for nom in noms
            if nom
            in TERMINALES_EN_MAIN
        ),
        reverse=True,
    )

    # Chaque carte +2 Actions permet de
    # jouer une terminale de plus.
    jouables = 1 + sum(
        nom
        in CARTES_SUPPORT_ACTIONS
        for nom in noms
    )

    autres = sum(
        VALEUR_EN_MAIN.get(
            nom,
            0.0,
        )
        for nom in noms
        if nom
        not in TERMINALES_EN_MAIN
    )

    # Seules les meilleures terminales
    # jouables comptent : deux Smithy sans
    # Village, la seconde ne sert à rien.
    return (
        autres
        + sum(
            terminales[
                :jouables
            ]
        )
    )


def carte_a_defausser(
    cartes: list[Any],
) -> Any:
    """
    Choisit la carte dont la défausse
    laisse la meilleure main.

    Utilisé par la Militia adverse : le
    hook est appelé une fois par carte
    jusqu'à 3 cartes en main.
    """

    if not cartes:
        return None

    noms = [
        str(carte)
        for carte in cartes
    ]

    meilleur_index = None
    meilleure_cle = None

    for index in range(
        len(cartes)
    ):
        restantes = (
            noms[:index]
            + noms[index + 1:]
        )

        cle = (
            valeur_main(
                restantes
            ),
            # À valeur égale : défausser
            # d'abord les cartes victoire,
            # puis les moins chères.
            Card.class_(
                noms[index]
            ).is_victory
            or noms[index]
            == "curse",
            -Card.class_(
                noms[index]
            ).cost,
        )

        if (
            meilleure_cle is None
            or cle > meilleure_cle
        ):
            meilleure_cle = cle
            meilleur_index = index

    return cartes[
        meilleur_index
    ]


def fin_de_partie_proche(
    etat: dict[str, Any],
) -> bool:
    provinces = etat.get(
        "provinces_restantes"
    )

    nb_joueurs = etat.get(
        "nb_joueurs"
    ) or 2

    return (
        provinces is not None
        and provinces
        <= nb_joueurs + 2
    )


def accepter_defausse_carte(
    carte: Any,
) -> bool:
    """
    Défausser CETTE carte (ex : Cellar,
    qui fait repiocher autant de cartes) ?

    Oui seulement pour les cartes mortes
    en main : Curse et cartes victoire
    pures.
    """

    nom = str(carte)

    classe = Card.class_(
        nom
    )

    return (
        nom == "curse"
        or (
            classe.is_victory
            and not classe.is_action
        )
    )


def accepter_ecarter_carte(
    carte: Any,
    etat: dict[str, Any],
) -> bool:
    """
    Écarter CETTE carte (ex : Chapel) ?

    Curse et Copper : oui.
    Estate : oui, sauf en fin de partie
    (c'est 1 point de victoire).
    Tout le reste : non.
    """

    nom = str(carte)

    if nom in {
        "curse",
        "copper",
    }:
        return True

    if nom == "estate":
        return not fin_de_partie_proche(
            etat
        )

    return False


def accepter_defausse_deck(
    etat: dict[str, Any],
) -> bool:
    """
    Chancellor : défausser son deck ?

    Oui tant que les cartes achetées
    récemment sont utiles (début et
    milieu de partie), non en fin de
    partie (on achète surtout des
    cartes victoire).
    """

    tour = int(
        etat.get(
            "tour",
            0,
        )
        or 0
    )

    provinces = etat.get(
        "provinces_restantes"
    )

    nb_joueurs = etat.get(
        "nb_joueurs"
    ) or 2

    if tour > TOUR_MAX_CHANCELLOR:
        return False

    if (
        provinces is not None
        and provinces
        <= nb_joueurs + 2
    ):
        return False

    return True
