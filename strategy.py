from dopynion.cards import Card
from dopynion.data_model import (
    CardName,
    Game,
)

from config import (
    EFFETS_ACTIONS,
    GAINS_ACTIONS,
    MAX_CARTES_ACTION,
    POIDS_MINIMUM_ACHAT,
    PRIORITE_ACTION,
    PRIORITE_DEPARTAGE,
)
from deck import enregistrer_carte_retiree
from game_utils import (
    calculer_argent_main,
    quantite_stock,
    trouver_mon_joueur,
)
from plans import plan_actuel
from state import (
    enregistrer_gain_estime,
    nombre_total_actions,
    obtenir_etat,
    quantite_achetee,
)
from weights import (
    calculer_poids_achat,
    max_total_actions_dynamique,
)


def choisir_action(
    game: Game,
    game_id: str,
) -> CardName | None:
    etat = obtenir_etat(
        game_id
    )

    if (
        etat["phase_achat"]
        or etat["actions_restantes"] <= 0
    ):
        return None

    moi = trouver_mon_joueur(
        game
    )

    if (
        moi is None
        or moi.hand is None
    ):
        return None

    for nom in PRIORITE_ACTION:
        for carte, quantite in (
            moi.hand.quantities.items()
        ):
            if (
                quantite > 0
                and carte == nom
                and Card.class_(
                    carte
                ).is_action
            ):
                return carte

    return None


def appliquer_effet_action(
    game: Game,
    game_id: str,
    carte: CardName,
) -> None:
    etat = obtenir_etat(
        game_id
    )

    nom = str(carte)

    effet = EFFETS_ACTIONS.get(
        nom,
        {
            "actions": 0,
            "achats": 0,
            "pieces": 0,
        },
    )

    etat[
        "actions_restantes"
    ] += (
        effet["actions"] - 1
    )

    etat[
        "achats_restants"
    ] += effet["achats"]

    etat[
        "bonus_pieces"
    ] += effet["pieces"]

    # Dans Dopynion, une Hireling jouée
    # quitte définitivement le deck.
    if nom == "hireling":
        enregistrer_carte_retiree(
            game_id,
            nom,
        )

    for nom_gain, quantite in (
        GAINS_ACTIONS.get(
            nom,
            {},
        ).items()
    ):
        disponible = quantite_stock(
            game,
            nom_gain,
        )

        if disponible <= 0:
            continue

        enregistrer_gain_estime(
            game_id,
            nom_gain,
            min(
                quantite,
                disponible,
            ),
        )


def commencer_phase_achat(
    game: Game,
    game_id: str,
) -> None:
    etat = obtenir_etat(
        game_id
    )

    if etat["phase_achat"]:
        return

    etat[
        "argent_restant"
    ] = (
        calculer_argent_main(
            game
        )
        + etat["bonus_pieces"]
    )

    etat[
        "phase_achat"
    ] = True


def carte_action_autorisee(
    game: Game,
    game_id: str,
    nom: str,
) -> bool:
    limite = MAX_CARTES_ACTION.get(
        nom,
        0,
    )

    if limite <= 0:
        return False

    if (
        quantite_achetee(
            game_id,
            nom,
        )
        >= limite
    ):
        return False

    return (
        nombre_total_actions(
            game_id
        )
        < max_total_actions_dynamique(
            game,
            game_id,
        )
    )


def choisir_achat(
    game: Game,
    game_id: str,
) -> CardName | None:
    etat = obtenir_etat(
        game_id
    )

    if (
        etat["achats_restants"] <= 0
        or etat["argent_restant"]
        is None
    ):
        return None

    interdits = {
        "copper",
        "curse",
    }

    departage = {
        nom: index
        for index, nom
        in enumerate(
            PRIORITE_DEPARTAGE
        )
    }

    candidats = []
    evaluations = {}
    strategie = None

    for carte, quantite in (
        game.stock.quantities.items()
    ):
        if quantite <= 0:
            continue

        nom = str(carte)

        if nom in interdits:
            continue

        classe = Card.class_(
            carte
        )

        if (
            classe.cost
            > etat["argent_restant"]
        ):
            continue

        # Plan calculé une seule fois,
        # dès qu'une carte est achetable.
        if strategie is None:
            strategie = plan_actuel(
                game,
                game_id,
            )

        if (
            classe.is_action
            and not carte_action_autorisee(
                game,
                game_id,
                nom,
            )
        ):
            continue

        evaluation = (
            calculer_poids_achat(
                game,
                game_id,
                nom,
                strategie,
            )
        )

        evaluations[
            nom
        ] = evaluation

        candidats.append(
            (
                evaluation["total"],
                -departage.get(
                    nom,
                    999,
                ),
                carte,
            )
        )

    # Le plan (etat["strategie_actuelle"])
    # est tenu à jour par plan_actuel().
    etat[
        "derniere_evaluation_achat"
    ] = evaluations

    if not candidats:
        return None

    candidats.sort(
        key=lambda item: (
            item[0],
            item[1],
        ),
        reverse=True,
    )

    meilleur = candidats[0]

    if (
        meilleur[0]
        < POIDS_MINIMUM_ACHAT
    ):
        return None

    return meilleur[2]