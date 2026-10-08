import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from dopynion.cards import Card
from dopynion.data_model import Game

from game_utils import (
    calculer_argent_main,
    provinces_restantes,
    trouver_mon_joueur,
)
from state import obtenir_etat


FICHIER_LOGS = (
    Path(__file__).resolve().parent
    / "logs.json"
)

_verrou_logs = threading.Lock()


def ecrire_situation(
    situation: dict[str, Any],
) -> None:

    situation = {
        "horodatage": datetime.now().isoformat(
            timespec="seconds"
        ),
        **situation,
    }

    with _verrou_logs:
        FICHIER_LOGS.write_text(
            json.dumps(
                situation,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


def afficher_situation(
    game: Game,
    game_id: str,
) -> None:

    moi = trouver_mon_joueur(game)
    etat = obtenir_etat(game_id)

    situation: dict[str, Any] = {
        "partie": game_id,
        "tour": etat["tour"],
    }

    print("------------- SITUATION -------------")

    if moi is not None and moi.hand is not None:

        main = moi.hand.quantities
        nb_cartes = sum(main.values())

        argent_tresor = calculer_argent_main(game)

        if etat["argent_restant"] is None:
            argent_dispo = (
                argent_tresor
                + etat["bonus_pieces"]
            )
        else:
            argent_dispo = (
                etat["argent_restant"]
            )

        actions = [
            carte.value
            for carte in main
            if Card.class_(carte).is_action
        ]

        achetables = [
            carte.value
            for carte, quantite
            in game.stock.quantities.items()
            if (
                quantite > 0
                and Card.class_(carte).cost
                <= argent_dispo
                and etat["achats_restants"] > 0
            )
        ]

        print(f"Tour          : {etat['tour']}")
        print(f"Joueur        : {moi.name} (score {moi.score})")
        print(f"Cartes en main: {nb_cartes}")

        for carte, quantite in main.items():

            infos = Card.class_(carte)

            print(
                f"   - {quantite} x "
                f"{carte.value:<15} "
                f"(argent {infos.money}, coût {infos.cost})"
            )

        print(f"Argent trésor : {argent_tresor}")
        print(f"Bonus pièces  : {etat['bonus_pieces']}")
        print(f"Argent dispo  : {argent_dispo}")
        print(f"Actions dispo : {etat['actions_restantes']}")
        print(f"Achats dispo  : {etat['achats_restants']}")
        print(f"Phase achat   : {etat['phase_achat']}")
        print(f"Cartes action : {actions or 'aucune'}")
        print(f"Je peux acheter : {achetables or 'rien'}")

        situation.update(
            {
                "joueur": moi.name,
                "score": moi.score,

                "nb_cartes_en_main":
                    nb_cartes,

                "main": [
                    {
                        "carte": carte.value,
                        "quantite": quantite,
                        "argent":
                            Card.class_(carte).money,
                        "cout":
                            Card.class_(carte).cost,
                    }
                    for carte, quantite
                    in main.items()
                ],

                "argent_tresor":
                    argent_tresor,

                "bonus_pieces":
                    etat["bonus_pieces"],

                "argent_dispo":
                    argent_dispo,

                "argent_restant":
                    etat["argent_restant"],

                "actions_restantes":
                    etat["actions_restantes"],

                "achats_restants":
                    etat["achats_restants"],

                "phase_achat":
                    etat["phase_achat"],

                "cartes_action":
                    actions,

                "cartes_achetees":
                    etat["cartes_achetees"],

                "achetables":
                    achetables,

                "provinces_restantes":
                    provinces_restantes(game),
            }
        )

    else:
        print(
            "Ma main n'a pas été trouvée."
        )

        situation["main"] = None

    print("Scores :")

    for joueur in game.players:
        print(
            f"   - {joueur.name:<20} "
            f"{joueur.score}"
        )

    print("Réserve :")

    for carte, quantite in game.stock.quantities.items():
        print(
            f"   - {carte.value:<15} "
            f"x{quantite:<3} "
            f"(coût {Card.class_(carte).cost})"
        )

    print(f"Partie finie : {game.finished}")
    print("-------------------------------------", flush=True)

    situation.update(
        {
            "scores": {
                joueur.name: joueur.score
                for joueur in game.players
            },

            "reserve": {
                carte.value: {
                    "quantite": quantite,
                    "cout":
                        Card.class_(carte).cost,
                }
                for carte, quantite
                in game.stock.quantities.items()
            },

            "partie_finie":
                game.finished,
        }
    )

    ecrire_situation(situation)