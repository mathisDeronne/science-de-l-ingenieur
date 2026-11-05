from __future__ import annotations

from typing import Any

from dopynion.data_model import Game

from config import (
    BONUS_BUREAUCRAT_4_JOUEURS,
    BONUS_PREMIER_HIRELING,
    CARTES_PIOCHE,
    CARTES_PIOCHE_FORTE,
    CARTES_SUPPORT_ACTIONS,
    CARTES_TERMINALES,
    MALUS_PAR_COPIE_ACTION,
    MAX_CARTES_ACTION,
    MAX_TOTAL_ACTIONS,
    MAX_TOTAL_ACTIONS_BASE,
    NB_ACTIONS_AVANT_ECONOMIE,
    PLANS,
    POIDS_BASE_ACHAT,
    SYNERGIES_ACHAT,
    TOUR_MAX_PREMIER_HIRELING,
)

from game_utils import (
    curses_restantes,
    nombre_piles_vides,
    piles_presentes,
    provinces_restantes,
    quantite_stock,
    risque_fin_par_piles,
    trouver_mon_joueur,
)

from deck import taille_deck
from fin_partie import bonus_fin_partie
from plans import (
    bonus_carte_cle,
    plan_actuel,
)
from state import (
    nombre_total_actions,
    obtenir_etat,
    quantite_achetee,
    quantite_economique,
)


# =========================================================
# OUTILS GÉNÉRAUX
# =========================================================

def nombre_achetees_parmi(
    game_id: str,
    cartes: set[str],
) -> int:
    # Ex : nombre de cartes de pioche,
    # de terminales, de Villages...
    return sum(
        quantite_achetee(
            game_id,
            nom,
        )
        for nom in cartes
    )


def ecart_score(
    game: Game,
) -> int:
    moi = trouver_mon_joueur(
        game
    )

    if moi is None:
        return 0

    adversaires = [
        joueur.score
        for joueur
        in game.players
        if joueur is not moi
    ]

    if not adversaires:
        return 0

    return (
        moi.score
        - max(
            adversaires
        )
    )


# =========================================================
# STRATÉGIE = PLAN DE PARTIE
# =========================================================
#
# Le plan est choisi une fois au premier achat d'après le
# royaume, puis ne change qu'une fois au maximum, sur un
# déclencheur fort. Toute la logique est dans plans.py,
# les bonus de chaque plan dans config.PLANS.
# =========================================================

def bonus_strategie(
    nom: str,
    strategie: str,
) -> int:
    return PLANS.get(
        strategie,
        {},
    ).get(
        "bonus_achat",
        {},
    ).get(
        nom,
        0,
    )


# =========================================================
# SYNERGIES
# =========================================================

