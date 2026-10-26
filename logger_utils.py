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


#####################################################
# Configuration des logs
#####################################################

DOSSIER_LOGS = Path(__file__).resolve().parent / "logs"
DOSSIER_LOGS.mkdir(exist_ok=True)

MAX_PARTIES_LOGS = 500

# RLock permet à une fonction de logs d'appeler
# une autre fonction utilisant le même verrou.
_verrou_logs = threading.RLock()


#####################################################
# Utilitaires
#####################################################


def maintenant() -> str:
    return datetime.now().isoformat(
        timespec="seconds"
    )


def nom_fichier_game(game_id: str) -> str:
    """
    Transforme le game_id en nom de fichier sûr.
    """

    propre = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        str(game_id),
    )

    return propre + ".json"


def chemin_log(game_id: str) -> Path:
    return (
        DOSSIER_LOGS
        / nom_fichier_game(game_id)
    )


#####################################################
# Historique des parties
#####################################################


def initialiser_historique(
    game_id: str,
) -> None:
    """
    Crée le fichier d'historique d'une nouvelle partie.
    """

    fichier = chemin_log(game_id)

    historique = {
        "game_id": game_id,
        "debut": maintenant(),
        "fin": None,
        "situations": [],
    }

    with _verrou_logs:

        fichier.write_text(
            json.dumps(
                historique,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        nettoyer_anciens_logs()


def charger_historique(
    game_id: str,
) -> dict[str, Any]:
    """
    Charge l'historique d'une partie.
    Si le fichier n'existe pas, il est créé.
    """

    fichier = chemin_log(game_id)

    if not fichier.exists():
        return {
            "game_id": game_id,
            "debut": maintenant(),
            "fin": None,
            "situations": [],
        }

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
        return {
            "game_id": game_id,
            "debut": maintenant(),
            "fin": None,
            "situations": [],
        }


def enregistrer_situation(
    game_id: str,
    situation: dict[str, Any],
) -> None:
    """
    Ajoute une situation à l'historique de la partie.
    """

    fichier = chemin_log(game_id)

    situation = {
        "horodatage": maintenant(),
        **situation,
    }

    with _verrou_logs:

        historique = charger_historique(
            game_id
        )

        historique.setdefault(
            "situations",
            [],
        )

        historique["situations"].append(
            situation
        )

        fichier.write_text(
            json.dumps(
                historique,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        nettoyer_anciens_logs()


def terminer_historique(
    game_id: str,
) -> None:
    """
    Marque la partie comme terminée.
    """

    fichier = chemin_log(game_id)

    with _verrou_logs:

        historique = charger_historique(
            game_id
        )

        historique["fin"] = maintenant()

        fichier.write_text(
            json.dumps(
                historique,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        nettoyer_anciens_logs()


#####################################################
# Maximum 10 parties
#####################################################


def nettoyer_anciens_logs() -> None:
    """
    Conserve seulement les 10 parties les plus récentes.

    Le classement utilise la date de début enregistrée
    dans chaque fichier et non sa dernière modification.
    """

    with _verrou_logs:

        fichiers = list(
            DOSSIER_LOGS.glob("*.json")
        )

        if len(fichiers) <= MAX_PARTIES_LOGS:
            return

        parties = []

        for fichier in fichiers:

            try:
                contenu = json.loads(
                    fichier.read_text(
                        encoding="utf-8"
                    )
                )

                debut = contenu.get(
                    "debut",
                    "",
                )

            except (
                json.JSONDecodeError,
                OSError,
            ):
                debut = ""

            parties.append(
                (
                    debut,
                    fichier,
                )
            )

        # Plus récente en premier.
        parties.sort(
            key=lambda element: element[0],
            reverse=True,
        )

        # On supprime tout ce qui dépasse les 10 parties.
        for _, fichier in parties[
            MAX_PARTIES_LOGS:
        ]:
            try:
                fichier.unlink()

                print(
                    f">>> Ancien log supprimé : "
                    f"{fichier.name}",
                    flush=True,
                )

            except FileNotFoundError:
                pass


#####################################################
# Affichage / sauvegarde d'une situation
#####################################################


def afficher_situation(
    game: Game,
    game_id: str,
) -> None:

    moi = trouver_mon_joueur(game)
    etat = obtenir_etat(game_id)

    situation: dict[str, Any] = {
        "tour": etat["tour"],
    }

    print(
        "------------- SITUATION -------------"
    )

    #################################################
    # Notre joueur
    #################################################

    if moi is not None and moi.hand is not None:

        main = moi.hand.quantities

        argent_tresor = calculer_argent_main(
            game
        )

        if etat["argent_restant"] is None:
            argent_dispo = (
                argent_tresor
                + etat["bonus_pieces"]
            )
        else:
            argent_dispo = etat[
                "argent_restant"
            ]

        actions = [
            carte.value
            for carte, quantite in main.items()
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
            f"Tour          : "
            f"{etat['tour']}"
        )

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
            f"Argent trésor : "
            f"{argent_tresor}"
        )

        print(
            f"Bonus pièces  : "
            f"{etat['bonus_pieces']}"
        )

        print(
            f"Argent dispo  : "
            f"{argent_dispo}"
        )

        print(
            f"Actions dispo : "
            f"{etat['actions_restantes']}"
        )

        print(
            f"Achats dispo  : "
            f"{etat['achats_restants']}"
        )

        print(
            f"Phase achat   : "
            f"{etat['phase_achat']}"
        )

        print(
            f"Cartes action : "
            f"{actions or 'aucune'}"
        )

        print(
            f"Provinces     : "
            f"{provinces_restantes(game)}"
        )

        print(
            f"Curses        : "
            f"{curses_restantes(game)}"
        )

        print(
            f"Piles vides   : "
            f"{nombre_piles_vides(game)}"
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

                "provinces_restantes":
                    provinces_restantes(game),

                "curses_restantes":
                    curses_restantes(game),

                "piles_vides":
                    nombre_piles_vides(game),
            }
        )


    #################################################
    # Scores
    #################################################

    print("Scores :")

    scores = {}

    for joueur in game.players:

        scores[joueur.name] = joueur.score

        print(
            f"   - {joueur.name:<20} "
            f"{joueur.score}"
        )


    #################################################
    # Réserve
    #################################################

    print("Réserve :")

    reserve = {}

    for carte, quantite in game.stock.quantities.items():

        infos = Card.class_(carte)

        reserve[carte.value] = {
            "quantite": quantite,
            "cout": infos.cost,
        }

        print(
            f"   - {carte.value:<15} "
            f"x{quantite:<3} "
            f"(coût {infos.cost})"
        )


    #################################################
    # Fin de situation
    #################################################

    print(
        f"Partie finie : "
        f"{game.finished}"
    )

    print(
        "-------------------------------------",
        flush=True,
    )

    situation.update(
        {
            "scores": scores,
            "reserve": reserve,
            "partie_finie": game.finished,
        }
    )

    enregistrer_situation(
        game_id,
        situation,
    )