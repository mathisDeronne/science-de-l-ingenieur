from typing import Any

from fastapi import (
    FastAPI,
    Header,
    Request,
)
from fastapi.responses import (
    HTMLResponse,
)
from pydantic import BaseModel

from dopynion.cards import Card
from dopynion.data_model import (
    Game,
    Hand,
    MoneyCardsInHand,
    PossibleCards,
)

from config import obtenir_nom_joueur
from game_utils import (
    bot_officiel_en_face,
)
from logger_utils import (
    afficher_situation,
    enregistrer_decision,
    initialiser_historique,
    marquer_abandon,
    terminer_historique,
)
from state import (
    demarrer_tour,
    enregistrer_achat,
    initialiser_partie,
    obtenir_etat,
    supprimer_partie,
    verrou_partie,
)
from strategy import (
    appliquer_effet_action,
    choisir_action,
    choisir_achat,
    commencer_phase_achat,
)


app = FastAPI()


# =========================================================
# RÉPONSES ATTENDUES PAR L'ARBITRE
# =========================================================

class DopynionResponseStr(
    BaseModel
):
    game_id: str
    decision: str


class DopynionResponseCardName(
    BaseModel
):
    game_id: str
    decision: str


class DopynionResponseBool(
    BaseModel
):
    game_id: str
    decision: bool


# =========================================================
# INFORMATIONS GÉNÉRALES
# =========================================================

@app.get(
    "/",
    response_class=HTMLResponse,
)
def root(
    request: Request,
) -> str:
    nom = obtenir_nom_joueur(
        request.headers.get(
            "host",
            "",
        )
    )

    return f"""
    <html>
        <body>
            <h1>{nom}</h1>
            <p>Bot Dopynion actif.</p>
        </body>
    </html>
    """


@app.get("/name")
def name(
    request: Request,
) -> str:
    return obtenir_nom_joueur(
        request.headers.get(
            "host",
            "",
        )
    )


# =========================================================
# GESTION PARTIE
# =========================================================

