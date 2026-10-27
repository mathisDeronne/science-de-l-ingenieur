from __future__ import annotations

import json
import os
import re
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

import config
from dopynion.data_model import Game

from game_utils import (
    calculer_argent_main,
    nombre_piles_vides,
    trouver_mon_joueur,
)
from state import obtenir_etat


# ============================================================
# CONFIGURATION
# ============================================================

MAX_LOGS = 500
TAILLE_RESUME = 100

# Change cette valeur à chaque grosse version stratégique.
VERSION_STRATEGIE = getattr(
    config,
    "VERSION_STRATEGIE",
    "noncumul-v1",
)


# ============================================================
# CHEMINS ABSOLUS
# ============================================================
#
# Important :
# on ne dépend plus du dossier courant utilisé par FastAPI /
# Alwaysdata.
#
# Les logs seront TOUJOURS créés à côté de logger_utils.py :
#
# projet/
# ├── logger_utils.py
# └── logs/
#     └── resumes/
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DOSSIER_LOGS = BASE_DIR / "logs"
DOSSIER_RESUMES = DOSSIER_LOGS / "resumes"

FICHIER_STATS = DOSSIER_LOGS / "_stats.json"

DOSSIER_LOGS.mkdir(
    parents=True,
    exist_ok=True,
)

DOSSIER_RESUMES.mkdir(
    parents=True,
    exist_ok=True,
)


print(
    "[LOGGER INIT]",
    {
        "pid": os.getpid(),
        "cwd": os.getcwd(),
        "base_dir": str(BASE_DIR),
        "logs": str(DOSSIER_LOGS),
        "resumes": str(DOSSIER_RESUMES),
        "writable": os.access(
            DOSSIER_LOGS,
            os.W_OK,
        ),
        "version_strategie": VERSION_STRATEGIE,
    },
    flush=True,
)


# ============================================================
# MÉMOIRE
# ============================================================

_historiques: dict[str, dict[str, Any]] = {}

_verrou_logs = threading.RLock()


# ============================================================
# OUTILS
# ============================================================

def maintenant_iso() -> str:
    return datetime.now().astimezone().isoformat(
        timespec="seconds"
    )


def nom_carte(carte: Any) -> str:
    """
    Convertit CardName / Enum / str vers un nom lowercase.
    """

    valeur = getattr(
        carte,
        "value",
        carte,
    )

    return str(valeur).lower()


def rendre_json_serialisable(
    valeur: Any,
) -> Any:
    """
    Rend récursivement une valeur sérialisable en JSON.
    """

    if valeur is None:
        return None

    if isinstance(
        valeur,
        (
            str,
            int,
            float,
            bool,
        ),
    ):
        return valeur

    if isinstance(
        valeur,
        Path,
    ):
        return str(valeur)

    if isinstance(
        valeur,
        dict,
    ):
        return {
            str(
                getattr(
                    cle,
                    "value",
                    cle,
                )
            ): rendre_json_serialisable(
                contenu
            )
            for cle, contenu
            in valeur.items()
        }

    if isinstance(
        valeur,
        (
            list,
            tuple,
            set,
        ),
    ):
        return [
            rendre_json_serialisable(
                element
            )
            for element
            in valeur
        ]

    enum_value = getattr(
        valeur,
        "value",
        None,
    )

    if enum_value is not None:
        return rendre_json_serialisable(
            enum_value
        )

    if hasattr(
        valeur,
        "model_dump",
    ):
        return rendre_json_serialisable(
            valeur.model_dump()
        )

    if hasattr(
        valeur,
        "dict",
    ):
        try:
            return rendre_json_serialisable(
                valeur.dict()
            )
        except Exception:
            pass

    return str(valeur)


