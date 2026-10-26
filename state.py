import threading
from typing import Any

from config import EFFETS_ACTIONS


etat_tours: dict[str, dict[str, Any]] = {}

_verrous_parties: dict[str, threading.RLock] = {}
_verrou_registre = threading.Lock()


def verrou_partie(game_id: str) -> threading.RLock:
    with _verrou_registre:
        return _verrous_parties.setdefault(
            game_id,
            threading.RLock(),
        )


def nouvel_etat_partie() -> dict[str, Any]:
    return {
        "tour": 0,
        "actions_restantes": 1,
        "achats_restants": 1,
        "bonus_pieces": 0,
        "argent_restant": None,
        "phase_achat": False,
        "cartes_achetees": {},
    }


def initialiser_partie(game_id: str) -> None:
    with verrou_partie(game_id):
        etat_tours[game_id] = nouvel_etat_partie()


def obtenir_etat(game_id: str) -> dict[str, Any]:
    with verrou_partie(game_id):
        return etat_tours.setdefault(
            game_id,
            nouvel_etat_partie(),
        )


def demarrer_tour(game_id: str) -> dict[str, Any]:
    with verrou_partie(game_id):
        etat = obtenir_etat(game_id)

        etat["tour"] += 1
        etat["actions_restantes"] = 1
        etat["achats_restants"] = 1
        etat["bonus_pieces"] = 0
        etat["argent_restant"] = None
        etat["phase_achat"] = False

        return etat


def enregistrer_achat(
    game_id: str,
    nom_carte: str,
) -> None:

    with verrou_partie(game_id):
        etat = obtenir_etat(game_id)

        etat["cartes_achetees"][nom_carte] = (
            etat["cartes_achetees"].get(nom_carte, 0)
            + 1
        )


def nombre_carte_achetee(
    game_id: str,
    nom_carte: str,
) -> int:

    with verrou_partie(game_id):
        return obtenir_etat(game_id)[
            "cartes_achetees"
        ].get(nom_carte, 0)


def nombre_total_actions_achetees(
    game_id: str,
) -> int:

    with verrou_partie(game_id):
        etat = obtenir_etat(game_id)

        return sum(
            etat["cartes_achetees"].get(nom, 0)
            for nom in EFFETS_ACTIONS
        )


def supprimer_partie(game_id: str) -> None:
    with verrou_partie(game_id):
        etat_tours.pop(game_id, None)

    with _verrou_registre:
        _verrous_parties.pop(game_id, None)