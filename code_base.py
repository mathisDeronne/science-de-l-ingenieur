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
# Logs : console + fichier logs.json
#####################################################

FICHIER_LOGS = Path(__file__).resolve().parent / "logs.json"
_verrou_logs = threading.Lock()


def ecrire_situation(situation: dict[str, Any]) -> None:
    """Ecrase logs.json avec la situation la plus recente."""
    situation = {
        "horodatage": datetime.now().isoformat(timespec="seconds"),
        **situation,
    }

    with _verrou_logs:
        FICHIER_LOGS.write_text(
            json.dumps(situation, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()

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
    """Affiche la decision envoyee a l'arbitre."""
    print(
        f">>> Décision ({route}) partie={game_id} : {decision}",
        flush=True,
    )


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


def get_game_id(
    x_game_id: str = Header(description="ID of the game"),
) -> str:
    return x_game_id


GameIdDependency = Annotated[str, Depends(get_game_id)]


#####################################################
# Error management
#####################################################


@app.exception_handler(Exception)
def unknown_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:

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

    return (
        header
        + html.escape(Path(__file__).read_text(encoding="utf-8"))
        + footer
    )


#####################################################
# STRATEGIE
#####################################################

NOM_JOUEUR = "Le 4ème Empire"


#####################################################
# Effets des cartes Action
#####################################################

# Les +Cartes sont geres directement par l'arbitre.
# On memorise seulement les informations que l'arbitre
# ne nous renvoie pas : Actions, Achats et pieces bonus.

EFFETS_ACTIONS = {
    "festival": {
        "actions": 2,
        "achats": 1,
        "pieces": 2,
    },
    "smithy": {
        "actions": 0,
        "achats": 0,
        "pieces": 0,
    },
    "laboratory": {
        "actions": 1,
        "achats": 0,
        "pieces": 0,
    },
    "village": {
        "actions": 2,
        "achats": 0,
        "pieces": 0,
    },
    "woodcutter": {
        "actions": 0,
        "achats": 1,
        "pieces": 2,
    },
    "market": {
        "actions": 1,
        "achats": 1,
        "pieces": 1,
    },
}


#####################################################
# Ordre de jeu des cartes Action
#####################################################

PRIORITE_ACTION = [
    "village",
    "laboratory",
    "market",
    "festival",
    "smithy",
    "woodcutter",
]


#####################################################
# Ordre de priorite des achats
#####################################################

PRIORITE_ACHAT = [
    "province",
    "gold",
    "festival",
    "laboratory",
    "market",
    "duchy",
    "smithy",
    "village",
    "woodcutter",
    "silver",
    "estate",
]


#####################################################
# Etat local de chaque partie
#####################################################

# L'arbitre ne renvoie pas le nombre d'Actions ou d'Achats
# restants. On doit donc les memoriser nous-memes par game_id.

etat_tours: dict[str, dict[str, Any]] = {}


def nouvel_etat_tour() -> dict[str, Any]:
    """Etat initial d'un nouveau tour."""
    return {
        "actions_restantes": 1,
        "achats_restants": 1,
        "bonus_pieces": 0,

        # None tant que la phase achat n'a pas commence.
        "argent_restant": None,

        # Une fois True, on ne joue plus de carte Action.
        "phase_achat": False,
    }


#####################################################
# Routes debut de partie / tour
#####################################################


@app.get("/name")
def name() -> str:
    return NOM_JOUEUR


@app.get("/start_game")
def start_game(
    game_id: GameIdDependency,
) -> DopynionResponseStr:

    etat_tours[game_id] = nouvel_etat_tour()

    return DopynionResponseStr(
        game_id=game_id,
        decision="OK",
    )


@app.get("/start_turn")
def start_turn(
    game_id: GameIdDependency,
) -> DopynionResponseStr:

    # Chaque tour commence avec 1 Action et 1 Achat.
    etat_tours[game_id] = nouvel_etat_tour()

    print(
        f">>> Nouveau tour | partie={game_id} | "
        f"Actions=1 | Achats=1",
        flush=True,
    )

    return DopynionResponseStr(
        game_id=game_id,
        decision="OK",
    )


#####################################################
# Fonctions utiles
#####################################################


def trouver_mon_joueur(game: Game):
    """Trouve notre joueur grâce à la main visible."""

    moi = next(
        (p for p in game.players if p.hand is not None),
        None,
    )

    if moi is None:
        moi = next(
            (p for p in game.players if p.name == NOM_JOUEUR),
            None,
        )

    return moi


def calculer_argent_main(game: Game) -> int:
    """
    Calcule l'argent fourni par les cartes Tresor.

    Les bonus de Festival, Market et Woodcutter sont
    ajoutes separement uniquement apres avoir joue la carte.
    """

    moi = trouver_mon_joueur(game)

    if moi is None or moi.hand is None:
        return 0

    argent = 0

    for carte, quantite in moi.hand.quantities.items():
        infos = Card.class_(carte)

        # On ne compte pas automatiquement l'argent
        # des cartes Action.
        if not infos.is_action:
            argent += infos.money * quantite

    return argent


#####################################################
# Gestion des cartes Action
#####################################################


def choisir_action(
    game: Game,
    game_id: str,
) -> CardName | None:
    """Choisit une carte Action selon PRIORITE_ACTION."""

    etat = etat_tours[game_id]

    if etat["phase_achat"]:
        return None

    if etat["actions_restantes"] <= 0:
        return None

    moi = trouver_mon_joueur(game)

    if moi is None or moi.hand is None:
        return None

    main = moi.hand.quantities

    for nom_prioritaire in PRIORITE_ACTION:
        for carte, quantite in main.items():

            if quantite <= 0:
                continue

            if (
                carte.value.lower() == nom_prioritaire
                and Card.class_(carte).is_action
            ):
                return carte

    return None


def appliquer_effet_action(
    game_id: str,
    carte: CardName,
) -> None:
    """Met a jour nos compteurs apres avoir joue une Action."""

    etat = etat_tours[game_id]

    nom = carte.value.lower()

    effet = EFFETS_ACTIONS.get(
        nom,
        {
            "actions": 0,
            "achats": 0,
            "pieces": 0,
        },
    )

    # Jouer une carte Action consomme 1 Action.
    etat["actions_restantes"] -= 1

    # Puis on applique les bonus.
    etat["actions_restantes"] += effet["actions"]
    etat["achats_restants"] += effet["achats"]
    etat["bonus_pieces"] += effet["pieces"]

    print(
        f">>> {carte.value} jouée | "
        f"Actions={etat['actions_restantes']} | "
        f"Achats={etat['achats_restants']} | "
        f"Bonus pièces={etat['bonus_pieces']}",
        flush=True,
    )


#####################################################
# Gestion de la phase Achat
#####################################################


def commencer_phase_achat(
    game: Game,
    game_id: str,
) -> None:
    """Calcule et memorise l'argent disponible pour les achats."""

    etat = etat_tours[game_id]

    if etat["phase_achat"]:
        return

    argent_tresor = calculer_argent_main(game)

    etat["argent_restant"] = (
        argent_tresor
        + etat["bonus_pieces"]
    )

    etat["phase_achat"] = True

    print(
        f">>> Phase achat | "
        f"Trésors={argent_tresor} | "
        f"Bonus={etat['bonus_pieces']} | "
        f"Argent={etat['argent_restant']} | "
        f"Achats={etat['achats_restants']}",
        flush=True,
    )


def choisir_achat(
    game: Game,
    game_id: str,
) -> CardName | None:
    """Choisit la meilleure carte encore achetable."""

    etat = etat_tours[game_id]

    if etat["achats_restants"] <= 0:
        return None

    argent = etat["argent_restant"]

    if argent is None:
        return None

    achetables = [
        carte
        for carte, quantite in game.stock.quantities.items()
        if (
            quantite > 0
            and Card.class_(carte).cost <= argent
        )
    ]

    print(
        f"Argent restant : {argent}",
        flush=True,
    )

    print(
        "Cartes achetables :",
        [carte.value for carte in achetables],
        flush=True,
    )

    for nom_prioritaire in PRIORITE_ACHAT:
        for carte in achetables:

            if carte.value.lower() == nom_prioritaire:
                return carte

    return None


#####################################################
# Affichage de la situation + logs.json
#####################################################


def afficher_situation(
    game: Game,
    game_id: str,
) -> None:

    moi = trouver_mon_joueur(game)

    etat = etat_tours.setdefault(
        game_id,
        nouvel_etat_tour(),
    )

    situation: dict[str, Any] = {
        "partie": game_id,
    }

    print("------------- SITUATION -------------")

    if moi is not None and moi.hand is not None:

        main = moi.hand.quantities
        nb_cartes = sum(main.values())

        argent_tresor = calculer_argent_main(game)

        # Pendant la phase Action, on affiche l'argent
        # potentiel avec les bonus deja obtenus.
        if etat["argent_restant"] is None:
            argent_dispo = (
                argent_tresor
                + etat["bonus_pieces"]
            )
        else:
            argent_dispo = etat["argent_restant"]

        actions = [
            carte.value
            for carte in main
            if Card.class_(carte).is_action
        ]

        achetables = [
            carte.value
            for carte, quantite in game.stock.quantities.items()
            if (
                quantite > 0
                and Card.class_(carte).cost <= argent_dispo
                and etat["achats_restants"] > 0
            )
        ]

        print(f"Joueur        : {moi.name} (score {moi.score})")
        print(f"Cartes en main: {nb_cartes}")

        for carte, quantite in main.items():
            infos = Card.class_(carte)

            print(
                f"   - {quantite} x {carte.value:<15} "
                f"(argent {infos.money}, coût {infos.cost})"
            )

        print(f"Argent trésor : {argent_tresor}")
        print(f"Bonus pièces  : {etat['bonus_pieces']}")
        print(f"Argent dispo  : {argent_dispo}")
        print(f"Actions dispo : {etat['actions_restantes']}")
        print(f"Achats dispo  : {etat['achats_restants']}")
        print(f"Phase achat   : {etat['phase_achat']}")
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
                        "quantite": quantite,
                        "argent": Card.class_(carte).money,
                        "cout": Card.class_(carte).cost,
                    }
                    for carte, quantite in main.items()
                ],

                "argent_tresor": argent_tresor,
                "bonus_pieces": etat["bonus_pieces"],
                "argent_dispo": argent_dispo,
                "argent_restant": etat["argent_restant"],

                "actions_restantes": etat["actions_restantes"],
                "achats_restants": etat["achats_restants"],
                "phase_achat": etat["phase_achat"],

                "cartes_action": actions,
                "achetables": achetables,
            }
        )

    else:
        print("Ma main n'a pas été trouvée dans la trame.")
        situation["main"] = None

    print("Scores        :")

    for joueur in game.players:
        print(
            f"   - {joueur.name:<20} {joueur.score}"
        )

    print("Réserve (stock):")

    for carte, quantite in game.stock.quantities.items():
        print(
            f"   - {carte.value:<15} "
            f"x{quantite:<3} "
            f"(coût {Card.class_(carte).cost})"
        )

    print(f"Partie finie  : {game.finished}")
    print("-------------------------------------", flush=True)

    situation.update(
        {
            "scores": {
                joueur.name: joueur.score
                for joueur in game.players
            },

            "reserve": {
                carte.value: {
                    "quantite": quantite,
                    "cout": Card.class_(carte).cost,
                }
                for carte, quantite in game.stock.quantities.items()
            },

            "partie_finie": game.finished,
        }
    )

    ecrire_situation(situation)