def extraire_quantites(
    objet: Any,
) -> dict[str, int]:
    """
    Supporte :
    - Hand.quantities
    - dict
    - liste de cartes
    - objet itérable
    """

    if objet is None:
        return {}

    if hasattr(
        objet,
        "quantities",
    ):
        brut = objet.quantities

        return {
            nom_carte(carte): int(qte)
            for carte, qte
            in brut.items()
        }

    if hasattr(
        objet,
        "hand",
    ):
        return extraire_quantites(
            objet.hand
        )

    if isinstance(
        objet,
        dict,
    ):
        return {
            nom_carte(carte): int(qte)
            for carte, qte
            in objet.items()
        }

    if isinstance(
        objet,
        (
            list,
            tuple,
            set,
        ),
    ):
        quantites: dict[str, int] = {}

        for carte in objet:
            nom = nom_carte(carte)

            quantites[nom] = (
                quantites.get(
                    nom,
                    0,
                )
                + 1
            )

        return quantites

    try:
        cartes = list(objet)
    except TypeError:
        return {}

    quantites: dict[str, int] = {}

    for carte in cartes:
        nom = nom_carte(carte)

        quantites[nom] = (
            quantites.get(
                nom,
                0,
            )
            + 1
        )

    return quantites


def extraire_stock(
    game: Game,
) -> dict[str, int]:
    stock = getattr(
        game,
        "stock",
        None,
    )

    if stock is None:
        return {}

    quantites = getattr(
        stock,
        "quantities",
        {},
    )

    return {
        nom_carte(carte): int(qte)
        for carte, qte
        in quantites.items()
    }


def extraire_scores(
    game: Game,
) -> dict[str, int]:
    scores: dict[str, int] = {}

    for joueur in getattr(
        game,
        "players",
        [],
    ):
        nom = str(
            getattr(
                joueur,
                "name",
                "???",
            )
        )

        try:
            score = int(
                getattr(
                    joueur,
                    "score",
                    0,
                )
            )
        except Exception:
            score = 0

        scores[nom] = score

    return scores


def royaume_depuis_stock(
    stock: dict[str, int],
) -> dict[str, int]:
    cartes_base = {
        "copper",
        "silver",
        "gold",
        "estate",
        "duchy",
        "province",
        "curse",
    }

    return {
        nom: qte
        for nom, qte
        in stock.items()
        if nom not in cartes_base
    }


def piles_basses_depuis_royaume(
    royaume: dict[str, int],
    limite: int = 3,
) -> list[list[Any]]:
    return [
        [
            nom,
            qte,
        ]
        for nom, qte
        in sorted(
            royaume.items(),
            key=lambda item: (
                item[1],
                item[0],
            ),
        )[:limite]
    ]


def obtenir_argent_log(
    game: Game,
    etat: dict[str, Any],
) -> int:
    """
    Essaie d'abord les valeurs locales du moteur.
    Sinon recalcule l'argent de la main.
    """

    cles_possibles = (
        "budget_restant",
        "budget_achat_restant",
        "argent_restant",
        "argent",
    )

    for cle in cles_possibles:
        valeur = etat.get(
            cle,
        )

        if isinstance(
            valeur,
            (
                int,
                float,
            ),
        ):
            return int(
                valeur
            )

    try:
        return int(
            calculer_argent_main(
                game
            )
        )
    except Exception:
        return 0


def lire_stats() -> dict[str, Any]:
    if not FICHIER_STATS.exists():
        return {
            "parties_terminees_total": 0,
        }

    try:
        with FICHIER_STATS.open(
            "r",
            encoding="utf-8",
        ) as fichier:
            contenu = json.load(
                fichier
            )

        if not isinstance(
            contenu,
            dict,
        ):
            raise ValueError(
                "stats invalides"
            )

        return contenu

    except Exception:
        return {
            "parties_terminees_total": 0,
        }


def ecrire_json_atomique(
    chemin: Path,
    contenu: Any,
) -> None:
    chemin.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporaire = chemin.with_suffix(
        chemin.suffix + ".tmp"
    )

    with temporaire.open(
        "w",
        encoding="utf-8",
    ) as fichier:
        json.dump(
            rendre_json_serialisable(
                contenu
            ),
            fichier,
            ensure_ascii=False,
            indent=2,
        )

    temporaire.replace(
        chemin
    )


def sauvegarder_stats(
    stats: dict[str, Any],
) -> None:
    ecrire_json_atomique(
        FICHIER_STATS,
        stats,
    )


# ============================================================
# HISTORIQUE EN MÉMOIRE
# ============================================================

