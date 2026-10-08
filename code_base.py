import html
import json
import threading
from datetime import datetime
from pathlib import Path
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
from fastapi import Depends, FastAPI, Header, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI()

#####################################################
# Logs : console + fichier logs.json (meme dossier que ce fichier)
#####################################################

FICHIER_LOGS = Path(__file__).resolve().parent / "logs.json"
_verrou_logs = threading.Lock()  # evite que deux requetes ecrivent en meme temps


def ecrire_situation(situation: dict[str, Any]) -> None:
    """Ecrase logs.json avec la derniere situation de la partie
    (le fichier ne contient toujours qu'une seule situation, la plus recente)."""
    situation = {"horodatage": datetime.now().isoformat(timespec="seconds"), **situation}
    with _verrou_logs:
        FICHIER_LOGS.write_text(
            json.dumps(situation, indent=2, ensure_ascii=False), encoding="utf-8"
        )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    contenu: Any
    if body:
        try:
            contenu = json.loads(body)
        except ValueError:
            contenu = body.decode("utf-8", errors="replace")
    else:
        contenu = None

    game_id = request.headers.get("x-game-id")
    affichage = (
        json.dumps(contenu, indent=2, ensure_ascii=False)
        if contenu is not None
        else "(pas de contenu)"
    )
    print(
        f"\n>>> {request.method} {request.url.path} | partie={game_id}\n{affichage}",
        flush=True,
    )
    return await call_next(request)


def log_decision(game_id: str, route: str, decision: Any) -> None:
    """Affiche dans la console la decision renvoyee au serveur."""
    print(f">>> Décision ({route}) partie={game_id} : {decision}", flush=True)


#####################################################
# Data model for responses
#####################################################


class DopynionResponseBool(BaseModel):
    game_id: str
    decision: bool


class DopynionResponseCardName(BaseModel):
    game_id: str
    decision: CardName


class DopynionResponseStr(BaseModel):
    game_id: str
    decision: str


#####################################################
# Getter for the game identifier
#####################################################


def get_game_id(x_game_id: str = Header(description="ID of the game")) -> str:
    return x_game_id


GameIdDependency = Annotated[str, Depends(get_game_id)]


#####################################################
# Error management
#####################################################


@app.exception_handler(Exception)
def unknown_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    print(exc.__class__.__name__, str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "message": "Oops!",
            "detail": str(exc),
            "name": exc.__class__.__name__,
        },
    )


#####################################################
# Template extra bonus
#####################################################


# The root of the website shows the code of the website
@app.get("/", response_class=HTMLResponse)
def root() -> str:
    header = (
        "<html><head><title>Dopynion template</title></head><body>"
        "<h1>Dopynion documentation</h1>"
        "<h2>API documentation</h2>"
        '<p><a href="/docs">Read the documentation.</a></p>'
        "<h2>Code template</h2>"
        "<p>The code of this website is:</p>"
        "<pre>"
    )
    footer = "</pre></body></html>"
    return header + html.escape(Path(__file__).read_text(encoding="utf-8")) + footer


#####################################################
# The code of the strategy
#####################################################

NOM_JOUEUR = "Le 4ème Empire"

# Memorise, pour chaque partie, si on a deja achete pendant le tour en cours
achat_fait: dict[str, bool] = {}


@app.get("/name")
def name() -> str:
    return NOM_JOUEUR


@app.get("/start_game")
def start_game(game_id: GameIdDependency) -> DopynionResponseStr:
    achat_fait[game_id] = False
    return DopynionResponseStr(game_id=game_id, decision="OK")


@app.get("/start_turn")
def start_turn(game_id: GameIdDependency) -> DopynionResponseStr:
    achat_fait[game_id] = False  # nouveau tour : on n'a encore rien achete
    return DopynionResponseStr(game_id=game_id, decision="OK")


