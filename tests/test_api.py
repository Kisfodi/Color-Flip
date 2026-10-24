import sqlite3
import pytest
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api import router
from backend.db import get_db_dependency


@pytest.fixture
def test_client(tmp_path):
    """FastAPI TestClient backed by an isolated temporary SQLite database."""
    db_file = tmp_path / "test_api.sqlite"
    schema_path = Path(__file__).resolve().parent.parent / "schema.sql"

    # Initialize schema
    conn = sqlite3.connect(db_file)
    conn.executescript(schema_path.read_text(encoding="utf-8"))
    conn.close()

    def override_db():
        c = sqlite3.connect(db_file)
        c.row_factory = sqlite3.Row
        try:
            yield c
        finally:
            c.close()

    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.dependency_overrides[get_db_dependency] = override_db

    with TestClient(app) as client:
        yield client


# ─── Config & Colors Endpoints ───────────────────────────────────────────────

def test_get_config(test_client):
    res = test_client.get("/api/config")
    assert res.status_code == 200
    data = res.json()
    assert "size" in data
    assert "ruleset" in data
    assert "rulesets" in data
    assert "color_flip" in data["rulesets"]
    assert "lights_out" in data["rulesets"]


def test_get_colors(test_client):
    res = test_client.get("/api/colors")
    assert res.status_code == 200
    colors = res.json()
    assert isinstance(colors, dict)
    assert len(colors) > 0


def test_get_color_scheme_valid(test_client):
    res = test_client.get("/api/colors/default")
    assert res.status_code == 200
    data = res.json()
    assert "board" in data
    assert "on_cell" in data["board"]


def test_get_color_scheme_invalid(test_client):
    res = test_client.get("/api/colors/invalid_scheme_xyz")
    assert res.status_code in (404, 422)


# ─── New Game Endpoint ───────────────────────────────────────────────────────

def test_new_game_color_flip_valid(test_client):
    payload = {"size": 4, "seed": 42, "mode": "mixed", "ruleset": "color_flip"}
    res = test_client.post("/api/new_game", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["game_id"] is not None
    assert data["board_size"] == [4, 4]
    assert data["ruleset"] == "color_flip"
    assert data["moves_made"] == 0
    assert data["game_over"] is False


def test_new_game_color_flip_odd_size_rejected(test_client):
    # Color flip requires even sizes; 5 should be rejected by Pydantic validator (422)
    payload = {"size": 5, "ruleset": "color_flip"}
    res = test_client.post("/api/new_game", json=payload)
    assert res.status_code == 422


def test_new_game_lights_out_valid(test_client):
    payload = {"size": 5, "seed": 99, "mode": "all_off", "ruleset": "lights_out"}
    res = test_client.post("/api/new_game", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["board_size"] == [5, 5]
    assert data["ruleset"] == "lights_out"
    assert data["mode"] == "all_off"


def test_new_game_lights_out_invalid_mode_rejected(test_client):
    # Lights Out only supports 'all_off'
    payload = {"size": 5, "mode": "mixed", "ruleset": "lights_out"}
    res = test_client.post("/api/new_game", json=payload)
    assert res.status_code == 400


def test_new_game_invalid_ruleset(test_client):
    res = test_client.post("/api/new_game", json={"ruleset": "nonexistent_ruleset"})
    assert res.status_code == 400


# ─── Game State Endpoint ─────────────────────────────────────────────────────

def test_get_game_state_success(test_client):
    create_res = test_client.post("/api/new_game", json={"size": 4, "seed": 10})
    game_id = create_res.json()["game_id"]

    res = test_client.get("/api/game_state", headers={"X-Game-ID": game_id})
    assert res.status_code == 200
    data = res.json()
    assert data["game_id"] == game_id
    assert data["board_size"] == [4, 4]


def test_get_game_state_missing_header(test_client):
    res = test_client.get("/api/game_state")
    assert res.status_code in (400, 422)


def test_get_game_state_not_found(test_client):
    res = test_client.get("/api/game_state", headers={"X-Game-ID": "non-existent-uuid"})
    assert res.status_code == 404


# ─── Step & Undo Endpoints ───────────────────────────────────────────────────

def test_step_and_undo_endpoints(test_client):
    # 1. Create a game
    create_res = test_client.post("/api/new_game", json={"size": 4, "seed": 10, "ruleset": "color_flip"})
    game_id = create_res.json()["game_id"]

    headers = {"X-Game-ID": game_id}

    # 2. Step
    step_res = test_client.post("/api/step", json={"row": 1, "col": 1}, headers=headers)
    assert step_res.status_code == 200
    step_data = step_res.json()
    assert step_data["moves_made"] == 1

    # 3. Undo
    undo_res = test_client.post("/api/undo", headers=headers)
    assert undo_res.status_code == 200
    undo_data = undo_res.json()
    assert undo_data["moves_made"] == 0


def test_step_missing_header(test_client):
    res = test_client.post("/api/step", json={"row": 0, "col": 0})
    assert res.status_code in (400, 422)


def test_step_nonexistent_game(test_client):
    headers = {"X-Game-ID": "fake-nonexistent-id"}
    res = test_client.post("/api/step", json={"row": 0, "col": 0}, headers=headers)
    assert res.status_code == 404


def test_undo_no_moves(test_client):
    create_res = test_client.post("/api/new_game", json={"size": 4, "seed": 10})
    game_id = create_res.json()["game_id"]

    res = test_client.post("/api/undo", headers={"X-Game-ID": game_id})
    assert res.status_code == 400


def test_undo_missing_header(test_client):
    res = test_client.post("/api/undo")
    assert res.status_code in (400, 422)


# ─── Solve Game Endpoint ─────────────────────────────────────────────────────

def test_solve_game_endpoint(test_client):
    create_res = test_client.post("/api/new_game", json={"size": 4, "seed": 7, "mode": "all_on", "ruleset": "color_flip"})
    game_id = create_res.json()["game_id"]

    headers = {"X-Game-ID": game_id}

    # Enable solver
    solve_res = test_client.post("/api/solve_game", json={"enabled": True}, headers=headers)
    assert solve_res.status_code == 200
    data = solve_res.json()
    assert data["solve_mode"] is True
    assert isinstance(data["solution_cells"], list)
    assert len(data["solution_cells"]) > 0


def test_solve_game_disable(test_client):
    create_res = test_client.post("/api/new_game", json={"size": 4, "seed": 7, "mode": "all_on", "ruleset": "color_flip"})
    game_id = create_res.json()["game_id"]

    headers = {"X-Game-ID": game_id}

    # Enable then disable solver
    test_client.post("/api/solve_game", json={"enabled": True}, headers=headers)
    solve_res = test_client.post("/api/solve_game", json={"enabled": False}, headers=headers)
    assert solve_res.status_code == 200
    data = solve_res.json()
    assert data["solve_mode"] is False
    assert data["solution_cells"] == []