def demarrer_historique(
    game_id: str,
    game: Game | None = None,
) -> dict[str, Any]:
    with _verrou_logs:

        historique = _historiques.get(
            game_id
        )

        if historique is not None:
            return historique

        historique = {
            "game_id": game_id,
            "debut": maintenant_iso(),
            "fin": None,
            "resultat": None,
            "abandon": False,
            "raison_abandon": None,
            "nb_joueurs": (
                len(game.players)
                if game is not None
                else None
            ),
            "version_strategie":
                VERSION_STRATEGIE,
            "pid_initial": os.getpid(),
            "situations": [],
        }

        _historiques[
            game_id
        ] = historique

        return historique


def obtenir_historique(
    game_id: str,
) -> dict[str, Any]:
    with _verrou_logs:
        return _historiques.setdefault(
            game_id,
            {
                "game_id": game_id,
                "debut": maintenant_iso(),
                "fin": None,
                "resultat": None,
                "abandon": False,
                "raison_abandon": None,
                "nb_joueurs": None,
                "version_strategie":
                    VERSION_STRATEGIE,
                "pid_initial":
                    os.getpid(),
                "situations": [],
            },
        )


# ============================================================
# SITUATION
# ============================================================

def afficher_situation(
    game: Game,
    game_id: str,
) -> dict[str, Any]:

    historique = obtenir_historique(
        game_id
    )

    try:
        etat = obtenir_etat(
            game_id
        )
    except Exception:
        etat = {}

    moi = trouver_mon_joueur(
        game
    )

    scores = extraire_scores(
        game
    )

    if moi is not None:
        nom_joueur = str(
            getattr(
                moi,
                "name",
                "???",
            )
        )

        score = scores.get(
            nom_joueur,
            int(
                getattr(
                    moi,
                    "score",
                    0,
                )
                or 0
            ),
        )

        main = extraire_quantites(
            getattr(
                moi,
                "hand",
                None,
            )
        )
    else:
        nom_joueur = (
            historique
            .get(
                "situations",
                [{}],
            )[-1]
            .get(
                "joueur",
                "???",
            )
            if historique.get(
                "situations"
            )
            else "???"
        )

        score = scores.get(
            nom_joueur,
            0,
        )

        main = {}

    stock_complet = extraire_stock(
        game
    )

    stock_base = {
        nom: stock_complet.get(
            nom,
            0,
        )
        for nom in (
            "province",
            "duchy",
            "estate",
            "gold",
            "silver",
            "curse",
        )
    }

    royaume = royaume_depuis_stock(
        stock_complet
    )

    situation = {
        "tour": int(
            etat.get(
                "tour",
                0,
            )
            or 0
        ),

        # Diagnostic processus / déploiement
        "pid": os.getpid(),
        "version_strategie":
            VERSION_STRATEGIE,

        "partie_finie": bool(
            getattr(
                game,
                "finished",
                False,
            )
        ),

        "joueur": nom_joueur,
        "score": score,
        "scores": scores,

        "main": main,

        "argent":
            obtenir_argent_log(
                game,
                etat,
            ),

        "actions_restantes": int(
            etat.get(
                "actions_restantes",
                etat.get(
                    "actions",
                    1,
                ),
            )
            or 0
        ),

        "achats_restants": int(
            etat.get(
                "achats_restants",
                etat.get(
                    "achats",
                    1,
                ),
            )
            or 0
        ),

        "cartes_achetees":
            rendre_json_serialisable(
                etat.get(
                    "cartes_achetees",
                    {},
                )
            ),

        "gains_estimes":
            rendre_json_serialisable(
                etat.get(
                    "gains_estimes",
                    {},
                )
            ),

        "stock": stock_base,
        "royaume": royaume,

        "piles_vides":
            nombre_piles_vides(
                game
            ),

        "piles_basses":
            piles_basses_depuis_royaume(
                royaume
            ),

        "strategie":
            etat.get(
                "strategie_actuelle"
            ),

        "scores_strategies":
            rendre_json_serialisable(
                etat.get(
                    "scores_strategies",
                    {},
                )
            ),

        "decisions": [],
        "evaluations_achats": [],
    }

    with _verrou_logs:

        if historique.get(
            "nb_joueurs"
        ) is None:
            historique[
                "nb_joueurs"
            ] = len(
                getattr(
                    game,
                    "players",
                    [],
                )
            )

        historique[
            "situations"
        ].append(
            situation
        )

    return situation


# ============================================================
# ÉVALUATIONS D'ACHAT
# ============================================================

