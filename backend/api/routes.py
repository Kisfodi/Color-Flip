import sqlite3
import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Path

from backend.colors import get_all_color_schemes, get_color_scheme, validate_color_scheme
from backend.config import get_default_board_size, get_default_seed, get_default_game_mode
from backend.db import get_db_dependency
from backend.game import Game
from backend.api.deps import get_active_game
from backend.api.schemas import (
    NewGameRequest,
    SolveGameRequest,
    StepRequest,
    ConfigResponse,
    ColorScheme,
    GameStateResponse
)
from backend.game_db import create_game_in_db, save_game_progress

GameID = Annotated[str, Header(alias="X-Game-ID")]
DbConn = Annotated[sqlite3.Connection, Depends(get_db_dependency)]
ActiveGame = Annotated[Game, Depends(get_active_game)]

router = APIRouter()

_scheme_names = tuple(get_all_color_schemes().keys())
SchemeName = Literal[_scheme_names]


@router.get("/config")
def get_config() -> ConfigResponse:
    try:
        from backend.config import get_all_config

        config = get_all_config()
        return ConfigResponse(
            size=config.get("size", 4),
            seed=config.get("seed"),
            color_scheme=config.get("color_scheme", "default"),
            mode=config.get("mode", "mixed")
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/colors", response_model=dict[str, ColorScheme])
def get_colors() -> dict[str, ColorScheme]:
    try:
        return get_all_color_schemes()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/colors/{scheme_name}", response_model=ColorScheme)
def get_color_scheme_endpoint(
    scheme_name: Annotated[
        SchemeName,
        Path(description="Key name of the color scheme to retrieve")
    ]
) -> ColorScheme:
    try:
        if not validate_color_scheme(scheme_name):
            raise HTTPException(status_code=404, detail=f"Color scheme '{scheme_name}' not found")

        return get_color_scheme(scheme_name)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/game_state", response_model=GameStateResponse)
def get_game_state(game: ActiveGame, x_game_id: GameID) -> GameStateResponse:
    state = game.get_game_state()
    state["game_id"] = x_game_id
    return state

@router.post("/new_game", response_model=GameStateResponse)
def new_game(
        db: DbConn,
        payload: Annotated[NewGameRequest, Body()] = NewGameRequest(),
) -> GameStateResponse:
    data = payload.model_dump(exclude_none=True)

    size = data.get("size", get_default_board_size())
    seed = data.get("seed", get_default_seed())
    mode = data.get("mode", get_default_game_mode())
    ruleset = data.get("ruleset", "color_flip")

    try:
        game = Game(size=size, seed=seed, mode=mode, ruleset=ruleset)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    game_id = str(uuid.uuid4())
    game_state = game.get_game_state()

    # Persist the new game so subsequent requests can load it by ID
    create_game_in_db(
        conn=db,
        game_id=game_id,
        user_id=None,   # guests; attach a real user_id once auth is implemented
        game_state=game_state,
        seed=game_state.get("seed"),
    )

    # Return the state with the game_id so the client can store it
    game_state["game_id"] = game_id
    return game_state


@router.post("/step", response_model=GameStateResponse)
def step(
        payload: StepRequest,
        game: ActiveGame,
        x_game_id: GameID,
        db: DbConn,
) -> GameStateResponse:

    new_state = game.step(payload.row, payload.col)

    save_game_progress(
        conn=db,
        game_id=x_game_id,
        current_board=new_state['board'],
        moves_history=game.moves_history,
        moves_count=new_state['moves_made'],
        time_elapsed=new_state['elapsed_time'],
        is_completed=new_state['game_over']
    )

    new_state["game_id"] = x_game_id
    return new_state

@router.post("/undo", response_model=GameStateResponse)
def undo(
        game: ActiveGame,
        x_game_id: GameID,
        db: DbConn,
) -> GameStateResponse:
    try:
        new_state = game.undo()

        save_game_progress(
            conn=db,
            game_id=x_game_id,
            current_board=new_state['board'],
            moves_history=game.moves_history,
            moves_count=new_state['moves_made'],
            time_elapsed=new_state['elapsed_time'],
            is_completed=new_state['game_over']
        )

        new_state["game_id"] = x_game_id
        return new_state
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/solve_game", response_model=GameStateResponse)
def solve_game(
        game: ActiveGame,
        x_game_id: GameID,
        payload: Annotated[SolveGameRequest, Body()] = SolveGameRequest(),
) -> GameStateResponse:
    data = payload.model_dump(exclude_none=True)
    enabled = data.get("enabled")
    state = game.solve_game(enabled=enabled)
    state["game_id"] = x_game_id
    return state
