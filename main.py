import traceback
from typing import Annotated

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
    CardName,
    CardNameAndHand,
    Game,
    Hand,
    MoneyCardsInHand,
    PossibleCards,
)

from config import obtenir_nom_joueur
from deck import observer_partie
from game_utils import (
    bot_officiel_en_face,
)
from reactions import (
    accepter_defausse_carte,
    accepter_defausse_deck,
    accepter_ecarter_carte,
    carte_a_defausser,
)
from logger_utils import (
    afficher_situation,
    enregistrer_decision,
    enregistrer_erreur,
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


# Identifiant de la partie, envoyé par
# l'arbitre dans l'en-tête x-game-id.
GameId = Annotated[
    str,
    Header(alias="x-game-id"),
]


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
    x_game_id: GameId,
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
    x_game_id: GameId,
) -> str:
    demarrer_tour(
        x_game_id
    )

    return "OK"


@app.post("/play")
def play(
    game: Game,
    x_game_id: GameId,
) -> DopynionResponseStr:
    """
    Filet de sécurité : si la logique
    de décision plante (bug, cas
    imprévu...), on passe le tour au
    lieu de renvoyer une erreur 500 à
    l'arbitre. L'erreur est affichée
    dans la console du serveur et
    gardée dans le log de la partie.
    """

    try:
        decision = decider(
            game,
            x_game_id,
        )

    except Exception:
        decision = "END_TURN"

        try:
            tour = obtenir_etat(
                x_game_id
            ).get("tour")

        except Exception:
            tour = None

        enregistrer_erreur(
            x_game_id,
            tour,
            traceback.format_exc(),
        )

    return DopynionResponseStr(
        game_id=x_game_id,
        decision=decision,
    )


def decider(
    game: Game,
    x_game_id: str,
) -> str:
    with verrou_partie(
        x_game_id
    ):
        etat = obtenir_etat(
            x_game_id
        )

        # Piles initiales, Curses reçues
        # (déduites du score), Provinces
        # restantes... avant toute décision.
        observer_partie(
            game,
            x_game_id,
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

            return decision

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

            return decision

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

            return decision

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
                str(achat),
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

        # -------------------------
        # FIN DU TOUR
        # -------------------------

        decision = "END_TURN"

        enregistrer_decision(
            x_game_id,
            etat["tour"],
            decision,
        )

        return decision


@app.get("/end_game")
def end_game(
    x_game_id: GameId,
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
#
# Avec les 16 cartes du royaume de l'arbitre, seuls deux
# callbacks sont réellement appelés :
# - /discard_card_from_hand (Militia adverse) ;
# - /confirm_discard_deck (notre Chancellor).
# Les autres répondent simplement, au cas où l'arbitre
# ajouterait des cartes (Chapel, Mine, Remodel...).
# =========================================================

def reponse_carte(
    game_id: str,
    carte: CardName | None,
) -> DopynionResponseCardName:
    return DopynionResponseCardName(
        game_id=game_id,
        decision=(
            "NONE"
            if carte is None
            else carte.value
        ),
    )


def premiere_parmi(
    cartes: list[CardName],
    ordre: tuple[str, ...],
) -> CardName | None:
    # Première carte présente, dans
    # l'ordre de préférence donné.
    return next(
        (
            carte
            for nom in ordre
            for carte in cartes
            if carte == nom
        ),
        None,
    )


def meilleure_carte(
    cartes: list[CardName],
) -> CardName | None:
    # La plus chère, puis celle qui
    # rapporte le plus d'argent.
    return max(
        cartes,
        key=lambda carte: (
            Card.class_(carte).cost,
            Card.class_(carte).money,
        ),
        default=None,
    )


# =========================================================
# MILITIA / DÉFAUSSE
# =========================================================

@app.post(
    "/confirm_discard_card_from_hand"
)
def confirm_discard_card_from_hand(
    demande: CardNameAndHand,
    x_game_id: GameId,
) -> DopynionResponseBool:
    # L'arbitre demande carte par carte
    # (card_name) : on ne défausse que
    # les cartes mortes.
    return DopynionResponseBool(
        game_id=x_game_id,
        decision=accepter_defausse_carte(
            demande.card_name
        ),
    )


@app.post(
    "/discard_card_from_hand"
)
def discard_card_from_hand(
    hand: Hand,
    x_game_id: GameId,
) -> DopynionResponseCardName:
    # Garde la meilleure main possible
    # (trésors, cartes de pioche, une
    # seule terminale sans Village...).
    return reponse_carte(
        x_game_id,
        carte_a_defausser(
            hand.hand
        ),
    )


# =========================================================
# TRASH
# =========================================================

@app.post(
    "/confirm_trash_card_from_hand"
)
def confirm_trash_card_from_hand(
    demande: CardNameAndHand,
    x_game_id: GameId,
) -> DopynionResponseBool:
    # L'arbitre demande carte par carte :
    # on décide sur card_name, pas sur
    # le contenu de la main (sinon une
    # Chapel écarterait aussi les Gold).
    return DopynionResponseBool(
        game_id=x_game_id,
        decision=accepter_ecarter_carte(
            demande.card_name,
            obtenir_etat(
                x_game_id
            ),
        ),
    )


@app.post(
    "/trash_card_from_hand"
)
def trash_card_from_hand(
    hand: Hand,
    x_game_id: GameId,
) -> DopynionResponseCardName:
    return reponse_carte(
        x_game_id,
        premiere_parmi(
            hand.hand,
            ("curse", "estate", "copper"),
        ),
    )


# =========================================================
# CHANCELLOR
# =========================================================

@app.post(
    "/confirm_discard_deck"
)
def confirm_discard_deck(
    x_game_id: GameId,
) -> DopynionResponseBool:
    # Oui en début / milieu de partie :
    # le prochain mélange contiendra nos
    # achats récents. Non en fin de partie.
    return DopynionResponseBool(
        game_id=x_game_id,
        decision=accepter_defausse_deck(
            obtenir_etat(
                x_game_id
            )
        ),
    )


# =========================================================
# RÉCEPTION DE CARTES
# =========================================================

@app.post(
    "/choose_card_to_receive_in_discard"
)
def choose_card_to_receive_in_discard(
    possible_cards: PossibleCards,
    x_game_id: GameId,
) -> DopynionResponseCardName:
    return reponse_carte(
        x_game_id,
        meilleure_carte(
            possible_cards.possible_cards
        ),
    )


@app.post(
    "/choose_card_to_receive_in_deck"
)
def choose_card_to_receive_in_deck(
    possible_cards: PossibleCards,
    x_game_id: GameId,
) -> DopynionResponseCardName:
    return reponse_carte(
        x_game_id,
        meilleure_carte(
            possible_cards.possible_cards
        ),
    )


@app.post(
    "/skip_card_reception_in_hand"
)
def skip_card_reception_in_hand(
    x_game_id: GameId,
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
    x_game_id: GameId,
) -> DopynionResponseCardName:
    return reponse_carte(
        x_game_id,
        premiere_parmi(
            money_cards.money_in_hand,
            ("copper", "silver", "gold"),
        ),
    )
