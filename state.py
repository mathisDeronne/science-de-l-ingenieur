import threading
from typing import Any

from config import EFFETS_ACTIONS


etat_tours: dict[str, dict[str, Any]] = {}

_verrous_parties: dict[
    str,
    threading.RLock,
] = {}

_verrou_registre = threading.Lock()


def verrou_partie(
    game_id: str,
) -> threading.RLock:
    # Chemin rapide :
    # pas de verrou global si le verrou
    # de cette partie existe déjà.
    verrou = _verrous_parties.get(
        game_id
    )

    if verrou is not None:
        return verrou

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
        "gains_estimes": {},

        "strategie_actuelle": None,

        # Plan de partie (voir plans.py)
        "plan_initial": None,
        "changement_plan": None,
        "plan_verifie_tour": 0,

        # Suivi de la partie (voir deck.py)
        # Piles présentes au premier /play :
        # Dopynion retire les piles vides de
        # la réserve envoyée.
        "piles_initiales": None,
        # Cartes sorties de notre deck
        # (Hireling jouée).
        "cartes_retirees": {},
        # Déduit de notre score exact.
        "curses_recues": 0,
        "deck_coherent": True,
        # Dernières valeurs vues, pour les
        # callbacks sans état de partie
        # (Chancellor).
        "provinces_restantes": None,
        "nb_joueurs": None,
        "derniere_evaluation_achat": {},
    }


def initialiser_partie(
    game_id: str,
) -> None:
    with verrou_partie(game_id):
        etat_tours[game_id] = (
            nouvel_etat_partie()
        )


def obtenir_etat(
    game_id: str,
) -> dict[str, Any]:
    with verrou_partie(game_id):
        return etat_tours.setdefault(
            game_id,
            nouvel_etat_partie(),
        )


def demarrer_tour(
    game_id: str,
) -> dict[str, Any]:
    with verrou_partie(game_id):
        etat = obtenir_etat(
            game_id
        )

        etat["tour"] += 1
        etat["actions_restantes"] = 1
        etat["achats_restants"] = 1
        etat["bonus_pieces"] = 0

        etat["argent_restant"] = None
        etat["phase_achat"] = False

        etat[
            "derniere_evaluation_achat"
        ] = {}

        return etat


def enregistrer_achat(
    game_id: str,
    nom_carte: str,
) -> None:
    with verrou_partie(game_id):
        etat = obtenir_etat(
            game_id
        )

        achats = etat[
            "cartes_achetees"
        ]

        achats[nom_carte] = (
            achats.get(
                nom_carte,
                0,
            )
            + 1
        )


def enregistrer_gain_estime(
    game_id: str,
    nom_carte: str,
    quantite: int = 1,
) -> None:
    with verrou_partie(game_id):
        etat = obtenir_etat(
            game_id
        )

        gains = etat[
            "gains_estimes"
        ]

        gains[nom_carte] = (
            gains.get(
                nom_carte,
                0,
            )
            + quantite
        )


def quantite_achetee(
    game_id: str,
    nom_carte: str,
) -> int:
    return obtenir_etat(
        game_id
    )["cartes_achetees"].get(
        nom_carte,
        0,
    )


def quantite_gain_estime(
    game_id: str,
    nom_carte: str,
) -> int:
    return obtenir_etat(
        game_id
    )["gains_estimes"].get(
        nom_carte,
        0,
    )


def quantite_economique(
    game_id: str,
    nom_carte: str,
) -> int:
    # Achetées + gagnées par nos actions
    # (Bandit -> Gold, Bureaucrat -> Silver).
    return (
        quantite_achetee(
            game_id,
            nom_carte,
        )
        + quantite_gain_estime(
            game_id,
            nom_carte,
        )
    )


def nombre_total_actions(
    game_id: str,
) -> int:
    return sum(
        quantite_achetee(
            game_id,
            nom,
        )
        for nom
        in EFFETS_ACTIONS
    )


def supprimer_partie(
    game_id: str,
) -> None:
    with verrou_partie(game_id):
        etat_tours.pop(
            game_id,
            None,
        )