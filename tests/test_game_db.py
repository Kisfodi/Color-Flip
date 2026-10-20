import sqlite3
import pytest
from pathlib import Path

from backend.game_db import (
    serialize_board,
    deserialize_board,
    create_game_in_db,
    save_game_progress,
    load_game_from_db,
)


@pytest.fixture
def db_conn():
    """In-memory SQLite database initialized with schema.sql."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    schema_path = Path(__file__).resolve().parent.parent / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    yield conn
    conn.close()


def test_serialize_deserialize_board():
    board = [[True, False], [False, True]]
    serialized = serialize_board(board)
    assert isinstance(serialized, str)
    deserialized = deserialize_board(serialized)
    assert deserialized == board


def test_create_and_load_game_color_flip(db_conn):
    game_id = "test-uuid-color-flip"
    game_state = {
        "board_size": (4, 4),
        "mode": "mixed",
        "ruleset": "color_flip",
        "board": [[False] * 4 for _ in range(4)],
    }

    create_game_in_db(db_conn, game_id, user_id=None, game_state=game_state, seed=42)

    loaded = load_game_from_db(db_conn, game_id)
    assert loaded is not None
    assert loaded["board_size"] == 4
    assert loaded["mode"] == "mixed"
    assert loaded["ruleset"] == "color_flip"
    assert loaded["seed"] == 42
    assert loaded["moves_made"] == 0
    assert loaded["game_over"] is False
    assert loaded["moves_history"] == []


def test_create_and_load_game_lights_out(db_conn):
    game_id = "test-uuid-lights-out"
    game_state = {
        "board_size": (5, 5),
        "mode": "all_off",
        "ruleset": "lights_out",
        "board": [[True] * 5 for _ in range(5)],
    }

    create_game_in_db(db_conn, game_id, user_id=None, game_state=game_state, seed=99)

    loaded = load_game_from_db(db_conn, game_id)
    assert loaded is not None
    assert loaded["board_size"] == 5
    assert loaded["ruleset"] == "lights_out"
    assert loaded["mode"] == "all_off"


def test_save_game_progress(db_conn):
    game_id = "test-uuid-progress"
    game_state = {
        "board_size": (4, 4),
        "mode": "mixed",
        "ruleset": "color_flip",
        "board": [[False] * 4 for _ in range(4)],
    }
    create_game_in_db(db_conn, game_id, user_id=None, game_state=game_state, seed=1)

    updated_board = [[True] * 4 for _ in range(4)]
    moves_history = [[0, 0], [1, 1]]
    save_game_progress(
        conn=db_conn,
        game_id=game_id,
        current_board=updated_board,
        moves_history=moves_history,
        moves_count=2,
        time_elapsed=15.5,
        is_completed=True,
    )

    loaded = load_game_from_db(db_conn, game_id)
    assert loaded["board"] == updated_board
    assert loaded["moves_history"] == moves_history
    assert loaded["moves_made"] == 2
    assert loaded["elapsed_time"] == 15.5
    assert loaded["game_over"] is True


def test_load_nonexistent_game(db_conn):
    assert load_game_from_db(db_conn, "nonexistent-id") is None


def test_default_ruleset_on_insert(db_conn):
    """When ruleset is omitted during insert, schema default 'color_flip' applies."""
    cursor = db_conn.cursor()
    cursor.execute(
        """
        INSERT INTO games (
            id, user_id, board_size, game_mode, seed,
            initial_board, current_board, moves_history, moves_count, time_elapsed, is_completed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "legacy-game-id",
            None,
            4,
            "mixed",
            123,
            "[[false, false], [false, false]]",
            "[[false, false], [false, false]]",
            "[]",
            0,
            0.0,
            False,
        ),
    )
    db_conn.commit()

    loaded = load_game_from_db(db_conn, "legacy-game-id")
    assert loaded is not None
    assert loaded["ruleset"] == "color_flip"