def afficher_situation(game: Game, game_id: str) -> None:
    """Affiche un resume de la partie (main, argent, achats possibles, scores, reserve)
    dans la console ET l'enregistre dans logs.json."""
    # Mon joueur : celui dont on connait la main (sinon, on cherche par le nom)
    moi = next((p for p in game.players if p.hand is not None), None)
    if moi is None:
        moi = next((p for p in game.players if p.name == NOM_JOUEUR), None)

    situation: dict[str, Any] = {"partie": game_id}

    print("------------- SITUATION -------------")
    if moi is not None and moi.hand is not None:
        main = moi.hand.quantities
        nb_cartes = sum(main.values())
        argent = sum(Card.class_(c).money * n for c, n in main.items())
        actions = [c.value for c in main if Card.class_(c).is_action]
        achetables = [
            c.value
            for c, n in game.stock.quantities.items()
            if n > 0 and Card.class_(c).cost <= argent
        ]

        print(f"Joueur        : {moi.name} (score {moi.score})")
        print(f"Cartes en main: {nb_cartes}")
        for carte, n in main.items():
            infos = Card.class_(carte)
            print(f"   - {n} x {carte.value:<15} (argent {infos.money}, coût {infos.cost})")
        print(f"Argent dispo  : {argent}")
        print(f"Cartes action : {actions or 'aucune'}")
        print(f"Je peux acheter : {achetables or 'rien'}")

        situation.update(
            {
                "joueur": moi.name,
                "score": moi.score,
                "nb_cartes_en_main": nb_cartes,
                "main": [
                    {
                        "carte": carte.value,
                        "quantite": n,
                        "argent": Card.class_(carte).money,
                        "cout": Card.class_(carte).cost,
                    }
                    for carte, n in main.items()
                ],
                "argent_dispo": argent,
                "cartes_action": actions,
                "achetables": achetables,
            }
        )
    else:
        print("Ma main n'a pas été trouvée dans la trame.")
        situation["main"] = None

    print("Scores        :")
    for p in game.players:
        print(f"   - {p.name:<20} {p.score}")

    print("Réserve (stock):")
    for carte, n in game.stock.quantities.items():
        print(f"   - {carte.value:<15} x{n:<3} (coût {Card.class_(carte).cost})")
    print(f"Partie finie  : {game.finished}")
    print("-------------------------------------", flush=True)

    situation.update(
        {
            "scores": {p.name: p.score for p in game.players},
            "reserve": {
                carte.value: {"quantite": n, "cout": Card.class_(carte).cost}
                for carte, n in game.stock.quantities.items()
            },
            "partie_finie": game.finished,
        }
    )
    ecrire_situation(situation)


@app.post("/play")
def play(game: Game, game_id: GameIdDependency) -> DopynionResponseStr:
    afficher_situation(game, game_id)

    # Premier appel du tour : on achete un copper
    if not achat_fait.get(game_id, False):
        achat_fait[game_id] = True
        decision = "BUY copper"
    else:
        # Achat deja fait : on termine le tour
        decision = "END_TURN"

    log_decision(game_id, "/play", decision)
    return DopynionResponseStr(game_id=game_id, decision=decision)


@app.get("/end_game")
def end_game(game_id: GameIdDependency) -> DopynionResponseStr:
    achat_fait.pop(game_id, None)  # on libere la memoire de cette partie
    return DopynionResponseStr(game_id=game_id, decision="OK")


@app.post("/confirm_discard_card_from_hand")
async def confirm_discard_card_from_hand(
    game_id: GameIdDependency,
    _decision_input: CardNameAndHand,
) -> DopynionResponseBool:
    return DopynionResponseBool(game_id=game_id, decision=True)


@app.post("/discard_card_from_hand")
async def discard_card_from_hand(
    game_id: GameIdDependency,
    decision_input: Hand,
) -> DopynionResponseCardName:
    return DopynionResponseCardName(game_id=game_id, decision=decision_input.hand[0])


@app.post("/confirm_trash_card_from_hand")
async def confirm_trash_card_from_hand(
    game_id: GameIdDependency,
    _decision_input: CardNameAndHand,
) -> DopynionResponseBool:
    return DopynionResponseBool(game_id=game_id, decision=True)


@app.post("/trash_card_from_hand")
async def trash_card_from_hand(
    game_id: GameIdDependency,
    decision_input: Hand,
) -> DopynionResponseCardName:
    return DopynionResponseCardName(game_id=game_id, decision=decision_input.hand[0])


@app.post("/confirm_discard_deck")
async def confirm_discard_deck(
    game_id: GameIdDependency,
) -> DopynionResponseBool:
    return DopynionResponseBool(game_id=game_id, decision=True)


@app.post("/choose_card_to_receive_in_discard")
async def choose_card_to_receive_in_discard(
    game_id: GameIdDependency,
    decision_input: PossibleCards,
) -> DopynionResponseCardName:
    return DopynionResponseCardName(
        game_id=game_id,
        decision=decision_input.possible_cards[0],
    )


@app.post("/choose_card_to_receive_in_deck")
async def choose_card_to_receive_in_deck(
    game_id: GameIdDependency,
    decision_input: PossibleCards,
) -> DopynionResponseCardName:
    return DopynionResponseCardName(
        game_id=game_id,
        decision=decision_input.possible_cards[0],
    )


@app.post("/skip_card_reception_in_hand")
async def skip_card_reception_in_hand(
    game_id: GameIdDependency,
    _decision_input: CardNameAndHand,
) -> DopynionResponseBool:
    return DopynionResponseBool(game_id=game_id, decision=True)


@app.post("/trash_money_card_for_better_money_card")
async def trash_money_card_for_better_money_card(
    game_id: GameIdDependency,
    decision_input: MoneyCardsInHand,
) -> DopynionResponseCardName:
    return DopynionResponseCardName(
        game_id=game_id,
        decision=decision_input.money_in_hand[0],
    )