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
            json.dumps(
                situation,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


@app.middleware("http")
async def log_requests(request: Request, call_next):
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

    game_id = request.headers.get("x-game-id")

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
        f"\n>>> {request.method} {request.url.path} "
        f"| partie={game_id}\n{affichage}",
        flush=True,
    )

    return await call_next(request)


def log_decision(
    game_id: str,
    route: str,
    decision: Any,
) -> None:
    """Affiche la decision envoyee a l'arbitre."""
    print(
        f">>> Décision ({route}) "
        f"partie={game_id} : {decision}",
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
    x_game_id: str = Header(
        description="ID of the game"
    ),
) -> str:
    return x_game_id


GameIdDependency = Annotated[
    str,
    Depends(get_game_id),
]


#####################################################
# Error management
#####################################################


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


#####################################################
# Template extra bonus
#####################################################


@app.get(
    "/",
    response_class=HTMLResponse,
)
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
        + html.escape(
            Path(__file__).read_text(
                encoding="utf-8"
            )
        )
        + footer
    )


#####################################################
# STRATEGIE
#####################################################

NOM_JOUEUR = "Le 4ème Empire"


#####################################################
# Effets des cartes Action
#####################################################

# L'arbitre gere lui-meme les cartes piochees.
# Nous memorisons uniquement :
# - Actions
# - Achats
# - pieces bonus

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
# Limites des cartes Action
#####################################################

# Evite de remplir le deck de cartes Action.
#
# Le Royaume gagnait avec relativement peu de cartes
# moteur et beaucoup de Tresors / Provinces.

MAX_CARTES_ACTION = {
    "laboratory": 3,
    "smithy": 2,
    "festival": 1,
    "market": 1,
    "village": 1,
    "woodcutter": 0,
}

# Meme si les limites individuelles permettraient
# davantage, on ne veut pas depasser ce total.
MAX_TOTAL_ACTIONS = 5


#####################################################
# Ordre de jeu des cartes Action
#####################################################

PRIORITE_ACTION = [
    "laboratory",
    "village",
    "market",
    "festival",
    "smithy",
    "woodcutter",
]


#####################################################
# Priorites d'achat selon le moment de la partie
#####################################################

# Debut : construire un PETIT moteur.
PRIORITE_ACHAT_DEBUT = [
    "province",
    "gold",
    "laboratory",
    "smithy",
    "festival",
    "market",
    "silver",
    "village",
]

# Milieu : economie avant nouvelles cartes Action.
PRIORITE_ACHAT_MILIEU = [
    "province",
    "gold",
    "laboratory",
    "silver",
    "smithy",
    "festival",
    "market",
    "village",
]

# Fin : convertir l'argent en points.
PRIORITE_ACHAT_FIN = [
    "province",
    "duchy",
    "gold",
    "silver",
    "estate",
]

# Toute fin : les petits points deviennent importants.
PRIORITE_ACHAT_FIN_URGENTE = [
    "province",
    "duchy",
    "estate",
    "gold",
    "silver",
]


#####################################################
# Etat local de chaque partie
#####################################################

# L'arbitre ne nous renvoie pas :
# - Actions restantes
# - Achats restants
# - bonus de pieces
# - argent restant apres plusieurs achats
#
# Ces informations sont donc stockees par game_id.

etat_tours: dict[str, dict[str, Any]] = {}


def nouvel_etat_partie() -> dict[str, Any]:
    """Etat au debut d'une nouvelle partie."""
    return {
        "tour": 0,

        "actions_restantes": 1,
        "achats_restants": 1,

        "bonus_pieces": 0,
        "argent_restant": None,

        "phase_achat": False,

        # Permet de savoir combien de cartes de chaque
        # type notre bot a achetees pendant cette partie.
        "cartes_achetees": {},
    }


def reinitialiser_tour(
    etat: dict[str, Any],
) -> None:
    """Reinitialise uniquement les informations du tour."""

    etat["actions_restantes"] = 1
    etat["achats_restants"] = 1
    etat["bonus_pieces"] = 0
    etat["argent_restant"] = None
    etat["phase_achat"] = False


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

    etat_tours[game_id] = nouvel_etat_partie()

    return DopynionResponseStr(
        game_id=game_id,
        decision="OK",
    )


