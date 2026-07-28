from typing import Optional

from fastapi import APIRouter, HTTPException, Request

from backend.colors import get_all_color_schemes, get_color_scheme, validate_color_scheme
from backend.config import get_default_board_size, get_default_seed, get_default_game_mode
from backend.game import Game
from backend.api.schemas import NewGameRequest, SolveGameRequest, StepRequest
from backend.api.deps import get_active_game, set_active_game

router = APIRouter()


@router.get("/config")
def get_config():
    try:
        from backend.config import get_all_config

        config = get_all_config()
        return {
            "size": config.get("size", 4),
            "seed": config.get("seed"),
            "color_scheme": config.get("color_scheme", "default"),
            "mode": config.get("mode", "mixed"),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/colors")
def get_colors():
    try:
        return get_all_color_schemes()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/colors/{scheme_name}")
def get_color_scheme_endpoint(scheme_name: str):
    try:
        if not validate_color_scheme(scheme_name):
            raise HTTPException(status_code=404, detail=f"Color scheme '{scheme_name}' not found")

        return get_color_scheme(scheme_name)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/new_game")
def new_game(request: Request, payload: Optional[NewGameRequest] = None):
    data = payload.model_dump(exclude_none=True) if payload else {}

    size = data.get("size", get_default_board_size())
    seed = data.get("seed", get_default_seed())
    mode = data.get("mode", get_default_game_mode())

    try:
        set_active_game(request, Game(size=size, seed=seed, mode=mode))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    game = get_active_game(request)
    return game.get_game_state()


@router.post("/step")
def step(request: Request, payload: StepRequest):
    game = get_active_game(request)
    if game is None:
        raise HTTPException(status_code=400, detail="No active game. Start a new game first.")

    return game.step(payload.row, payload.col)


@router.get("/game_state")
def get_game_state(request: Request):
    game = get_active_game(request)
    if game is None:
        raise HTTPException(status_code=400, detail="No active game. Start a new game first.")

    return game.get_game_state()


@router.post("/solve_game")
def solve_game(request: Request, payload: Optional[SolveGameRequest] = None):
    game = get_active_game(request)
    if game is None:
        raise HTTPException(status_code=400, detail="No active game. Start a new game first.")

    data = payload.model_dump(exclude_none=True) if payload else {}
    enabled = data.get("enabled")
    return game.solve_game(enabled=enabled)