def compacter_evaluation(
    evaluation: Any,
) -> Any:

    if not isinstance(
        evaluation,
        dict,
    ):
        return rendre_json_serialisable(
            evaluation
        )

    # Cas où on reçoit directement :
    #
    # {
    #   "silver": {...},
    #   "gold": {...},
    #   ...
    # }
    #
    # On ne conserve que le top 5.

    cartes_evaluees = []

    for nom, details in evaluation.items():

        if not isinstance(
            details,
            dict,
        ):
            continue

        total = details.get(
            "total"
        )

        if not isinstance(
            total,
            (
                int,
                float,
            ),
        ):
            continue

        cartes_evaluees.append(
            (
                str(nom),
                total,
                details,
            )
        )

    if cartes_evaluees:

        cartes_evaluees.sort(
            key=lambda item:
                item[1],
            reverse=True,
        )

        top = {
            nom: total
            for nom, total, _
            in cartes_evaluees[:5]
        }

        return {
            "top": top,
        }

    return rendre_json_serialisable(
        evaluation
    )


def enregistrer_decision(
    game_id: str,
    decision: str,
    evaluation: Any = None,
) -> None:

    historique = obtenir_historique(
        game_id
    )

    with _verrou_logs:

        situations = historique.get(
            "situations",
            [],
        )

        if not situations:
            return

        situation = situations[-1]

        situation.setdefault(
            "decisions",
            [],
        ).append(
            str(decision)
        )

        if evaluation is None:
            return

        evaluation_compacte = (
            compacter_evaluation(
                evaluation
            )
        )

        situation.setdefault(
            "evaluations_achats",
            [],
        ).append(
            evaluation_compacte
        )


def enregistrer_evaluation_achat(
    game_id: str,
    decision: str,
    strategie: str | None,
    evaluations: dict[str, Any],
    choisi: dict[str, Any] | None = None,
) -> None:
    """
    Variante plus précise si strategy.py fournit déjà
    toutes les évaluations.
    """

    historique = obtenir_historique(
        game_id
    )

    top = []

    for nom, details in evaluations.items():

        if not isinstance(
            details,
            dict,
        ):
            continue

        total = details.get(
            "total"
        )

        if isinstance(
            total,
            (
                int,
                float,
            ),
        ):
            top.append(
                (
                    str(nom),
                    total,
                )
            )

    top.sort(
        key=lambda item:
            item[1],
        reverse=True,
    )

    resultat = {
        "decision": decision,
        "strategie": strategie,
        "top": {
            nom: score
            for nom, score
            in top[:5]
        },
        "choisi":
            rendre_json_serialisable(
                choisi
            )
            if choisi is not None
            else None,
    }

    with _verrou_logs:

        situations = historique.get(
            "situations",
            [],
        )

        if not situations:
            return

        situations[-1].setdefault(
            "evaluations_achats",
            [],
        ).append(
            resultat
        )


# ============================================================
# RÉSULTAT
# ============================================================

def elimination_precoce_probable(
    historique: dict[str, Any],
) -> bool:
    """
    Détecte le cas où le bot a probablement été éliminé
    immédiatement par Dopynion.

    Typiquement :
    - une seule situation
    - tour 1
    - partie non terminée
    - scores encore tous identiques
    """

    situations = historique.get(
        "situations",
        [],
    )

    if len(
        situations
    ) != 1:
        return False

    situation = situations[0]

    if situation.get(
        "tour"
    ) != 1:
        return False

    if situation.get(
        "partie_finie"
    ):
        return False

    scores = situation.get(
        "scores",
        {},
    )

    if not scores:
        return False

    valeurs = list(
        scores.values()
    )

    return len(
        set(
            valeurs
        )
    ) == 1


def est_victoire_historique(
    historique: dict[str, Any],
) -> bool:

    situations = historique.get(
        "situations",
        [],
    )

    if not situations:
        return False

    situation = situations[-1]

    scores = situation.get(
        "scores",
        {},
    )

    joueur = situation.get(
        "joueur"
    )

    if (
        not scores
        or joueur not in scores
    ):
        return False

    mon_score = scores[
        joueur
    ]

    meilleur_score = max(
        scores.values()
    )

    # Une égalité au meilleur score compte
    # comme victoire.
    return (
        mon_score
        == meilleur_score
    )


