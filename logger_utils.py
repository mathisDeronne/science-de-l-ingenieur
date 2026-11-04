import json
import os
import re
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from dopynion.data_model import Game

from config import EFFETS_ACTIONS
from game_utils import (
    calculer_argent_main,
    nombre_piles_vides,
    trouver_mon_joueur,
)
from state import obtenir_etat


DOSSIER_LOGS = (
    Path(__file__).resolve().parent
    / "logs"
)

DOSSIER_LOGS.mkdir(
    exist_ok=True
)


DOSSIER_RESUMES = (
    DOSSIER_LOGS
    / "resumes"
)

DOSSIER_RESUMES.mkdir(
    exist_ok=True
)


MAX_PARTIES_LOGS = 500
TAILLE_RESUME = 100


FICHIER_STATS = (
    DOSSIER_LOGS
    / "_stats.json"
)


_verrous_logs_parties: dict[
    str,
    threading.RLock,
] = {}

_verrou_registre_logs = (
    threading.Lock()
)

_verrou_resume = (
    threading.RLock()
)


def verrou_log_partie(
    game_id: str,
) -> threading.RLock:
    verrou = (
        _verrous_logs_parties.get(
            game_id
        )
    )

    if verrou is not None:
        return verrou

    with _verrou_registre_logs:
        return (
            _verrous_logs_parties
            .setdefault(
                game_id,
                threading.RLock(),
            )
        )


def maintenant() -> str:
    return (
        datetime
        .now()
        .astimezone()
        .isoformat(
            timespec="seconds"
        )
    )


def nom_temporaire(
    game_id: str,
) -> str:
    propre = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        str(game_id),
    )

    return (
        f"game_{propre}.json"
    )


def chemin_temporaire(
    game_id: str,
) -> Path:
    return (
        DOSSIER_LOGS
        / nom_temporaire(
            game_id
        )
    )