@app.get("/start_game")
def start_game(
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> str:
    initialiser_partie(
        x_game_id
    )

    initialiser_historique(
        x_game_id
    )

    return "OK"


@app.get("/start_turn")
def start_turn(
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> str:
    demarrer_tour(
        x_game_id
    )

    return "OK"


@app.post("/play")
def play(
    game: Game,
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> DopynionResponseStr:
    with verrou_partie(
        x_game_id
    ):
        etat = obtenir_etat(
            x_game_id
        )

        afficher_situation(
            game,
            x_game_id,
        )

        # Partie déjà terminée
        if game.finished:
            decision = "END_TURN"

            enregistrer_decision(
                x_game_id,
                etat["tour"],
                decision,
            )

            return DopynionResponseStr(
                game_id=x_game_id,
                decision=decision,
            )

        # Protection :
        # le bot dev ne joue jamais
        # contre le bot officiel.
        if bot_officiel_en_face(
            game
        ):
            marquer_abandon(
                x_game_id,
                "bot_officiel_en_face",
            )

            decision = "END_TURN"

            enregistrer_decision(
                x_game_id,
                etat["tour"],
                decision,
            )

            return DopynionResponseStr(
                game_id=x_game_id,
                decision=decision,
            )

        # -------------------------
        # PHASE ACTION
        # -------------------------

        action = choisir_action(
            game,
            x_game_id,
        )

        if action is not None:
            appliquer_effet_action(
                game,
                x_game_id,
                action,
            )

            decision = (
                f"ACTION "
                f"{action.value}"
            )

            enregistrer_decision(
                x_game_id,
                etat["tour"],
                decision,
            )

            return DopynionResponseStr(
                game_id=x_game_id,
                decision=decision,
            )

        # -------------------------
        # PHASE ACHAT
        # -------------------------

        commencer_phase_achat(
            game,
            x_game_id,
        )

        achat = choisir_achat(
            game,
            x_game_id,
        )

        if achat is not None:
            classe = Card.class_(
                achat
            )

            etat[
                "argent_restant"
            ] -= classe.cost

            etat[
                "achats_restants"
            ] -= 1

            enregistrer_achat(
                x_game_id,
                achat.value.lower(),
            )

            decision = (
                f"BUY "
                f"{achat.value}"
            )

            enregistrer_decision(
                x_game_id,
                etat["tour"],
                decision,
            )

            return DopynionResponseStr(
                game_id=x_game_id,
                decision=decision,
            )

        # -------------------------
        # FIN DU TOUR
        # -------------------------

        decision = "END_TURN"

        enregistrer_decision(
            x_game_id,
            etat["tour"],
            decision,
        )

        return DopynionResponseStr(
            game_id=x_game_id,
            decision=decision,
        )


@app.get("/end_game")
def end_game(
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> str:
    terminer_historique(
        x_game_id
    )

    supprimer_partie(
        x_game_id
    )

    return "OK"


# =========================================================
# OUTILS CALLBACKS
# =========================================================

def extraire_quantites(
    objet: Any,
    attribut: str,
) -> dict:
    contenu = getattr(
        objet,
        attribut,
        objet,
    )

    # Ancien format éventuel :
    # objet.quantities
    if hasattr(
        contenu,
        "quantities",
    ):
        return dict(
            contenu.quantities
        )

    # Dictionnaire déjà prêt
    if isinstance(
        contenu,
        dict,
    ):
        return contenu

    # Format réellement envoyé
    # actuellement par Dopynion :
    # [Copper, Estate, Silver, ...]
    if isinstance(
        contenu,
        (
            list,
            tuple,
        ),
    ):
        quantites = {}

        for carte in contenu:
            quantites[carte] = (
                quantites.get(
                    carte,
                    0,
                )
                + 1
            )

        return quantites

    # Dernier fallback pour
    # un éventuel iterable.
    try:
        cartes = list(
            contenu
        )

    except TypeError:
        return {}

    quantites = {}

    for carte in cartes:
        quantites[carte] = (
            quantites.get(
                carte,
                0,
            )
            + 1
        )

    return quantites

def choisir_carte_faible(
    quantites: dict,
):
    # Pour une défausse, on privilégie
    # les cartes mortes dans la main.
    ordre = [
        "curse",

        "estate",
        "gardens",
        "duchy",
        "province",

        "chancellor",
        "woodcutter",

        "copper",

        "silver",
        "gold",
    ]

    for nom in ordre:
        for carte, quantite in (
            quantites.items()
        ):
            if (
                quantite > 0
                and carte.value.lower()
                == nom
            ):
                return carte

    # Si aucune carte connue,
    # on renvoie quand même une carte
    # disponible pour ne pas provoquer
    # une commande vide.
    for carte, quantite in (
        quantites.items()
    ):
        if quantite > 0:
            return carte

    return None


def choisir_carte_a_trash(
    quantites: dict,
):
    ordre = [
        "curse",
        "estate",
        "copper",
    ]

    for nom in ordre:
        for carte, quantite in (
            quantites.items()
        ):
            if (
                quantite > 0
                and carte.value.lower()
                == nom
            ):
                return carte

    return None


def cartes_possibles(
    objet: Any,
    attribut: str,
) -> list:
    contenu = getattr(
        objet,
        attribut,
        objet,
    )

    if hasattr(
        contenu,
        "quantities",
    ):
        return [
            carte
            for carte, quantite
            in contenu.quantities.items()
            if quantite > 0
        ]

    if isinstance(
        contenu,
        dict,
    ):
        return [
            carte
            for carte, quantite
            in contenu.items()
            if quantite > 0
        ]

    try:
        return list(
            contenu
        )

    except TypeError:
        return []


def meilleure_carte(
    cartes: list,
):
    if not cartes:
        return None

    return max(
        cartes,
        key=lambda carte: (
            Card.class_(
                carte
            ).cost,

            Card.class_(
                carte
            ).money,
        ),
    )


# =========================================================
# MILITIA / DÉFAUSSE
# =========================================================

@app.post(
    "/confirm_discard_card_from_hand"
)
def confirm_discard_card_from_hand(
    hand: Hand,
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> DopynionResponseBool:
    return DopynionResponseBool(
        game_id=x_game_id,
        decision=True,
    )


@app.post(
    "/discard_card_from_hand"
)
def discard_card_from_hand(
    hand: Hand,
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> DopynionResponseCardName:
    quantites = extraire_quantites(
        hand,
        "hand",
    )

    carte = choisir_carte_faible(
        quantites
    )

    if carte is None:
        return DopynionResponseCardName(
            game_id=x_game_id,
            decision="NONE",
        )

    return DopynionResponseCardName(
        game_id=x_game_id,
        decision=carte.value,
    )

# =========================================================
# TRASH
# =========================================================

@app.post(
    "/confirm_trash_card_from_hand"
)
def confirm_trash_card_from_hand(
    hand: Hand,
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> DopynionResponseBool:
    quantites = extraire_quantites(
        hand,
        "hand",
    )

    decision = (
        choisir_carte_a_trash(
            quantites
        )
        is not None
    )

    return DopynionResponseBool(
        game_id=x_game_id,
        decision=decision,
    )


@app.post(
    "/trash_card_from_hand"
)
def trash_card_from_hand(
    hand: Hand,
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> DopynionResponseCardName:
    quantites = extraire_quantites(
        hand,
        "hand",
    )

    carte = choisir_carte_a_trash(
        quantites
    )

    if carte is None:
        return DopynionResponseCardName(
            game_id=x_game_id,
            decision="NONE",
        )

    return DopynionResponseCardName(
        game_id=x_game_id,
        decision=carte.value,
    )

# =========================================================
# CHANCELLOR
# =========================================================

@app.post(
    "/confirm_discard_deck"
)
def confirm_discard_deck(
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> DopynionResponseBool:
    # Pas assez d'informations pour
    # savoir si vider le deck est
    # avantageux.
    return DopynionResponseBool(
        game_id=x_game_id,
        decision=False,
    )


# =========================================================
# RÉCEPTION DE CARTES
# =========================================================

@app.post(
    "/choose_card_to_receive_in_discard"
)
def choose_card_to_receive_in_discard(
    possible_cards: PossibleCards,
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> DopynionResponseCardName:
    cartes = cartes_possibles(
        possible_cards,
        "possible_cards",
    )

    carte = meilleure_carte(
        cartes
    )

    if carte is None:
        return DopynionResponseCardName(
            game_id=x_game_id,
            decision="NONE",
        )

    return DopynionResponseCardName(
        game_id=x_game_id,
        decision=carte.value,
    )

@app.post(
    "/choose_card_to_receive_in_deck"
)
def choose_card_to_receive_in_deck(
    possible_cards: PossibleCards,
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> DopynionResponseCardName:
    cartes = cartes_possibles(
        possible_cards,
        "possible_cards",
    )

    carte = meilleure_carte(
        cartes
    )

    if carte is None:
        return DopynionResponseCardName(
            game_id=x_game_id,
            decision="NONE",
        )

    return DopynionResponseCardName(
        game_id=x_game_id,
        decision=carte.value,
    )

@app.post(
    "/skip_card_reception_in_hand"
)
def skip_card_reception_in_hand(
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> DopynionResponseBool:
    return DopynionResponseBool(
        game_id=x_game_id,
        decision=False,
    )


# =========================================================
# CARTE D'ARGENT À TRASH
# =========================================================

@app.post(
    "/trash_money_card_for_better_money_card"
)
def trash_money_card_for_better_money_card(
    money_cards: MoneyCardsInHand,
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> DopynionResponseCardName:
    quantites = extraire_quantites(
        money_cards,
        "money_in_hand",
    )

    for nom in (
        "copper",
        "silver",
        "gold",
    ):
        for carte, quantite in (
            quantites.items()
        ):
            if (
                quantite > 0
                and carte.value.lower()
                == nom
            ):
                return DopynionResponseCardName(
                    game_id=x_game_id,
                    decision=carte.value,
                )

    return DopynionResponseCardName(
        game_id=x_game_id,
        decision="NONE",
    )