@app.get("/start_turn")
def start_turn(
    game_id: GameIdDependency,
) -> DopynionResponseStr:

    etat = etat_tours.setdefault(
        game_id,
        nouvel_etat_partie(),
    )

    etat["tour"] += 1

    reinitialiser_tour(etat)

    print(
        f">>> Nouveau tour {etat['tour']} "
        f"| partie={game_id} "
        f"| Actions=1 "
        f"| Achats=1",
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
    """Trouve notre joueur grace a la main visible."""

    moi = next(
        (
            p
            for p in game.players
            if p.hand is not None
        ),
        None,
    )

    if moi is None:
        moi = next(
            (
                p
                for p in game.players
                if p.name == NOM_JOUEUR
            ),
            None,
        )

    return moi


def calculer_argent_main(
    game: Game,
) -> int:
    """Calcule l'argent provenant des cartes Tresor."""

    moi = trouver_mon_joueur(game)

    if moi is None or moi.hand is None:
        return 0

    argent = 0

    for carte, quantite in moi.hand.quantities.items():

        infos = Card.class_(carte)

        # Les cartes Action ne donnent leurs pieces
        # que lorsqu'elles sont reellement jouees.
        if not infos.is_action:
            argent += (
                infos.money
                * quantite
            )

    return argent


def nombre_carte_achetee(
    game_id: str,
    nom: str,
) -> int:
    """Nombre d'exemplaires achetes de cette carte."""

    etat = etat_tours[game_id]

    return etat["cartes_achetees"].get(
        nom,
        0,
    )


def nombre_total_actions_achetees(
    game_id: str,
) -> int:
    """Nombre total de cartes Action achetees."""

    etat = etat_tours[game_id]

    total = 0

    for nom in EFFETS_ACTIONS:
        total += etat["cartes_achetees"].get(
            nom,
            0,
        )

    return total


def enregistrer_achat(
    game_id: str,
    carte: CardName,
) -> None:
    """Memorise localement une carte achetee."""

    etat = etat_tours[game_id]

    nom = carte.value.lower()

    etat["cartes_achetees"][nom] = (
        etat["cartes_achetees"].get(
            nom,
            0,
        )
        + 1
    )


def carte_action_autorisee(
    game_id: str,
    nom: str,
) -> bool:
    """
    Verifie si nous pouvons encore acheter
    cette carte Action.
    """

    if nom not in EFFETS_ACTIONS:
        return True

    limite = MAX_CARTES_ACTION.get(
        nom,
        0,
    )

    if limite <= 0:
        return False

    if nombre_total_actions_achetees(
        game_id
    ) >= MAX_TOTAL_ACTIONS:
        return False

    return (
        nombre_carte_achetee(
            game_id,
            nom,
        )
        < limite
    )


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
                carte.value.lower()
                == nom_prioritaire
                and Card.class_(carte).is_action
            ):
                return carte

    return None


def appliquer_effet_action(
    game_id: str,
    carte: CardName,
) -> None:
    """Met a jour les compteurs apres une Action."""

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

    # Jouer une Action consomme une Action.
    etat["actions_restantes"] -= 1

    # Puis on ajoute ses bonus.
    etat["actions_restantes"] += (
        effet["actions"]
    )

    etat["achats_restants"] += (
        effet["achats"]
    )

    etat["bonus_pieces"] += (
        effet["pieces"]
    )

    print(
        f">>> {carte.value} jouée | "
        f"Actions={etat['actions_restantes']} | "
        f"Achats={etat['achats_restants']} | "
        f"Bonus={etat['bonus_pieces']}",
        flush=True,
    )


#####################################################
# Gestion de la phase achat
#####################################################


def commencer_phase_achat(
    game: Game,
    game_id: str,
) -> None:
    """Memorise le budget total disponible."""

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
        f"Tour={etat['tour']} | "
        f"Trésors={argent_tresor} | "
        f"Bonus={etat['bonus_pieces']} | "
        f"Argent={etat['argent_restant']} | "
        f"Achats={etat['achats_restants']}",
        flush=True,
    )


def provinces_restantes(
    game: Game,
) -> int:
    """Retourne le nombre de Provinces restantes."""

    for carte, quantite in game.stock.quantities.items():

        if carte.value.lower() == "province":
            return quantite

    return 0


def obtenir_priorite_achat(
    game: Game,
    game_id: str,
) -> list[str]:
    """
    Change la strategie selon :
    - le numero du tour
    - le nombre de Provinces restantes
    """

    etat = etat_tours[game_id]

    tour = etat["tour"]

    provinces = provinces_restantes(game)

    # Fin tres proche.
    if provinces <= 2 or tour >= 20:

        print(
            ">>> Strategie achat : FIN URGENTE",
            flush=True,
        )

        return PRIORITE_ACHAT_FIN_URGENTE

    # Fin de partie.
    if provinces <= 4 or tour >= 15:

        print(
            ">>> Strategie achat : FIN",
            flush=True,
        )

        return PRIORITE_ACHAT_FIN

    # Debut.
    if tour <= 6:

        print(
            ">>> Strategie achat : DEBUT",
            flush=True,
        )

        return PRIORITE_ACHAT_DEBUT

    # Milieu.
    print(
        ">>> Strategie achat : MILIEU",
        flush=True,
    )

    return PRIORITE_ACHAT_MILIEU