def est_victoire(
    game: Game,
) -> bool:

    moi = trouver_mon_joueur(
        game
    )

    joueurs = getattr(
        game,
        "players",
        [],
    )

    if (
        moi is None
        or not joueurs
    ):
        return False

    mon_score = int(
        getattr(
            moi,
            "score",
            0,
        )
        or 0
    )

    meilleur_score = max(
        int(
            getattr(
                joueur,
                "score",
                0,
            )
            or 0
        )
        for joueur
        in joueurs
    )

    return (
        mon_score
        == meilleur_score
    )


# ============================================================
# SAUVEGARDE PARTIE
# ============================================================

def nom_fichier_partie(
    resultat: str,
    game_id: str,
) -> str:

    date = datetime.now().astimezone()

    prefixe = date.strftime(
        "%m%d%H%M"
    )

    return (
        f"{prefixe}"
        f"{resultat}_"
        f"{game_id}.json"
    )


def terminer_historique(
    game_id: str,
    game: Game | None = None,
    abandon: bool = False,
    raison_abandon: str | None = None,
) -> Path:

    with _verrou_logs:

        historique = obtenir_historique(
            game_id
        )

        historique[
            "fin"
        ] = maintenant_iso()

        historique[
            "abandon"
        ] = bool(
            abandon
        )

        historique[
            "raison_abandon"
        ] = raison_abandon

        # ----------------------------------------------------
        # FORFAIT / ABANDON
        # ----------------------------------------------------

        if abandon:
            resultat = "F"

        # ----------------------------------------------------
        # ÉLIMINATION PRÉCOCE / COMMANDE INVALIDE
        # ----------------------------------------------------

        elif elimination_precoce_probable(
            historique
        ):
            resultat = "F"

            historique[
                "abandon"
            ] = True

            if not historique.get(
                "raison_abandon"
            ):
                historique[
                    "raison_abandon"
                ] = (
                    "elimination_precoce"
                )

        # ----------------------------------------------------
        # RÉSULTAT NORMAL
        # ----------------------------------------------------

        else:

            victoire = False

            if game is not None:
                try:
                    victoire = est_victoire(
                        game
                    )
                except Exception:
                    victoire = (
                        est_victoire_historique(
                            historique
                        )
                    )
            else:
                victoire = (
                    est_victoire_historique(
                        historique
                    )
                )

            resultat = (
                "V"
                if victoire
                else "D"
            )

        historique[
            "resultat"
        ] = resultat

        historique[
            "pid_final"
        ] = os.getpid()

        nom_fichier = nom_fichier_partie(
            resultat,
            game_id,
        )

        chemin = (
            DOSSIER_LOGS
            / nom_fichier
        )

        ecrire_json_atomique(
            chemin,
            historique,
        )

        print(
            "[LOGGER SAVE]",
            {
                "game_id":
                    game_id,
                "resultat":
                    resultat,
                "fichier":
                    str(
                        chemin
                    ),
                "pid":
                    os.getpid(),
                "version":
                    VERSION_STRATEGIE,
            },
            flush=True,
        )

        _historiques.pop(
            game_id,
            None,
        )

        stats = lire_stats()

        stats[
            "parties_terminees_total"
        ] = (
            int(
                stats.get(
                    "parties_terminees_total",
                    0,
                )
            )
            + 1
        )

        stats[
            "derniere_partie"
        ] = nom_fichier

        stats[
            "derniere_mise_a_jour"
        ] = maintenant_iso()

        sauvegarder_stats(
            stats
        )

        nettoyer_anciens_logs()

        total = stats[
            "parties_terminees_total"
        ]

        if (
            total
            % TAILLE_RESUME
            == 0
        ):
            generer_resume(
                total
            )

        return chemin


# ============================================================
# ABANDON EXPLICITE
# ============================================================

def terminer_historique_abandon(
    game_id: str,
    raison: str,
    game: Game | None = None,
) -> Path:

    return terminer_historique(
        game_id=game_id,
        game=game,
        abandon=True,
        raison_abandon=raison,
    )


# ============================================================
# LECTURE DES LOGS
# ============================================================

REGEX_LOG_PARTIE = re.compile(
    r"^\d{8}[VDF]_.+\.json$"
)


