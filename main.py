import json
from typing import Annotated, Any

from dopynion.cards import Card
from dopynion.data_model import (
    CardName,
    CardNameAndHand,
    Game,
    Hand,
    MoneyCardsInHand,
    PossibleCards,
)
from fastapi import (
    Depends,
    FastAPI,
    Header,
    Request,
)
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
)
from pydantic import BaseModel

from config import (
    NOM_BOT_OFFICIEL,
    obtenir_nom_joueur,
)
from game_utils import (
    bot_officiel_en_face,
)
from logger_utils import (
    afficher_situation,
    initialiser_historique,
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


@app.middleware("http")
async def log_requests(
    request: Request,
    call_next,
):
    body = await request.body()

    if body:
        try:
            contenu = json.loads(body)
        except ValueError:
            contenu = body.decode(
                "utf-8",
                errors="replace",
            )
    else:
        contenu = None

    game_id = request.headers.get(
        "x-game-id"
    )

    affichage = (
        json.dumps(
            contenu,
            indent=2,
            ensure_ascii=False,
        )
        if contenu is not None
        else "(pas de contenu)"
    )

    print(
        f"\n>>> {request.method} "
        f"{request.url.path} "
        f"| partie={game_id}\n"
        f"{affichage}",
        flush=True,
    )

    return await call_next(request)


def log_decision(
    game_id: str,
    route: str,
    decision: Any,
) -> None:

    print(
        f">>> Décision ({route}) "
        f"partie={game_id} : "
        f"{decision}",
        flush=True,
    )


class DopynionResponseBool(BaseModel):
    game_id: str
    decision: bool


class DopynionResponseCardName(BaseModel):
    game_id: str
    decision: CardName


class DopynionResponseStr(BaseModel):
    game_id: str
    decision: str


def get_game_id(
    x_game_id: str = Header(
        description="ID of the game"
    ),
) -> str:

    return x_game_id


GameIdDependency = Annotated[
    str,
    Depends(get_game_id),
]


@app.exception_handler(Exception)
def unknown_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:

    print(
        exc.__class__.__name__,
        str(exc),
    )

    return JSONResponse(
        status_code=500,
        content={
            "message": "Oops!",
            "detail": str(exc),
            "name": exc.__class__.__name__,
        },
    )


@app.get(
    "/",
    response_class=HTMLResponse,
)
def root() -> str:
    return """
    <html>
        <body>
            <h1>Le 4ème Empire</h1>
            <p>Bot Dopynion actif.</p>
        </body>
    </html>
    """


@app.get("/name")
def name(request: Request) -> str:
    return obtenir_nom_joueur(
        request.headers.get("host", "")
    )


@app.get("/start_game")
def start_game(
    game_id: GameIdDependency,
) -> DopynionResponseStr:

    initialiser_partie(
        game_id
    )

    initialiser_historique(
        game_id
    )

    return DopynionResponseStr(
        game_id=game_id,
        decision="OK",
    )


@app.get("/start_turn")
def start_turn(
    game_id: GameIdDependency,
) -> DopynionResponseStr:

    etat = demarrer_tour(
        game_id
    )

    print(
        f">>> Nouveau tour "
        f"{etat['tour']} | "
        f"partie={game_id}",
        flush=True,
    )

    return DopynionResponseStr(
        game_id=game_id,
        decision="OK",
    )


@app.post("/play")
def play(
    game: Game,
    game_id: GameIdDependency,
) -> DopynionResponseStr:

    with verrou_partie(game_id):

        etat = obtenir_etat(
            game_id
        )

        afficher_situation(
            game,
            game_id,
        )

        if game.finished:
            decision = "END_TURN"

            log_decision(
                game_id,
                "/play",
                decision,
            )

            return DopynionResponseStr(
                game_id=game_id,
                decision=decision,
            )

        if bot_officiel_en_face(game):
            decision = "END_TURN"

            print(
                f">>> {NOM_BOT_OFFICIEL} "
                f"détecté : mode passif",
                flush=True,
            )

            log_decision(
                game_id,
                "/play",
                decision,
            )

            return DopynionResponseStr(
                game_id=game_id,
                decision=decision,
            )

        if (
            not etat["phase_achat"]
            and etat["actions_restantes"] > 0
        ):
            carte_action = choisir_action(
                game,
                game_id,
            )

            if carte_action is not None:
                appliquer_effet_action(
                    game_id,
                    carte_action,
                )

                decision = (
                    f"ACTION "
                    f"{carte_action.value}"
                )

                log_decision(
                    game_id,
                    "/play",
                    decision,
                )

                return DopynionResponseStr(
                    game_id=game_id,
                    decision=decision,
                )

            commencer_phase_achat(
                game,
                game_id,
            )

        elif not etat["phase_achat"]:
            commencer_phase_achat(
                game,
                game_id,
            )

        if etat["achats_restants"] > 0:

            carte = choisir_achat(
                game,
                game_id,
            )

            if carte is not None:
                cout = Card.class_(
                    carte
                ).cost

                etat[
                    "argent_restant"
                ] -= cout

                etat[
                    "achats_restants"
                ] -= 1

                enregistrer_achat(
                    game_id,
                    carte.value.lower(),
                )

                decision = (
                    f"BUY {carte.value}"
                )

                log_decision(
                    game_id,
                    "/play",
                    decision,
                )

                return DopynionResponseStr(
                    game_id=game_id,
                    decision=decision,
                )

        decision = "END_TURN"

        log_decision(
            game_id,
            "/play",
            decision,
        )

        return DopynionResponseStr(
            game_id=game_id,
            decision=decision,
        )


@app.get("/end_game")
def end_game(
    game_id: GameIdDependency,
) -> DopynionResponseStr:

    terminer_historique(
        game_id
    )

    supprimer_partie(
        game_id
    )

    return DopynionResponseStr(
        game_id=game_id,
        decision="OK",
    )


@app.post(
    "/confirm_discard_card_from_hand"
)
async def confirm_discard_card_from_hand(
    game_id: GameIdDependency,
    _decision_input: CardNameAndHand,
) -> DopynionResponseBool:

    return DopynionResponseBool(
        game_id=game_id,
        decision=True,
    )


@app.post(
    "/discard_card_from_hand"
)
async def discard_card_from_hand(
    game_id: GameIdDependency,
    decision_input: Hand,
) -> DopynionResponseCardName:

    return DopynionResponseCardName(
        game_id=game_id,
        decision=decision_input.hand[0],
    )


@app.post(
    "/confirm_trash_card_from_hand"
)
async def confirm_trash_card_from_hand(
    game_id: GameIdDependency,
    _decision_input: CardNameAndHand,
) -> DopynionResponseBool:

    return DopynionResponseBool(
        game_id=game_id,
        decision=True,
    )


@app.post(
    "/trash_card_from_hand"
)
async def trash_card_from_hand(
    game_id: GameIdDependency,
    decision_input: Hand,
) -> DopynionResponseCardName:

    return DopynionResponseCardName(
        game_id=game_id,
        decision=decision_input.hand[0],
    )


@app.post(
    "/confirm_discard_deck"
)
async def confirm_discard_deck(
    game_id: GameIdDependency,
) -> DopynionResponseBool:

    return DopynionResponseBool(
        game_id=game_id,
        decision=True,
    )


@app.post(
    "/choose_card_to_receive_in_discard"
)
async def choose_card_to_receive_in_discard(
    game_id: GameIdDependency,
    decision_input: PossibleCards,
) -> DopynionResponseCardName:

    return DopynionResponseCardName(
        game_id=game_id,
        decision=decision_input.possible_cards[0],
    )


@app.post(
    "/choose_card_to_receive_in_deck"
)
async def choose_card_to_receive_in_deck(
    game_id: GameIdDependency,
    decision_input: PossibleCards,
) -> DopynionResponseCardName:

    return DopynionResponseCardName(
        game_id=game_id,
        decision=decision_input.possible_cards[0],
    )


@app.post(
    "/skip_card_reception_in_hand"
)
async def skip_card_reception_in_hand(
    game_id: GameIdDependency,
    _decision_input: CardNameAndHand,
) -> DopynionResponseBool:

    return DopynionResponseBool(
        game_id=game_id,
        decision=True,
    )


@app.post(
    "/trash_money_card_for_better_money_card"
)
async def trash_money_card_for_better_money_card(
    game_id: GameIdDependency,
    decision_input: MoneyCardsInHand,
) -> DopynionResponseCardName:

    return DopynionResponseCardName(
        game_id=game_id,
        decision=decision_input.money_in_hand[0],
    )