def bonus_synergies(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    disponibles = piles_presentes(
        game
    )

    meilleur_bonus = 0

    for synergie in SYNERGIES_ACHAT:
        cartes = synergie["cartes"]

        if nom not in cartes:
            continue

        bonus_carte = synergie.get(
            "bonus",
            {},
        ).get(
            nom,
            0,
        )

        if bonus_carte <= 0:
            continue

        autres = [
            carte
            for carte in cartes
            if carte != nom
        ]

        synergie_active = any(
            quantite_achetee(
                game_id,
                autre,
            ) > 0
            for autre in autres
        )

        synergie_possible = any(
            autre in disponibles
            for autre in autres
        )

        # Synergie réellement construite :
        # bonus complet.
        if synergie_active:
            bonus_effectif = bonus_carte

        # Synergie seulement disponible
        # dans le royaume :
        # petit bonus de potentiel.
        elif synergie_possible:
            bonus_effectif = round(
                bonus_carte * 0.30
            )

        else:
            bonus_effectif = 0

        meilleur_bonus = max(
            meilleur_bonus,
            bonus_effectif,
        )

    return meilleur_bonus

# =========================================================
# OBJECTIF D'ACTIONS
# =========================================================

def seuil_actions_cible(
    game: Game,
    game_id: str,
) -> int:
    strategie = plan_actuel(
        game,
        game_id,
    )

    cible = (
        NB_ACTIONS_AVANT_ECONOMIE
    )

    # Plan construit autour d'une carte
    # Action (Witch, Smithy...) : une
    # action de plus.
    if PLANS.get(
        strategie,
        {},
    ).get(
        "carte_cle"
    ) is not None:
        cible += 1

    if (
        taille_deck(
            game_id
        )
        >= 22
    ):
        cible += 1

    return min(
        cible,
        MAX_TOTAL_ACTIONS,
    )


def max_total_actions_dynamique(
    game: Game,
    game_id: str,
) -> int:
    cible = seuil_actions_cible(
        game,
        game_id,
    )

    maximum = max(
        MAX_TOTAL_ACTIONS_BASE,
        cible,
    )

    if (
        nombre_achetees_parmi(
            game_id,
            CARTES_PIOCHE,
        )
        >= 2
    ):
        maximum += 1

    return min(
        maximum,
        MAX_TOTAL_ACTIONS,
    )


# =========================================================
# ÉCONOMIE
# =========================================================

def bonus_economie(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    bonus = 0

    silver = quantite_economique(
        game_id,
        "silver",
    )

    gold = quantite_economique(
        game_id,
        "gold",
    )

    total_actions = (
        nombre_total_actions(
            game_id
        )
    )

    # -----------------------------------------------------
    # Silver
    # -----------------------------------------------------

    if nom == "silver":
        if silver == 0:
            bonus += 6

        elif silver == 1:
            bonus += 4

        elif silver >= 6:
            bonus -= 8

    # -----------------------------------------------------
    # Gold
    # -----------------------------------------------------

    elif nom == "gold":
        if silver >= 2:
            bonus += 8

        if gold == 0:
            bonus += 6

        elif gold == 1:
            bonus += 4

    # -----------------------------------------------------
    # Éviter de construire 5 actions avant d'avoir
    # une économie correcte.
    # -----------------------------------------------------

    if (
        nom in MAX_CARTES_ACTION
        and total_actions
        >= NB_ACTIONS_AVANT_ECONOMIE
        and (
            silver
            + gold
        ) < 3
    ):
        bonus -= 8

    return bonus


# =========================================================
# GARDENS
# =========================================================

def bonus_gardens(
    game: Game,
    game_id: str,
) -> int:
    taille = taille_deck(
        game_id
    )

    nb_gardens = quantite_achetee(
        game_id,
        "gardens",
    )

    points_avant = (
        taille // 10
    )

    points_apres = (
        (taille + 1) // 10
    )

    # VP du nouveau Gardens.
    vp_marginaux = points_apres

    # Si on passe 19 -> 20,
    # 29 -> 30, etc.,
    # les Gardens déjà présents
    # gagnent également un point.
    if (
        points_apres
        > points_avant
    ):
        vp_marginaux += (
            nb_gardens
        )

    bonus = (
        vp_marginaux * 10
    )

    # Gardens beaucoup trop tôt.
    if taille < 20:
        bonus -= 20

    if (
        taille < 24
        and nb_gardens == 0
    ):
        bonus -= 10

    # Les gros decks commencent
    # réellement à valoriser Gardens.
    if taille >= 30:
        bonus += 8

    # En quatre joueurs,
    # on exige un peu plus de deck
    # avant de lancer Gardens.
    if (
        len(
            game.players
        ) >= 4
        and taille < 26
    ):
        bonus -= 10

    # Cartes qui font naturellement
    # grossir le deck.
    bonus += min(
        8,
        quantite_achetee(
            game_id,
            "distantshore",
        ) * 4,
    )

    bonus += min(
        6,
        quantite_achetee(
            game_id,
            "bandit",
        ) * 3,
    )

    return bonus


# =========================================================
# PHASE DE PARTIE
# =========================================================

def bonus_phase_partie(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    provinces = provinces_restantes(
        game
    )

    nb_joueurs = len(
        game.players
    )

    bonus = 0

    fin_urgente = (
        provinces
        <= max(
            1,
            nb_joueurs - 1,
        )
        or risque_fin_par_piles(
            game,
            game_id,
        )
        or nombre_piles_vides(
            game,
            game_id,
        ) >= 2
    )

    # Compromis trouvé après le test :
    # +3 verdissait beaucoup trop tôt.
    fin_normale = (
        provinces
        <= nb_joueurs + 2
    )

    if fin_urgente:
        if nom == "province":
            bonus += 300

        elif nom == "duchy":
            bonus += 350

        elif nom == "estate":
            bonus += 220

        elif nom == "gardens":
            bonus += 180

        elif nom in {
            "gold",
            "silver",
        }:
            bonus -= 35

        elif nom in (
            MAX_CARTES_ACTION
        ):
            bonus -= 40

    elif fin_normale:
        if nom == "province":
            bonus += 300

        elif nom == "duchy":
            bonus += 80

        elif nom == "estate":
            bonus += 15

        elif nom == "gardens":
            bonus += 50

        elif nom == "gold":
            bonus -= 8

        elif nom == "silver":
            bonus -= 12

        elif nom in (
            MAX_CARTES_ACTION
        ):
            bonus -= 15

    return bonus


# =========================================================
# SITUATION AU SCORE
# =========================================================

def bonus_situation_score(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    ecart = ecart_score(
        game
    )

    provinces = provinces_restantes(
        game
    )

    nb_joueurs = len(
        game.players
    )

    bonus = 0

    # -----------------------------------------------------
    # Nous sommes nettement devant :
    # convertir l'avantage en VP.
    # -----------------------------------------------------

    if ecart >= 8:
        if nom == "province":
            bonus += 20

        elif nom == "duchy":
            bonus += 10

        elif nom == "estate":
            bonus += 5

    # -----------------------------------------------------
    # Nous sommes nettement derrière.
    #
    # IMPORTANT :
    # cette logique ne doit fonctionner
    # que s'il reste réellement assez
    # de Provinces.
    # -----------------------------------------------------

    if (
        ecart <= -8
        and provinces
        > nb_joueurs + 4
    ):
        if nom == "gold":
            bonus += 10

        elif nom == "laboratory":
            bonus += 8

        elif nom == "smithy":
            bonus += 6

        elif nom == "duchy":
            bonus -= 8

        elif nom == "estate":
            bonus -= 10

    return bonus


# =========================================================
# STRUCTURE DU DECK
# =========================================================

def bonus_structure(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    bonus = 0

    terminaux = nombre_achetees_parmi(
        game_id,
        CARTES_TERMINALES,
    )

    supports = nombre_achetees_parmi(
        game_id,
        CARTES_SUPPORT_ACTIONS,
    )

    nb_pioche = nombre_achetees_parmi(
        game_id,
        CARTES_PIOCHE,
    )

    nb_pioche_forte = nombre_achetees_parmi(
        game_id,
        CARTES_PIOCHE_FORTE,
    )

    militia = quantite_achetee(
        game_id,
        "militia",
    )

    # =====================================================
    # NOUVEAU :
    # LE DECK N'A AUCUNE PIOCHE
    # =====================================================

    if nb_pioche == 0:
        if nom == "laboratory":
            bonus += 15

        elif nom == "smithy":
            bonus += 10

        elif nom == "councilroom":
            bonus += 10

        elif nom == "witch":
            bonus += 8

        elif nom == "distantshore":
            bonus += 8

        # On possède déjà notre attaque :
        # la deuxième Militia ne doit pas
        # remplacer notre première vraie
        # carte de pioche.
        if (
            nom == "militia"
            and militia >= 1
        ):
            bonus -= 12

    # =====================================================
    # Peu de pioche forte
    # =====================================================

    elif nb_pioche_forte == 0:
        if nom == "laboratory":
            bonus += 10

        elif nom == "smithy":
            bonus += 7

        elif nom == "councilroom":
            bonus += 7

    # =====================================================
    # Trop de terminaux
    # =====================================================

    if terminaux > supports:
        if nom in (
            CARTES_SUPPORT_ACTIONS
        ):
            bonus += min(
                18,
                (
                    terminaux
                    - supports
                ) * 6,
            )

        if (
            nom
            in CARTES_TERMINALES
        ):
            bonus -= min(
                28,
                (
                    terminaux
                    - supports
                ) * 8,
            )

    # =====================================================
    # Trop de supports sans payload
    # =====================================================

    if (
        supports
        > terminaux + 2
    ):
        if nom in (
            CARTES_SUPPORT_ACTIONS
        ):
            bonus -= 10

        if nom in {
            "laboratory",
            "smithy",
            "councilroom",
            "witch",
        }:
            bonus += 8

    return bonus


# =========================================================
# BONUS SELON LA MAIN
# =========================================================

def bonus_main(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    moi = trouver_mon_joueur(
        game
    )

    if (
        moi is None
        or moi.hand is None
    ):
        return 0

    cartes_main = {
        str(carte)
        for carte, quantite
        in moi.hand.quantities.items()
        if quantite > 0
    }

    # Si une carte terminale est
    # présente dans la main, les cartes
    # +Actions ont un petit intérêt
    # supplémentaire.
    if (
        cartes_main
        & CARTES_TERMINALES
        and nom
        in CARTES_SUPPORT_ACTIONS
    ):
        return 5

    return 0


# =========================================================
# BONUS SPÉCIFIQUES
# =========================================================

def bonus_carte_specifique(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    etat = obtenir_etat(
        game_id
    )

    tour = int(
        etat.get(
            "tour",
            0,
        )
    )

    bonus = 0

    # -----------------------------------------------------
    # Gardens
    # -----------------------------------------------------

    if nom == "gardens":
        bonus += bonus_gardens(
            game,
            game_id,
        )

    # -----------------------------------------------------
    # Militia
    # -----------------------------------------------------

    elif nom == "militia":
        if tour <= 8:
            bonus += 7

        elif tour >= 16:
            bonus -= 8

        # Anciennement *4.
        # Réduit après l'analyse des
        # défaites multijoueurs.
        bonus += max(
            0,
            len(
                game.players
            ) - 2,
        ) * 2

    # -----------------------------------------------------
    # Witch
    # -----------------------------------------------------

    elif nom == "witch":
        curses = curses_restantes(
            game
        )

        if curses > 0:
            bonus += min(
                14,
                curses // 3,
            )

        bonus += max(
            0,
            len(
                game.players
            ) - 2,
        ) * 3

        if curses <= 3:
            bonus -= 12

    # -----------------------------------------------------
    # Bandit
    # -----------------------------------------------------

    elif nom == "bandit":
        bonus += max(
            0,
            len(
                game.players
            ) - 2,
        ) * 3

        if quantite_stock(
            game,
            "gold",
        ) <= 5:
            bonus -= 12

    # -----------------------------------------------------
    # Laboratory
    # -----------------------------------------------------

    elif nom == "laboratory":
        # Très bon premier moteur.
        if (
            quantite_achetee(
                game_id,
                "laboratory",
            )
            == 0
        ):
            bonus += 5

    # -----------------------------------------------------
    # Smithy
    # -----------------------------------------------------

    elif nom == "smithy":
        # Smithy est forte,
        # mais terminale.
        if (
            nombre_achetees_parmi(
                game_id,
                CARTES_SUPPORT_ACTIONS,
            )
            >= 1
        ):
            bonus += 5

    # -----------------------------------------------------
    # Council Room
    # -----------------------------------------------------

    elif nom == "councilroom":
        if len(
            game.players
        ) >= 4:
            # Les adversaires piochent aussi.
            bonus -= 4

    # -----------------------------------------------------
    # Hireling
    # -----------------------------------------------------

    elif nom == "hireling":
        if tour <= 8:
            bonus += 7

        elif tour >= 16:
            bonus -= 12

        # La première Hireling achetée tôt
        # vaut plus qu'une Gold : +1 carte à
        # chaque tour jusqu'à la fin.
        if (
            quantite_achetee(
                game_id,
                "hireling",
            ) == 0
            and tour
            <= TOUR_MAX_PREMIER_HIRELING
        ):
            bonus += (
                BONUS_PREMIER_HIRELING
            )

    # -----------------------------------------------------
    # Bureaucrat : utile seulement à 4 joueurs
    # -----------------------------------------------------

    elif nom == "bureaucrat":
        if len(
            game.players
        ) >= 4:
            bonus += (
                BONUS_BUREAUCRAT_4_JOUEURS
            )

    # -----------------------------------------------------
    # Distant Shore
    # -----------------------------------------------------

    elif nom == "distantshore":
        if quantite_stock(
            game,
            "estate",
        ) > 0:
            bonus += 5

        if tour >= 16:
            bonus -= 8

    # -----------------------------------------------------
    # Chancellor
    # -----------------------------------------------------

    elif nom == "chancellor":
        if tour <= 6:
            bonus += 4

        if tour >= 12:
            bonus -= 8

    # -----------------------------------------------------
    # Woodcutter
    # -----------------------------------------------------

    elif nom == "woodcutter":
        if tour >= 12:
            bonus -= 8

    return bonus


# =========================================================
# SATURATION
# =========================================================

def malus_saturation(
    game: Game,
    game_id: str,
    nom: str,
) -> int:
    quantite = quantite_achetee(
        game_id,
        nom,
    )

    # -----------------------------------------------------
    # Silver
    # -----------------------------------------------------

    if nom == "silver":
        return max(
            0,
            quantite - 2,
        ) * 5

    # -----------------------------------------------------
    # Gold
    #
    # IMPORTANT :
    # Bandit doit compter.
    # -----------------------------------------------------

    if nom == "gold":
        richesse = (
            quantite_economique(
                game_id,
                "gold",
            )
        )

        malus = max(
            0,
            richesse - 4,
        ) * 5

        if richesse >= 8:
            malus += 10

        return malus

    # -----------------------------------------------------
    # Gardens
    # -----------------------------------------------------

    if nom == "gardens":
        malus = (
            quantite * 5
        )

        if quantite >= 3:
            malus += (
                quantite - 2
            ) * 5

        return malus

    # -----------------------------------------------------
    # Actions
    # -----------------------------------------------------

    return (
        quantite
        * MALUS_PAR_COPIE_ACTION.get(
            nom,
            0,
        )
    )


# =========================================================
# CALCUL DU POIDS FINAL
# =========================================================
#
# Les limites (nombre max de chaque carte Action, nombre
# total d'Actions) ne sont pas ici : choisir_achat()
# n'évalue même pas une carte qui les dépasse (voir
# strategy.carte_action_autorisee).
# =========================================================

def calculer_poids_achat(
    game: Game,
    game_id: str,
    nom: str,
    strategie: str,
) -> dict[str, Any]:
    base = (
        POIDS_BASE_ACHAT.get(
            nom,
            0,
        )
    )

    synergies = bonus_synergies(
        game,
        game_id,
        nom,
    )

    bonus_strat = (
        bonus_strategie(
            nom,
            strategie,
        )
        + bonus_carte_cle(
            game_id,
            nom,
        )
    )

    economie = bonus_economie(
        game,
        game_id,
        nom,
    )

    phase = bonus_phase_partie(
        game,
        game_id,
        nom,
    )

    score = bonus_situation_score(
        game,
        game_id,
        nom,
    )

    structure = bonus_structure(
        game,
        game_id,
        nom,
    )

    main = bonus_main(
        game,
        game_id,
        nom,
    )

    specifique = (
        bonus_carte_specifique(
            game,
            game_id,
            nom,
        )
    )

    saturation = (
        malus_saturation(
            game,
            game_id,
            nom,
        )
    )

    # Termine-t-on la partie en
    # gagnant, ou en perdant ?
    fin = bonus_fin_partie(
        game,
        game_id,
        nom,
    )

    total = (
        fin
        +
        base
        + synergies
        + bonus_strat
        + economie
        + phase
        + score
        + structure
        + main
        + specifique
        - saturation
    )

    return {
        "base":
            base,

        "synergies":
            synergies,

        "bonus_strategie":
            bonus_strat,

        "economie":
            economie,

        "phase":
            phase,

        "score":
            score,

        "structure":
            structure,

        "main":
            main,

        "specifique":
            specifique,

        "saturation":
            -saturation,

        "fin_partie":
            fin,

        "total":
            total,
    }