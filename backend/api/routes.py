from typing import Annotated, Literal

from fastapi import APIRouter, Body, HTTPException, Request, Path

from backend.colors import get_all_color_schemes, get_color_scheme, validate_color_scheme
from backend.config import get_default_board_size, get_default_seed, get_default_game_mode
from backend.game import Game
from backend.api.deps import get_active_game, set_active_game
from backend.api.schemas import (
    NewGameRequest,
    SolveGameRequest,
    StepRequest,
    ConfigResponse,
    ColorScheme,
    GameStateResponse
)

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
def get_game_state(request: Request) -> GameStateResponse:
    game = get_active_game(request)
    if game is None:
        raise HTTPException(status_code=400, detail="No active game. Start a new game first.")

    return game.get_game_state()

@router.post("/new_game", response_model=GameStateResponse)
def new_game(
        request: Request,
        payload: Annotated[NewGameRequest, Body()] = NewGameRequest(),
) -> GameStateResponse:
    data = payload.model_dump(exclude_none=True)

    size = data.get("size", get_default_board_size())
    seed = data.get("seed", get_default_seed())
    mode = data.get("mode", get_default_game_mode())

    try:
        set_active_game(request, Game(size=size, seed=seed, mode=mode))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    game = get_active_game(request)
    return game.get_game_state()


@router.post("/step", response_model=GameStateResponse)
def step(
        request: Request,
        payload: StepRequest
) -> GameStateResponse:
    game = get_active_game(request)
    if game is None:
        raise HTTPException(status_code=400, detail="No active game. Start a new game first.")

    return game.step(payload.row, payload.col)


@router.post("/solve_game", response_model=GameStateResponse)
def solve_game(
        request: Request,
        payload: Annotated[SolveGameRequest, Body()] = SolveGameRequest(),
) -> GameStateResponse:
    game = get_active_game(request)
    if game is None:
        raise HTTPException(status_code=400, detail="No active game. Start a new game first.")

    data = payload.model_dump(exclude_none=True)
    enabled = data.get("enabled")
    return game.solve_game(enabled=enabled)
