import json
import re
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from dopynion.data_model import Game

from game_utils import (
    calculer_argent_main,
    nombre_piles_vides,
    trouver_mon_joueur,
)
from state import obtenir_etat


DOSSIER_LOGS = Path(__file__).resolve().parent / "logs"
DOSSIER_LOGS.mkdir(exist_ok=True)

MAX_PARTIES_LOGS = 300
_verrou_logs = threading.RLock()


def maintenant() -> str:
    return datetime.now().astimezone().isoformat(
        timespec="seconds"
    )


def nom_temporaire(game_id: str) -> str:
    propre = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        str(game_id),
    )
    return f"game_{propre}.json"


def chemin_temporaire(game_id: str) -> Path:
    return DOSSIER_LOGS / nom_temporaire(game_id)


def sauvegarder(
    game_id: str,
    historique: dict[str, Any],
) -> None:
    chemin_temporaire(game_id).write_text(
        json.dumps(
            historique,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def charger_historique(
    game_id: str,
) -> dict[str, Any]:
    fichier = chemin_temporaire(game_id)

    if fichier.exists():
        try:
            return json.loads(
                fichier.read_text(
                    encoding="utf-8"
                )
            )
        except (
            json.JSONDecodeError,
            OSError,
        ):
            pass

    return {
        "game_id": game_id,
        "debut": maintenant(),
        "fin": None,
        "resultat": None,
        "nb_joueurs": None,
        "situations": [],
    }


def initialiser_historique(
    game_id: str,
) -> None:
    historique = {
        "game_id": game_id,
        "debut": maintenant(),
        "fin": None,
        "resultat": None,
        "nb_joueurs": None,
        "situations": [],
    }

    with _verrou_logs:
        sauvegarder(
            game_id,
            historique,
        )


def est_victoire(
    historique: dict[str, Any],
) -> bool:
    situations = historique.get(
        "situations",
        [],
    )

    if not situations:
        return False

    derniere = situations[-1]
    scores = derniere.get(
        "scores",
        {},
    )

    mon_joueur = derniere.get(
        "joueur"
    )

    if (
        not scores
        or mon_joueur not in scores
    ):
        return False

    return (
        scores[mon_joueur]
        == max(scores.values())
    )


def nom_final(
    historique: dict[str, Any],
    victoire: bool,
) -> str:
    try:
        debut = datetime.fromisoformat(
            historique["debut"]
        )
    except (
        ValueError,
        TypeError,
        KeyError,
    ):
        debut = datetime.now().astimezone()

    prefixe = debut.strftime("%m%d%H%M")
    resultat = "V" if victoire else "D"

    game_id = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        str(
            historique.get(
                "game_id",
                "unknown",
            )
        ),
    )

    return (
        f"{prefixe}"
        f"{resultat}_"
        f"{game_id}.json"
    )


def nettoyer_anciens_logs() -> None:
    fichiers = [
        fichier
        for fichier
        in DOSSIER_LOGS.glob("*.json")
        if not fichier.name.startswith(
            "game_"
        )
    ]

    if len(fichiers) <= MAX_PARTIES_LOGS:
        return

    fichiers.sort(
        key=lambda fichier:
            fichier.stat().st_mtime,
        reverse=True,
    )

    for fichier in fichiers[
        MAX_PARTIES_LOGS:
    ]:
        try:
            fichier.unlink()
        except FileNotFoundError:
            pass


def afficher_situation(
    game: Game,
    game_id: str,
) -> None:
    moi = trouver_mon_joueur(game)

    if moi is None:
        return

    etat = obtenir_etat(game_id)

    stock = {
        carte.value.lower(): quantite
        for carte, quantite
        in game.stock.quantities.items()
    }

    piles_basses = sorted(
        stock.items(),
        key=lambda item: item[1],
    )[:3]

    argent = calculer_argent_main(
        game
    ) + etat["bonus_pieces"]

    situation = {
        "tour": etat["tour"],
        "partie_finie": game.finished,
        "joueur": moi.name,
        "score": moi.score,
        "scores": {
            joueur.name: joueur.score
            for joueur in game.players
        },
        "main": (
            {
                carte.value: quantite
                for carte, quantite
                in moi.hand.quantities.items()
            }
            if moi.hand is not None
            else {}
        ),
        "argent": argent,
        "actions_restantes":
            etat["actions_restantes"],
        "achats_restants":
            etat["achats_restants"],
        "cartes_achetees":
            dict(etat["cartes_achetees"]),
        "stock": {
            nom: stock.get(nom, 0)
            for nom in (
                "province",
                "duchy",
                "estate",
                "gold",
                "silver",
                "curse",
            )
        },
        "piles_vides":
            nombre_piles_vides(game),
        "piles_basses":
            piles_basses,
    }

    with _verrou_logs:
        historique = charger_historique(
            game_id
        )

        historique["nb_joueurs"] = len(
            game.players
        )

        situations = historique[
            "situations"
        ]

        if (
            situations
            and situations[-1]["tour"]
            == etat["tour"]
        ):
            decisions = situations[-1].get(
                "decisions",
                [],
            )

            situation["decisions"] = decisions
            situations[-1] = situation

        else:
            situation["decisions"] = []
            situations.append(
                situation
            )

        sauvegarder(
            game_id,
            historique,
        )

    print(
        f">>> T{etat['tour']} "
        f"| score={moi.score} "
        f"| argent={argent} "
        f"| achats={etat['cartes_achetees']}",
        flush=True,
    )


def enregistrer_decision(
    game_id: str,
    tour: int,
    decision: str,
) -> None:
    with _verrou_logs:
        historique = charger_historique(
            game_id
        )

        situations = historique.get(
            "situations",
            [],
        )

        if not situations:
            return

        situation = situations[-1]

        if situation.get("tour") != tour:
            return

        decisions = situation.setdefault(
            "decisions",
            [],
        )

        if (
            not decisions
            or decisions[-1] != decision
        ):
            decisions.append(
                decision
            )

        sauvegarder(
            game_id,
            historique,
        )


def terminer_historique(
    game_id: str,
) -> None:
    with _verrou_logs:
        temporaire = chemin_temporaire(
            game_id
        )

        historique = charger_historique(
            game_id
        )

        victoire = est_victoire(
            historique
        )

        historique["fin"] = maintenant()
        historique["resultat"] = (
            "V"
            if victoire
            else "D"
        )

        final = (
            DOSSIER_LOGS
            / nom_final(
                historique,
                victoire,
            )
        )

        final.write_text(
            json.dumps(
                historique,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        if temporaire.exists():
            temporaire.unlink()

        nettoyer_anciens_logs()

        print(
            f">>> Log final : "
            f"{final.name}",
            flush=True,
        )