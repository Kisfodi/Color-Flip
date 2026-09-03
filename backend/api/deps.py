from __future__ import annotations
from typing import Optional
import sqlite3
from fastapi import Depends, HTTPException, Header

from backend.game import Game
from backend.db import get_db_dependency
from backend.game_db import load_game_from_db


def get_active_game(
        x_game_id: Optional[str] = Header(None, alias="X-Game-ID"),
        db: sqlite3.Connection = Depends(get_db_dependency),
) -> Game:
    if not x_game_id:
        raise HTTPException(status_code=400, detail="Missing X-Game-ID header")

    game_data = load_game_from_db(db, x_game_id)

    if not game_data:
        raise HTTPException(status_code=404, detail="Game session not found")

    return Game.from_dict(game_data)