def ecrire_json_atomique(
    fichier: Path,
    contenu: dict[str, Any],
) -> None:
    temporaire = fichier.with_suffix(
        fichier.suffix
        + ".tmp"
    )

    temporaire.write_text(
        json.dumps(
            contenu,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    temporaire.replace(
        fichier
    )


def sauvegarder(
    game_id: str,
    historique: dict[str, Any],
) -> None:
    ecrire_json_atomique(
        chemin_temporaire(
            game_id
        ),
        historique,
    )


def nouvel_historique(
    game_id: str,
) -> dict[str, Any]:
    return {
        "game_id": game_id,

        "debut": maintenant(),
        "fin": None,

        "resultat": None,

        "abandon": False,
        "raison_abandon": None,

        "nb_joueurs": None,

        "situations": [],
    }


def charger_historique(
    game_id: str,
) -> dict[str, Any]:
    fichier = chemin_temporaire(
        game_id
    )

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

    return nouvel_historique(
        game_id
    )


def initialiser_historique(
    game_id: str,
) -> None:
    with verrou_log_partie(
        game_id
    ):
        sauvegarder(
            game_id,
            nouvel_historique(
                game_id
            ),
        )


def afficher_situation(
    game: Game,
    game_id: str,
) -> None:
    moi = trouver_mon_joueur(
        game
    )

    if moi is None:
        return

    etat = obtenir_etat(
        game_id
    )

    stock = {
        carte.value.lower():
            quantite
        for carte, quantite
        in game.stock.quantities.items()
    }

    piles_basses = sorted(
        stock.items(),
        key=lambda item:
            item[1],
    )[:3]

    argent = (
        calculer_argent_main(
            game
        )
        + etat["bonus_pieces"]
    )

    cartes_basiques = {
        "province",
        "duchy",
        "estate",
        "gold",
        "silver",
        "copper",
        "curse",
    }

    situation = {
        "tour":
            etat["tour"],

        "pid":
            os.getpid(),

        "partie_finie":
            game.finished,

        "joueur":
            moi.name,

        "score":
            moi.score,

        "scores": {
            joueur.name:
                joueur.score
            for joueur
            in game.players
        },

        "main": (
            {
                carte.value:
                    quantite
                for carte, quantite
                in moi.hand.quantities.items()
            }
            if moi.hand is not None
            else {}
        ),

        "argent":
            argent,

        "actions_restantes":
            etat[
                "actions_restantes"
            ],

        "achats_restants":
            etat[
                "achats_restants"
            ],

        "cartes_achetees":
            dict(
                etat[
                    "cartes_achetees"
                ]
            ),

        "gains_estimes":
            dict(
                etat.get(
                    "gains_estimes",
                    {},
                )
            ),

        "stock": {
            nom:
                stock.get(
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
        },

        "royaume": {
            nom:
                quantite
            for nom, quantite
            in stock.items()
            if nom
            not in cartes_basiques
        },

        "piles_vides":
            nombre_piles_vides(
                game
            ),

        "piles_basses":
            piles_basses,

        "strategie":
            etat.get(
                "strategie_actuelle"
            ),
    }

    with verrou_log_partie(
        game_id
    ):
        historique = (
            charger_historique(
                game_id
            )
        )

        historique[
            "nb_joueurs"
        ] = len(
            game.players
        )

        situations = historique[
            "situations"
        ]

        if (
            situations
            and situations[-1].get(
                "tour"
            )
            == etat["tour"]
        ):
            precedente = (
                situations[-1]
            )

            situation[
                "decisions"
            ] = precedente.get(
                "decisions",
                [],
            )

            situation[
                "evaluations_achats"
            ] = precedente.get(
                "evaluations_achats",
                [],
            )

            situations[-1] = (
                situation
            )

        else:
            situation[
                "decisions"
            ] = []

            situation[
                "evaluations_achats"
            ] = []

            situations.append(
                situation
            )

        sauvegarder(
            game_id,
            historique,
        )


def compacter_evaluation_achat(
    etat: dict[str, Any],
    decision: str,
) -> dict[str, Any]:
    evaluations = etat.get(
        "derniere_evaluation_achat",
        {},
    )

    nom_choisi = (
        decision
        .removeprefix(
            "BUY "
        )
        .strip()
        .lower()
    )

    classement = sorted(
        (
            (
                nom,
                evaluation.get(
                    "total",
                    -10000,
                ),
            )
            for nom, evaluation
            in evaluations.items()
        ),
        key=lambda item:
            item[1],
        reverse=True,
    )[:5]

    choisi = evaluations.get(
        nom_choisi,
        {},
    )

    detail_choisi = {
        cle: valeur
        for cle, valeur
        in choisi.items()
        if cle not in {
            "scores_strategies",
            "strategie",
        }
    }

    return {
        "decision":
            decision,

        "strategie":
            etat.get(
                "strategie_actuelle"
            ),

        "top": {
            nom:
                poids
            for nom, poids
            in classement
        },

        "choisi":
            detail_choisi,
    }


def enregistrer_decision(
    game_id: str,
    tour: int,
    decision: str,
) -> None:
    etat = obtenir_etat(
        game_id
    )

    evaluation = None

    if decision.startswith(
        "BUY "
    ):
        evaluation = (
            compacter_evaluation_achat(
                etat,
                decision,
            )
        )

    with verrou_log_partie(
        game_id
    ):
        historique = (
            charger_historique(
                game_id
            )
        )

        situations = historique.get(
            "situations",
            [],
        )

        if not situations:
            return

        situation = (
            situations[-1]
        )

        if (
            situation.get(
                "tour"
            )
            != tour
        ):
            return

        decisions = (
            situation.setdefault(
                "decisions",
                [],
            )
        )

        if (
            not decisions
            or decisions[-1]
            != decision
        ):
            decisions.append(
                decision
            )

        if evaluation is not None:
            situation.setdefault(
                "evaluations_achats",
                [],
            ).append(
                evaluation
            )

        sauvegarder(
            game_id,
            historique,
        )


def marquer_abandon(
    game_id: str,
    raison: str,
) -> None:
    with verrou_log_partie(
        game_id
    ):
        historique = (
            charger_historique(
                game_id
            )
        )

        historique[
            "abandon"
        ] = True

        historique[
            "raison_abandon"
        ] = raison

        sauvegarder(
            game_id,
            historique,
        )


def est_abandon(
    historique: dict[str, Any],
) -> bool:
    if historique.get(
        "abandon",
        False,
    ):
        return True

    situations = historique.get(
        "situations",
        [],
    )

    if not situations:
        return False

    derniere = situations[-1]

    joueur = derniere.get(
        "joueur"
    )

    scores = derniere.get(
        "scores",
        {},
    )

    if joueur not in scores:
        return False

    return (
        scores[joueur]
        <= -10000
    )


def elimination_precoce_probable(
    historique: dict[str, Any],
) -> bool:
    situations = historique.get(
        "situations",
        [],
    )

    if len(situations) != 1:
        return False

    derniere = situations[0]

    if derniere.get(
        "tour"
    ) != 1:
        return False

    if derniere.get(
        "partie_finie",
        False,
    ):
        return False

    scores = derniere.get(
        "scores",
        {},
    )

    if not scores:
        return False

    # Cas typique du kick :
    # premier tour, partie non finie,
    # tous les joueurs encore au
    # score de départ.
    return (
        len(
            set(
                scores.values()
            )
        )
        == 1
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
        or mon_joueur
        not in scores
    ):
        return False

    return (
        scores[
            mon_joueur
        ]
        == max(
            scores.values()
        )
    )


def nom_final(
    historique: dict[str, Any],
    resultat: str,
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
        debut = (
            datetime
            .now()
            .astimezone()
        )

    prefixe = debut.strftime(
        "%m%d%H%M"
    )

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


def fichiers_logs_finalises(
) -> list[Path]:
    motif = re.compile(
        r"^\d{8}[VDF]_.+\.json$"
    )

    fichiers = [
        fichier
        for fichier
        in DOSSIER_LOGS.glob(
            "*.json"
        )
        if motif.match(
            fichier.name
        )
    ]

    fichiers.sort(
        key=lambda fichier:
            fichier.stat().st_mtime,
        reverse=True,
    )

    return fichiers


def nettoyer_anciens_logs(
) -> None:
    with _verrou_resume:
        fichiers = (
            fichiers_logs_finalises()
        )

        if (
            len(fichiers)
            <= MAX_PARTIES_LOGS
        ):
            return

        for fichier in fichiers[
            MAX_PARTIES_LOGS:
        ]:
            try:
                fichier.unlink()

            except FileNotFoundError:
                pass


def stats_vides(
) -> dict[str, Any]:
    return {
        "parties_terminees": 0,
        "parties_depuis_resume": 0,
        "dernier_resume": 0,
        "logs_recents": [],
    }


def reconstruire_stats(
    exclure_nom: str | None = None,
) -> dict[str, Any]:
    fichiers = [
        fichier
        for fichier
        in fichiers_logs_finalises()
        if fichier.name
        != exclure_nom
    ]

    chronologiques = list(
        reversed(
            fichiers[
                :MAX_PARTIES_LOGS
            ]
        )
    )

    total = len(
        fichiers
    )

    return {
        "parties_terminees":
            total,

        "parties_depuis_resume":
            total
            % TAILLE_RESUME,

        "dernier_resume":
            (
                total
                // TAILLE_RESUME
            )
            * TAILLE_RESUME,

        "logs_recents": [
            fichier.name
            for fichier
            in chronologiques
        ],
    }


def charger_stats(
) -> dict[str, Any] | None:
    if not FICHIER_STATS.exists():
        return None

    try:
        stats = json.loads(
            FICHIER_STATS.read_text(
                encoding="utf-8"
            )
        )

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return None

    stats.setdefault(
        "parties_terminees",
        0,
    )

    stats.setdefault(
        "dernier_resume",
        0,
    )

    stats.setdefault(
        "logs_recents",
        [],
    )

    stats.setdefault(
        "parties_depuis_resume",
        (
            stats[
                "parties_terminees"
            ]
            % TAILLE_RESUME
        ),
    )

    return stats


def charger_logs_par_noms(
    noms: list[str],
) -> list[dict[str, Any]]:
    resultats = []

    for nom in noms:
        fichier = (
            DOSSIER_LOGS
            / nom
        )

        if not fichier.exists():
            continue

        try:
            historique = json.loads(
                fichier.read_text(
                    encoding="utf-8"
                )
            )

        except (
            json.JSONDecodeError,
            OSError,
        ):
            continue

        if historique.get(
            "resultat"
        ) not in {
            "V",
            "D",
            "F",
        }:
            continue

        resultats.append(
            historique
        )

    return resultats


def strategie_log(
    historique: dict[str, Any],
) -> str | None:
    for situation in reversed(
        historique.get(
            "situations",
            [],
        )
    ):
        evaluations = (
            situation.get(
                "evaluations_achats",
                [],
            )
        )

        for evaluation in reversed(
            evaluations
        ):
            strategie = (
                evaluation.get(
                    "strategie"
                )
            )

            if strategie:
                return strategie

    return None


def moyenne(
    valeurs: list[
        int | float
    ],
) -> float | None:
    if not valeurs:
        return None

    return round(
        sum(valeurs)
        / len(valeurs),
        2,
    )


def generer_resume(
    total_parties: int,
    noms_logs: list[str],
) -> dict[str, Any]:
    logs = charger_logs_par_noms(
        noms_logs
    )

    resultats = {
        "V": 0,
        "D": 0,
        "F": 0,
    }

    par_joueurs = {}
    strategies = {}

    tours = []
    scores = []
    actions = []

    achats = {
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

    for historique in logs:
        resultat = historique.get(
            "resultat"
        )

        if resultat in resultats:
            resultats[
                resultat
            ] += 1

        nb_joueurs = historique.get(
            "nb_joueurs"
        )

        if nb_joueurs is not None:
            cle = str(
                nb_joueurs
            )

            stats_joueurs = (
                par_joueurs.setdefault(
                    cle,
                    {
                        "V": 0,
                        "D": 0,
                        "F": 0,
                    },
                )
            )

            if resultat in stats_joueurs:
                stats_joueurs[
                    resultat
                ] += 1

        # Les F ne sont pas utilisés
        # pour évaluer la stratégie.
        if resultat == "F":
            continue

        situations = historique.get(
            "situations",
            [],
        )

        if not situations:
            continue

        derniere = (
            situations[-1]
        )

        tour = derniere.get(
            "tour"
        )

        if isinstance(
            tour,
            int,
        ):
            tours.append(
                tour
            )

        score = derniere.get(
            "score"
        )

        if isinstance(
            score,
            (
                int,
                float,
            ),
        ):
            scores.append(
                score
            )

        cartes = derniere.get(
            "cartes_achetees",
            {},
        )

        nb_actions = sum(
            cartes.get(
                nom,
                0,
            )
            for nom
            in EFFETS_ACTIONS
        )

        actions.append(
            nb_actions
        )

        for nom in achats:
            achats[nom].append(
                cartes.get(
                    nom,
                    0,
                )
            )

        strategie = strategie_log(
            historique
        )

        if strategie:
            strategies[
                strategie
            ] = (
                strategies.get(
                    strategie,
                    0,
                )
                + 1
            )

    v = resultats["V"]
    d = resultats["D"]

    win_rate = (
        round(
            v
            / (v + d)
            * 100,
            1,
        )
        if v + d > 0
        else None
    )

    for stats in (
        par_joueurs.values()
    ):
        vj = stats["V"]
        dj = stats["D"]

        stats[
            "win_rate"
        ] = (
            round(
                vj
                / (vj + dj)
                * 100,
                1,
            )
            if vj + dj > 0
            else None
        )

    return {
        "genere_le":
            maintenant(),

        "parties_terminees_total":
            total_parties,

        "fenetre":
            len(logs),

        "plage": {
            "premier_log":
                noms_logs[0]
                if noms_logs
                else None,

            "dernier_log":
                noms_logs[-1]
                if noms_logs
                else None,
        },

        "resultats": {
            **resultats,
            "win_rate":
                win_rate,
        },

        "par_nombre_joueurs":
            par_joueurs,

        "moyennes": {
            "tour_final":
                moyenne(tours),

            "score":
                moyenne(scores),

            "actions_achetees":
                moyenne(actions),

            **{
                nom:
                    moyenne(
                        valeurs
                    )
                for nom, valeurs
                in achats.items()
            },
        },

        "strategies":
            dict(
                sorted(
                    strategies.items(),
                    key=lambda item:
                        item[1],
                    reverse=True,
                )
            ),

        "programme": {
            "parties_actives":
                len(
                    list(
                        DOSSIER_LOGS.glob(
                            "game_*.json"
                        )
                    )
                ),

            "logs_conserves_max":
                MAX_PARTIES_LOGS,

            "taille_resume":
                TAILLE_RESUME,

            "dossier_resumes":
                "logs/resumes",
        },
    }


def enregistrer_partie_terminee(
    nom_fichier: str,
) -> None:
    with _verrou_resume:
        stats = charger_stats()

        if stats is None:
            # Le fichier final vient déjà
            # d'être créé : on l'exclut
            # pendant la reconstruction
            # pour éviter un double comptage.
            stats = reconstruire_stats(
                exclure_nom=nom_fichier,
            )

        stats[
            "parties_terminees"
        ] += 1

        stats[
            "parties_depuis_resume"
        ] += 1

        total = stats[
            "parties_terminees"
        ]

        logs_recents = stats[
            "logs_recents"
        ]

        logs_recents.append(
            nom_fichier
        )

        if (
            len(logs_recents)
            > MAX_PARTIES_LOGS
        ):
            del logs_recents[
                :-MAX_PARTIES_LOGS
            ]

        if (
            stats[
                "parties_depuis_resume"
            ]
            >= TAILLE_RESUME
            and len(
                logs_recents
            )
            >= TAILLE_RESUME
        ):
            derniers_100 = (
                logs_recents[
                    -TAILLE_RESUME:
                ]
            )

            resume = generer_resume(
                total,
                derniers_100,
            )

            fichier_resume = (
                DOSSIER_RESUMES
                / (
                    f"resume_"
                    f"{total:06d}"
                    f".json"
                )
            )

            ecrire_json_atomique(
                fichier_resume,
                resume,
            )

            stats[
                "dernier_resume"
            ] = total

            stats[
                "parties_depuis_resume"
            ] = 0

            print(
                f">>> Résumé créé : "
                f"{fichier_resume.name}",
                flush=True,
            )

        ecrire_json_atomique(
            FICHIER_STATS,
            stats,
        )


def terminer_historique(
    game_id: str,
) -> None:
    final = None

    with verrou_log_partie(
        game_id
    ):
        temporaire = (
            chemin_temporaire(
                game_id
            )
        )

        if not temporaire.exists():
            return

        historique = (
            charger_historique(
                game_id
            )
        )

        if est_abandon(
            historique
        ):
            resultat = "F"

        elif elimination_precoce_probable(
            historique
        ):
            resultat = "F"

            historique[
                "abandon"
            ] = True

            historique[
                "raison_abandon"
            ] = (
                "elimination_precoce"
            )

        elif est_victoire(
            historique
        ):
            resultat = "V"

        else:
            resultat = "D"

        historique[
            "fin"
        ] = maintenant()

        historique[
            "resultat"
        ] = resultat

        final = (
            DOSSIER_LOGS
            / nom_final(
                historique,
                resultat,
            )
        )

        ecrire_json_atomique(
            final,
            historique,
        )

        temporaire.unlink(
            missing_ok=True
        )

    if final is not None:
        enregistrer_partie_terminee(
            final.name
        )

        nettoyer_anciens_logs()

        print(
            f">>> Log final : "
            f"{final.name}",
            flush=True,
        )