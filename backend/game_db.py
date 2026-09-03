import json
import sqlite3


def serialize_board(board: list) -> str:
    return json.dumps(board)

def deserialize_board(board_str: str) -> list:
    return json.loads(board_str)

def create_game_in_db(
    conn: sqlite3.Connection,
    game_id: str,
    user_id: int | None,
    game_state: dict,
    seed: int | None = None
) -> None:


    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO games (
            id, user_id, board_size, game_mode, seed,
            initial_board, current_board, moves_history, moves_count, time_elapsed, is_completed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
        """,
        (
            game_id,
            user_id,
            game_state["board_size"][0],
            str(game_state["mode"]),
            seed,
            serialize_board(game_state["board"]),
            serialize_board(game_state["board"]),
            "[]",
            0,
            0.0,
            False
        )
    )

    conn.commit()

def save_game_progress(
        conn: sqlite3.Connection,
        game_id: str,
        current_board: list,
        moves_history: list,
        moves_count: int,
        time_elapsed: float,
        is_completed: bool
) -> None:
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE games 
        SET current_board=?,
            moves_history=?,
            moves_count=?,
            time_elapsed=?,
            is_completed=?,
            updated_at=CURRENT_TIMESTAMP
        WHERE id=?
        """,
        (
            serialize_board(current_board),
            json.dumps(moves_history),
            moves_count,
            time_elapsed,
            is_completed,
            game_id
        )
    )

    conn.commit()

def load_game_from_db(
        conn: sqlite3.Connection,
        game_id: str,
) -> dict | None:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT board_size, game_mode, seed, current_board, moves_history, moves_count, time_elapsed, is_completed 
        FROM games 
        WHERE id = ?
        """,
        (game_id,)
    )

    row = cursor.fetchone()
    if not row:
        return None

    return {
        "board_size": row["board_size"],
        "mode": row["game_mode"],
        "seed": row["seed"],
        "board": deserialize_board(row["current_board"]),
        "moves_history": json.loads(row["moves_history"]),
        "moves_made": row["moves_count"],
        "elapsed_time": row["time_elapsed"],
        "game_over": bool(row["is_completed"]),
    }
