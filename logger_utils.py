import json
import re
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from dopynion.cards import Card
from dopynion.data_model import Game

from game_utils import (
    calculer_argent_main,
    curses_restantes,
    nombre_piles_vides,
    provinces_restantes,
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
        "situations": [],
    }


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

    mon_score = scores[mon_joueur]

    return mon_score == max(
        scores.values()
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
    with _verrou_logs:
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


def initialiser_historique(
    game_id: str,
) -> None:
    historique = {
        "game_id": game_id,
        "debut": maintenant(),
        "fin": None,
        "resultat": None,
        "situations": [],
    }

    with _verrou_logs:
        chemin_temporaire(
            game_id
        ).write_text(
            json.dumps(
                historique,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


def enregistrer_situation(
    game_id: str,
    situation: dict[str, Any],
) -> None:
    with _verrou_logs:
        historique = charger_historique(
            game_id
        )

        historique["situations"].append(
            {
                "horodatage": maintenant(),
                **situation,
            }
        )

        chemin_temporaire(
            game_id
        ).write_text(
            json.dumps(
                historique,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
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
            "V" if victoire else "D"
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
            f">>> Log final : {final.name}",
            flush=True,
        )


def afficher_situation(
    game: Game,
    game_id: str,
) -> None:
    moi = trouver_mon_joueur(game)
    etat = obtenir_etat(game_id)

    situation: dict[str, Any] = {
        "tour": etat["tour"],
        "partie_finie": game.finished,
        "scores": {
            joueur.name: joueur.score
            for joueur in game.players
        },
        "reserve": {
            carte.value: {
                "quantite": quantite,
                "cout": Card.class_(carte).cost,
            }
            for carte, quantite
            in game.stock.quantities.items()
        },
        "provinces_restantes":
            provinces_restantes(game),
        "curses_restantes":
            curses_restantes(game),
        "piles_vides":
            nombre_piles_vides(game),
    }

    print(
        "------------- SITUATION -------------"
    )

    print(
        f"Tour          : "
        f"{etat['tour']}"
    )

    if moi is not None and moi.hand is not None:
        main = moi.hand.quantities

        argent_tresor = calculer_argent_main(
            game
        )

        argent_dispo = (
            etat["argent_restant"]
            if etat["argent_restant"] is not None
            else argent_tresor
            + etat["bonus_pieces"]
        )

        actions = [
            carte.value
            for carte, quantite
            in main.items()
            if (
                quantite > 0
                and Card.class_(carte).is_action
            )
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

        print(
            f"Joueur        : "
            f"{moi.name} "
            f"(score {moi.score})"
        )

        print(
            f"Cartes en main: "
            f"{sum(main.values())}"
        )

        for carte, quantite in main.items():
            infos = Card.class_(carte)

            print(
                f"   - {quantite} x "
                f"{carte.value:<15} "
                f"(argent {infos.money}, "
                f"coût {infos.cost})"
            )

        print(
            f"Argent trésor : {argent_tresor}"
        )
        print(
            f"Bonus pièces  : {etat['bonus_pieces']}"
        )
        print(
            f"Argent dispo  : {argent_dispo}"
        )
        print(
            f"Actions dispo : {etat['actions_restantes']}"
        )
        print(
            f"Achats dispo  : {etat['achats_restants']}"
        )
        print(
            f"Phase achat   : {etat['phase_achat']}"
        )
        print(
            f"Cartes action : {actions or 'aucune'}"
        )
        print(
            f"Je peux acheter : "
            f"{achetables or 'rien'}"
        )

        situation.update(
            {
                "joueur": moi.name,
                "score": moi.score,
                "main": {
                    carte.value: quantite
                    for carte, quantite
                    in main.items()
                },
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
                    dict(
                        etat["cartes_achetees"]
                    ),
                "achetables":
                    achetables,
            }
        )

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
            f"(coût "
            f"{Card.class_(carte).cost})"
        )

    print(
        f"Partie finie : {game.finished}"
    )

    print(
        "-------------------------------------",
        flush=True,
    )

    enregistrer_situation(
        game_id,
        situation,
    )