def lister_logs_parties() -> list[Path]:

    fichiers = []

    for chemin in (
        DOSSIER_LOGS
        .glob(
            "*.json"
        )
    ):
        if REGEX_LOG_PARTIE.match(
            chemin.name
        ):
            fichiers.append(
                chemin
            )

    fichiers.sort(
        key=lambda chemin:
            chemin.stat().st_mtime
    )

    return fichiers


def lire_log(
    chemin: Path,
) -> dict[str, Any] | None:

    try:
        with chemin.open(
            "r",
            encoding="utf-8",
        ) as fichier:
            contenu = json.load(
                fichier
            )

        if isinstance(
            contenu,
            dict,
        ):
            return contenu

    except Exception as exc:
        print(
            "[LOGGER WARNING]",
            "Impossible de lire",
            chemin,
            repr(exc),
            flush=True,
        )

    return None


# ============================================================
# NETTOYAGE
# ============================================================

def nettoyer_anciens_logs() -> None:

    fichiers = lister_logs_parties()

    if len(
        fichiers
    ) <= MAX_LOGS:
        return

    nombre_a_supprimer = (
        len(fichiers)
        - MAX_LOGS
    )

    for chemin in fichiers[
        :nombre_a_supprimer
    ]:
        try:
            chemin.unlink()
        except OSError:
            pass


# ============================================================
# RÉSUMÉ
# ============================================================

def win_rate(
    victoires: int,
    defaites: int,
) -> float:

    total = (
        victoires
        + defaites
    )

    if total <= 0:
        return 0.0

    return round(
        victoires
        / total
        * 100,
        1,
    )


def valeur_finale(
    historique: dict[str, Any],
    cle: str,
    defaut: Any = None,
) -> Any:

    situations = historique.get(
        "situations",
        [],
    )

    if not situations:
        return defaut

    return situations[-1].get(
        cle,
        defaut,
    )


def nombre_actions_achetees_log(
    historique: dict[str, Any],
) -> int:

    cartes = valeur_finale(
        historique,
        "cartes_achetees",
        {},
    )

    if not isinstance(
        cartes,
        dict,
    ):
        return 0

    cartes_non_actions = {
        "copper",
        "silver",
        "gold",
        "estate",
        "duchy",
        "province",
        "gardens",
        "curse",
    }

    return sum(
        int(qte)
        for nom, qte
        in cartes.items()
        if (
            str(nom).lower()
            not in cartes_non_actions
        )
    )


def moyenne(
    valeurs: list[float],
) -> float:

    if not valeurs:
        return 0.0

    return round(
        sum(valeurs)
        / len(valeurs),
        2,
    )