#####################################################
# Route principale
#####################################################


@app.post("/play")
def play(
    game: Game,
    game_id: GameIdDependency,
) -> DopynionResponseStr:

    etat = etat_tours.setdefault(
        game_id,
        nouvel_etat_tour(),
    )

    afficher_situation(
        game,
        game_id,
    )

    # Si la partie est terminee, on ne fait plus rien.
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


    #################################################
    # 1. PHASE ACTION
    #################################################

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

            # Commande annoncee pendant la reunion.
            decision = f"ACTION {carte_action.value}"

            # Si l'arbitre utilise PLAY à la place :
            # decision = f"PLAY {carte_action.value}"

            log_decision(
                game_id,
                "/play",
                decision,
            )

            return DopynionResponseStr(
                game_id=game_id,
                decision=decision,
            )

        # Aucune carte Action a jouer :
        # on passe aux achats.
        commencer_phase_achat(
            game,
            game_id,
        )

    elif not etat["phase_achat"]:

        # Plus aucune Action disponible.
        commencer_phase_achat(
            game,
            game_id,
        )


    #################################################
    # 2. PHASE ACHAT
    #################################################

    if etat["achats_restants"] > 0:

        carte_choisie = choisir_achat(
            game,
            game_id,
        )

        if carte_choisie is not None:

            cout = Card.class_(carte_choisie).cost

            # L'argent doit etre conserve localement car
            # l'arbitre retire les Tresors de la main.
            etat["argent_restant"] -= cout

            # Un BUY consomme un achat.
            etat["achats_restants"] -= 1

            decision = f"BUY {carte_choisie.value}"

            print(
                f">>> Achat {carte_choisie.value} | "
                f"Argent restant={etat['argent_restant']} | "
                f"Achats restants={etat['achats_restants']}",
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


    #################################################
    # 3. FIN DU TOUR
    #################################################

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


#####################################################
# Fin de partie
#####################################################


@app.get("/end_game")
def end_game(
    game_id: GameIdDependency,
) -> DopynionResponseStr:

    # On supprime les informations locales de la partie.
    etat_tours.pop(game_id, None)

    return DopynionResponseStr(
        game_id=game_id,
        decision="OK",
    )


#####################################################
# Routes du template
#####################################################


@app.post("/confirm_discard_card_from_hand")
async def confirm_discard_card_from_hand(
    game_id: GameIdDependency,
    _decision_input: CardNameAndHand,
) -> DopynionResponseBool:

    return DopynionResponseBool(
        game_id=game_id,
        decision=True,
    )


@app.post("/discard_card_from_hand")
async def discard_card_from_hand(
    game_id: GameIdDependency,
    decision_input: Hand,
) -> DopynionResponseCardName:

    return DopynionResponseCardName(
        game_id=game_id,
        decision=decision_input.hand[0],
    )


@app.post("/confirm_trash_card_from_hand")
async def confirm_trash_card_from_hand(
    game_id: GameIdDependency,
    _decision_input: CardNameAndHand,
) -> DopynionResponseBool:

    return DopynionResponseBool(
        game_id=game_id,
        decision=True,
    )


@app.post("/trash_card_from_hand")
async def trash_card_from_hand(
    game_id: GameIdDependency,
    decision_input: Hand,
) -> DopynionResponseCardName:

    return DopynionResponseCardName(
        game_id=game_id,
        decision=decision_input.hand[0],
    )


@app.post("/confirm_discard_deck")
async def confirm_discard_deck(
    game_id: GameIdDependency,
) -> DopynionResponseBool:

    return DopynionResponseBool(
        game_id=game_id,
        decision=True,
    )


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

    return DopynionResponseBool(
        game_id=game_id,
        decision=True,
    )


@app.post("/trash_money_card_for_better_money_card")
async def trash_money_card_for_better_money_card(
    game_id: GameIdDependency,
    decision_input: MoneyCardsInHand,
) -> DopynionResponseCardName:

    return DopynionResponseCardName(
        game_id=game_id,
        decision=decision_input.money_in_hand[0],
    )