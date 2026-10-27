from typing import Any

from fastapi import (
    FastAPI,
    Header,
    Request,
)
from fastapi.responses import (
    HTMLResponse,
)

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
) -> str:
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

        if game.finished:
            enregistrer_decision(
                x_game_id,
                etat["tour"],
                "END_TURN",
            )

            return "END_TURN"

        if bot_officiel_en_face(
            game
        ):
            marquer_abandon(
                x_game_id,
                "bot_officiel_en_face",
            )

            enregistrer_decision(
                x_game_id,
                etat["tour"],
                "END_TURN",
            )

            return "END_TURN"

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

            return decision

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

            return decision

        enregistrer_decision(
            x_game_id,
            etat["tour"],
            "END_TURN",
        )

        return "END_TURN"


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


def extraire_quantites(
    objet: Any,
    attribut: str,
) -> dict:
    contenu = getattr(
        objet,
        attribut,
        objet,
    )

    if hasattr(
        contenu,
        "quantities",
    ):
        return contenu.quantities

    if isinstance(
        contenu,
        dict,
    ):
        return contenu

    return {}


def choisir_carte_faible(
    quantites: dict,
):
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


@app.post(
    "/confirm_discard_card_from_hand"
)
def confirm_discard_card_from_hand(
    hand: Hand,
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> bool:
    return True


@app.post(
    "/discard_card_from_hand"
)
def discard_card_from_hand(
    hand: Hand,
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> str:
    quantites = extraire_quantites(
        hand,
        "hand",
    )

    carte = choisir_carte_faible(
        quantites
    )

    if carte is None:
        return ""

    return carte.value


@app.post(
    "/confirm_trash_card_from_hand"
)
def confirm_trash_card_from_hand(
    hand: Hand,
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> bool:
    quantites = extraire_quantites(
        hand,
        "hand",
    )

    return (
        choisir_carte_a_trash(
            quantites
        )
        is not None
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
) -> str:
    quantites = extraire_quantites(
        hand,
        "hand",
    )

    carte = choisir_carte_a_trash(
        quantites
    )

    if carte is None:
        carte = choisir_carte_faible(
            quantites
        )

    if carte is None:
        return ""

    return carte.value


@app.post(
    "/confirm_discard_deck"
)
def confirm_discard_deck(
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> bool:
    # Chancellor :
    # on refuse pour l'instant de
    # défausser aveuglément tout le deck.
    return False


@app.post(
    "/choose_card_to_receive_in_discard"
)
def choose_card_to_receive_in_discard(
    possible_cards: PossibleCards,
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> str:
    cartes = cartes_possibles(
        possible_cards,
        "possible_cards",
    )

    carte = meilleure_carte(
        cartes
    )

    if carte is None:
        return ""

    return carte.value


@app.post(
    "/choose_card_to_receive_in_deck"
)
def choose_card_to_receive_in_deck(
    possible_cards: PossibleCards,
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> str:
    cartes = cartes_possibles(
        possible_cards,
        "possible_cards",
    )

    carte = meilleure_carte(
        cartes
    )

    if carte is None:
        return ""

    return carte.value


@app.post(
    "/skip_card_reception_in_hand"
)
def skip_card_reception_in_hand(
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> bool:
    return False


@app.post(
    "/trash_money_card_for_better_money_card"
)
def trash_money_card_for_better_money_card(
    money_cards: MoneyCardsInHand,
    x_game_id: str = Header(
        ...,
        alias="x-game-id",
    ),
) -> str:
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
                return carte.value

    return ""