def generer_resume(
    total_parties: int | None = None,
) -> Path | None:

    fichiers = lister_logs_parties()

    if not fichiers:
        return None

    fichiers_fenetre = fichiers[
        -TAILLE_RESUME:
    ]

    logs = []

    for chemin in fichiers_fenetre:

        contenu = lire_log(
            chemin
        )

        if contenu is not None:
            logs.append(
                (
                    chemin,
                    contenu,
                )
            )

    if not logs:
        return None

    if total_parties is None:
        stats = lire_stats()

        total_parties = int(
            stats.get(
                "parties_terminees_total",
                len(logs),
            )
        )

    resultats = {
        "V": 0,
        "D": 0,
        "F": 0,
    }

    par_nombre_joueurs: dict[
        str,
        dict[str, Any]
    ] = {}

    strategies: dict[
        str,
        int
    ] = {}

    tours = []
    scores = []
    actions_achetees = []

    valeurs_cartes = {
        "gold": [],
        "silver": [],
        "province": [],
        "duchy": [],
        "estate": [],
        "gardens": [],
        "witch": [],
        "militia": [],
        "bandit": [],
        "laboratory": [],
    }

    for _, historique in logs:

        resultat = historique.get(
            "resultat"
        )

        if resultat not in (
            "V",
            "D",
            "F",
        ):
            continue

        resultats[
            resultat
        ] += 1

        nb_joueurs = historique.get(
            "nb_joueurs"
        )

        cle_nb = str(
            nb_joueurs
        )

        if cle_nb not in (
            par_nombre_joueurs
        ):
            par_nombre_joueurs[
                cle_nb
            ] = {
                "V": 0,
                "D": 0,
                "F": 0,
                "win_rate": 0.0,
            }

        par_nombre_joueurs[
            cle_nb
        ][
            resultat
        ] += 1

        # Les statistiques stratégiques ne doivent
        # pas être polluées par les forfaits.
        if resultat == "F":
            continue

        situations = historique.get(
            "situations",
            [],
        )

        if not situations:
            continue

        derniere = situations[-1]

        tour_final = derniere.get(
            "tour",
            0,
        )

        score_final = derniere.get(
            "score",
            0,
        )

        tours.append(
            float(
                tour_final
                or 0
            )
        )

        scores.append(
            float(
                score_final
                or 0
            )
        )

        actions_achetees.append(
            float(
                nombre_actions_achetees_log(
                    historique
                )
            )
        )

        cartes_achetees = (
            derniere.get(
                "cartes_achetees",
                {},
            )
            or {}
        )

        for nom in valeurs_cartes:
            valeurs_cartes[
                nom
            ].append(
                float(
                    cartes_achetees.get(
                        nom,
                        0,
                    )
                    or 0
                )
            )

        strategie = derniere.get(
            "strategie"
        )

        if strategie:
            strategie = str(
                strategie
            )

            strategies[
                strategie
            ] = (
                strategies.get(
                    strategie,
                    0,
                )
                + 1
            )

    for donnees in (
        par_nombre_joueurs
        .values()
    ):
        donnees[
            "win_rate"
        ] = win_rate(
            donnees["V"],
            donnees["D"],
        )

    resultats[
        "win_rate"
    ] = win_rate(
        resultats["V"],
        resultats["D"],
    )

    moyennes = {
        "tour_final":
            moyenne(
                tours
            ),

        "score":
            moyenne(
                scores
            ),

        "actions_achetees":
            moyenne(
                actions_achetees
            ),
    }

    for nom, valeurs in (
        valeurs_cartes.items()
    ):
        moyennes[
            nom
        ] = moyenne(
            valeurs
        )

    strategies_triees = dict(
        sorted(
            strategies.items(),
            key=lambda item:
                item[1],
            reverse=True,
        )
    )

    resume = {
        "genere_le":
            maintenant_iso(),

        "parties_terminees_total":
            total_parties,

        "fenetre":
            len(logs),

        "plage": {
            "premier_log":
                logs[0][0].name,

            "dernier_log":
                logs[-1][0].name,
        },

        "resultats":
            resultats,

        "par_nombre_joueurs":
            par_nombre_joueurs,

        "moyennes":
            moyennes,

        "strategies":
            strategies_triees,

        "programme": {
            "parties_actives":
                len(
                    _historiques
                ),

            "logs_conserves_max":
                MAX_LOGS,

            "taille_resume":
                TAILLE_RESUME,

            "dossier_resumes":
                str(
                    DOSSIER_RESUMES
                    .relative_to(
                        BASE_DIR
                    )
                ),

            "pid":
                os.getpid(),

            "version_strategie":
                VERSION_STRATEGIE,
        },
    }

    nom_resume = (
        f"resume_"
        f"{TAILLE_RESUME:06d}"
        f".json"
    )

    chemin_resume = (
        DOSSIER_RESUMES
        / nom_resume
    )

    ecrire_json_atomique(
        chemin_resume,
        resume,
    )

    print(
        "[LOGGER RESUME]",
        {
            "fichier":
                str(
                    chemin_resume
                ),
            "total":
                total_parties,
            "fenetre":
                len(logs),
            "win_rate":
                resultats[
                    "win_rate"
                ],
        },
        flush=True,
    )

    return chemin_resume


# ============================================================
# DEBUG
# ============================================================

def infos_logger() -> dict[str, Any]:
    """
    Pratique pour afficher rapidement l'état du logger
    depuis un shell ou un endpoint temporaire.
    """

    return {
        "pid": os.getpid(),
        "cwd": os.getcwd(),
        "base_dir":
            str(
                BASE_DIR
            ),
        "dossier_logs":
            str(
                DOSSIER_LOGS
            ),
        "dossier_resumes":
            str(
                DOSSIER_RESUMES
            ),
        "writable":
            os.access(
                DOSSIER_LOGS,
                os.W_OK,
            ),
        "version_strategie":
            VERSION_STRATEGIE,
        "parties_actives":
            len(
                _historiques
            ),
        "nombre_logs":
            len(
                lister_logs_parties()
            ),
        "stats":
            lire_stats(),
    }