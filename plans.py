from typing import Any

from dopynion.data_model import Game

from config import (
    BONUS_CARTE_CLE,
    PLAN_PAR_DEFAUT,
    PLANS,
    TOUR_MAX_CHANGEMENT_PLAN,
)
from game_utils import (
    curses_restantes,
    quantite_stock,
)
from state import obtenir_etat


# =========================================================
# PLAN DE PARTIE
# =========================================================
#
# 1. Au premier achat : on note chaque plan possible dans
#    ce royaume et on garde le meilleur.
#
# 2. Ensuite, une vérification par tour : si un déclencheur
#    fort apparaît, on change de plan. UNE SEULE FOIS par
#    partie, et avant TOUR_MAX_CHANGEMENT_PLAN.
# =========================================================


def noter_plans(
    game: Game,
    exclure: str | None = None,
) -> dict[str, int]:
    nb_joueurs = len(
        game.players
    )

    notes = {}

    for nom, plan in PLANS.items():
        if nom == exclure:
            continue

        # Plan impossible si une carte
        # indispensable manque dans
        # la réserve.
        if any(
            quantite_stock(
                game,
                carte,
            ) <= 0
            for carte
            in plan["requis"]
        ):
            continue

        notes[nom] = (
            plan["note"]
            + plan.get(
                "ajustement_joueurs",
                {},
            ).get(
                nb_joueurs,
                0,
            )
        )

    return notes


def meilleur_plan(
    notes: dict[str, int],
) -> str:
    if not notes:
        return PLAN_PAR_DEFAUT

    # En cas d'égalité, l'ordre de
    # PLANS dans config.py départage.
    return max(
        notes,
        key=notes.get,
    )


def raison_changement(
    game: Game,
    etat: dict[str, Any],
    plan: str,
) -> str | None:
    carte_cle = PLANS.get(
        plan,
        {},
    ).get(
        "carte_cle"
    )

    # Déclencheur 1 :
    # la carte clé n'est plus disponible
    # et on n'en a jamais obtenu.
    if (
        carte_cle is not None
        and quantite_stock(
            game,
            carte_cle,
        ) <= 0
        and etat[
            "cartes_achetees"
        ].get(
            carte_cle,
            0,
        ) == 0
    ):
        return f"pile_{carte_cle}_vide"

    # Déclencheur 2 :
    # plan Witch sans Curses à donner.
    if (
        plan == "WITCH_MONEY"
        and curses_restantes(
            game
        ) <= 0
    ):
        return "curses_epuisees"

    return None


def verifier_changement(
    game: Game,
    etat: dict[str, Any],
) -> None:
    tour = etat["tour"]

    if (
        etat.get(
            "changement_plan"
        ) is not None
        or tour
        > TOUR_MAX_CHANGEMENT_PLAN
        or etat.get(
            "plan_verifie_tour"
        ) == tour
    ):
        return

    etat[
        "plan_verifie_tour"
    ] = tour

    plan = etat[
        "strategie_actuelle"
    ]

    raison = raison_changement(
        game,
        etat,
        plan,
    )

    if raison is None:
        return

    nouveau = meilleur_plan(
        noter_plans(
            game,
            exclure=plan,
        )
    )

    etat[
        "changement_plan"
    ] = {
        "tour": tour,
        "de": plan,
        "vers": nouveau,
        "raison": raison,
    }

    etat[
        "strategie_actuelle"
    ] = nouveau


def plan_actuel(
    game: Game,
    game_id: str,
) -> str:
    etat = obtenir_etat(
        game_id
    )

    if etat.get(
        "plan_initial"
    ) is None:
        plan = meilleur_plan(
            noter_plans(
                game
            )
        )

        etat[
            "plan_initial"
        ] = plan

        etat[
            "strategie_actuelle"
        ] = plan

    verifier_changement(
        game,
        etat,
    )

    return etat[
        "strategie_actuelle"
    ]


def bonus_carte_cle(
    game_id: str,
    nom: str,
) -> int:
    etat = obtenir_etat(
        game_id
    )

    # En fin de partie, plus de bonus :
    # un Duchy doit passer devant la
    # carte clé.
    provinces = etat.get(
        "provinces_restantes"
    )

    nb_joueurs = etat.get(
        "nb_joueurs"
    ) or 2

    if (
        provinces is not None
        and provinces
        <= nb_joueurs + 2
    ):
        return 0

    carte_cle = PLANS.get(
        etat.get(
            "strategie_actuelle"
        ),
        {},
    ).get(
        "carte_cle"
    )

    if (
        nom == carte_cle
        and etat[
            "cartes_achetees"
        ].get(
            nom,
            0,
        ) == 0
    ):
        return BONUS_CARTE_CLE

    return 0