def choisir_achat(
    game: Game,
    game_id: str,
) -> CardName | None:
    """Choisit la meilleure carte actuellement achetable."""

    etat = etat_tours[game_id]

    if etat["achats_restants"] <= 0:
        return None

    argent = etat["argent_restant"]

    if argent is None:
        return None

    priorite = obtenir_priorite_achat(
        game,
        game_id,
    )

    achetables = [
        carte
        for carte, quantite
        in game.stock.quantities.items()
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
        [
            carte.value
            for carte in achetables
        ],
        flush=True,
    )

    for nom_prioritaire in priorite:

        for carte in achetables:

            nom = carte.value.lower()

            if nom != nom_prioritaire:
                continue

            # Si c'est une carte Action,
            # on verifie les limites.
            if Card.class_(carte).is_action:

                if not carte_action_autorisee(
                    game_id,
                    nom,
                ):
                    continue

            return carte

    # Rien d'interessant :
    # on prefere terminer le tour plutot que
    # d'acheter un Copper inutile.
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
        nouvel_etat_partie(),
    )

    situation: dict[str, Any] = {
        "partie": game_id,
        "tour": etat["tour"],
    }

    print("------------- SITUATION -------------")

    if moi is not None and moi.hand is not None:

        main = moi.hand.quantities

        nb_cartes = sum(
            main.values()
        )

        argent_tresor = calculer_argent_main(
            game
        )

        if etat["argent_restant"] is None:

            argent_dispo = (
                argent_tresor
                + etat["bonus_pieces"]
            )

        else:

            argent_dispo = (
                etat["argent_restant"]
            )

        actions = [
            carte.value
            for carte in main
            if Card.class_(carte).is_action
        ]

        achetables = [
            carte.value
            for carte, quantite
            in game.stock.quantities.items()
            if (
                quantite > 0
                and Card.class_(carte).cost
                <= argent_dispo
                and etat["achats_restants"] > 0
            )
        ]

        print(
            f"Tour          : {etat['tour']}"
        )

        print(
            f"Joueur        : {moi.name} "
            f"(score {moi.score})"
        )

        print(
            f"Cartes en main: {nb_cartes}"
        )

        for carte, quantite in main.items():

            infos = Card.class_(carte)

            print(
                f"   - {quantite} x "
                f"{carte.value:<15} "
                f"(argent {infos.money}, "
                f"coût {infos.cost})"
            )

        print(
            f"Argent trésor : {argent_tresor}"
        )

        print(
            f"Bonus pièces  : "
            f"{etat['bonus_pieces']}"
        )

        print(
            f"Argent dispo  : {argent_dispo}"
        )

        print(
            f"Actions dispo : "
            f"{etat['actions_restantes']}"
        )

        print(
            f"Achats dispo  : "
            f"{etat['achats_restants']}"
        )

        print(
            f"Phase achat   : "
            f"{etat['phase_achat']}"
        )

        print(
            f"Cartes action : "
            f"{actions or 'aucune'}"
        )

        print(
            f"Je peux acheter : "
            f"{achetables or 'rien'}"
        )

        print(
            "Cartes achetées : "
            f"{etat['cartes_achetees']}"
        )

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
                    for carte, quantite
                    in main.items()
                ],

                "argent_tresor": argent_tresor,
                "bonus_pieces": etat["bonus_pieces"],
                "argent_dispo": argent_dispo,
                "argent_restant": etat["argent_restant"],

                "actions_restantes":
                    etat["actions_restantes"],

                "achats_restants":
                    etat["achats_restants"],

                "phase_achat":
                    etat["phase_achat"],

                "cartes_action":
                    actions,

                "cartes_achetees":
                    etat["cartes_achetees"],

                "achetables":
                    achetables,

                "provinces_restantes":
                    provinces_restantes(game),
            }
        )

    else:

        print(
            "Ma main n'a pas été trouvée dans la trame."
        )

        situation["main"] = None

    print("Scores        :")

    for joueur in game.players:

        print(
            f"   - {joueur.name:<20} "
            f"{joueur.score}"
        )

    print("Réserve (stock):")

    for carte, quantite in game.stock.quantities.items():

        print(
            f"   - {carte.value:<15} "
            f"x{quantite:<3} "
            f"(coût {Card.class_(carte).cost})"
        )

    print(
        f"Partie finie  : {game.finished}"
    )

    print(
        "-------------------------------------",
        flush=True,
    )

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
                for carte, quantite
                in game.stock.quantities.items()
            },

            "partie_finie":
                game.finished,
        }
    )

    ecrire_situation(
        situation
    )


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
        nouvel_etat_partie(),
    )

    afficher_situation(
        game,
        game_id,
    )

    # Partie terminee.
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

            # Commande annoncee par l'arbitre.
            decision = (
                f"ACTION {carte_action.value}"
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

        # Plus de carte Action interessante.
        commencer_phase_achat(
            game,
            game_id,
        )

    elif not etat["phase_achat"]:

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

            cout = Card.class_(
                carte_choisie
            ).cost

            # L'arbitre retire les Tresors de la main
            # apres le premier achat, donc nous conservons
            # localement l'argent restant.
            etat["argent_restant"] -= cout

            etat["achats_restants"] -= 1

            enregistrer_achat(
                game_id,
                carte_choisie,
            )

            decision = (
                f"BUY {carte_choisie.value}"
            )

            print(
                f">>> Achat "
                f"{carte_choisie.value} | "
                f"Argent restant="
                f"{etat['argent_restant']} | "
                f"Achats restants="
                f"{etat['achats_restants']}",
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

    etat_tours.pop(
        game_id,
        None,
    )

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