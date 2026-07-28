from __future__ import annotations

from typing import Optional

from fastapi import Request

from backend.game import Game


def get_active_game(request: Request) -> Optional[Game]:
    return getattr(request.app.state, "game", None)


def set_active_game(request: Request, game: Game) -> None:
    request.app.state.game = game
