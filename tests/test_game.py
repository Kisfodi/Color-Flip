import pytest
from backend.game import Game
from backend.game_mode import GameMode


# ─── helpers ──────────────────────────────────────────────────────────────────

def _one_cell_on() -> list:
    """4×4 board with only (0,0) ON – one step away from all_on."""
    return [
        [True,  False, False, False],
        [False, False, False, False],
        [False, False, False, False],
        [False, False, False, False],
    ]

def _all_on() -> list:
    return [[True] * 4 for _ in range(4)]


# ─── solve_game ────────────────────────────────────────────────────────────────

def test_solve_game_can_be_toggled_off():
    game = Game(size=4, seed=0, mode="all_on", current_board_state=_one_cell_on())

    state = game.solve_game(enabled=False)

    assert state["solve_mode"] is False
    assert state["solution_cells"] == []


def test_solve_game_returns_hint_cells_when_enabled():
    game = Game(size=4, seed=0, mode="all_on", current_board_state=_one_cell_on())

    state = game.solve_game(enabled=True)

    assert state["solve_mode"] is True
    assert isinstance(state["solution_cells"], list)


def test_step_recomputes_solution_cells_when_solve_mode_is_on():
    game = Game(size=4, seed=0, mode="all_on", current_board_state=_one_cell_on())

    game.solve_game(enabled=True)
    state = game.step(0, 1)

    assert state["solve_mode"] is True
    assert state["solution_cells"] != []


# ─── timing ───────────────────────────────────────────────────────────────────

class FakeClock:
    def __init__(self, start=0.0):
        self._now = start

    def __call__(self):
        return self._now

    def advance_to(self, value):
        self._now = value


@pytest.fixture
def fake_clock(monkeypatch):
    clock = FakeClock(start=1000.0)
    monkeypatch.setattr("backend.game.time.time", clock)
    return clock


def test_elapsed_time_freezes_after_game_over(fake_clock):
    game = Game(size=4, seed=0, mode=GameMode.ALL_ON, current_board_state=_all_on())

    fake_clock.advance_to(1005.0)
    first_state = game.get_game_state()

    assert first_state["game_over"] is True
    assert first_state["elapsed_time"] == 5.0

    fake_clock.advance_to(1005.0 + 42.0)
    second_state = game.get_game_state()

    assert second_state["game_over"] is True
    assert second_state["elapsed_time"] == 5.0  # Should remain the same


def test_start_time_is_not_cleared_when_game_ends(fake_clock):
    game = Game(size=4, seed=0, mode="all_on", current_board_state=_all_on())

    fake_clock.advance_to(1003.0)
    game.get_game_state()

    assert game._end_time == 1003.0

    fake_clock.advance_to(1050.0)
    game.get_game_state()
    game.get_game_state()

    assert game._end_time == 1003.0


def test_elapsed_time_still_increases_while_game_in_progress(fake_clock):
    game = Game(size=4, seed=0, mode="all_on")

    fake_clock.advance_to(1007.0)
    state = game.get_game_state()

    assert state["game_over"] is False
    assert state["elapsed_time"] == 7.0
    assert game._end_time is None


# ─── undo ─────────────────────────────────────────────────────────────────────

def test_undo_reverses_last_step():
    game = Game(size=4, seed=0, mode="all_on", current_board_state=_one_cell_on())
    board_before = game.get_game_state()["board"]

    game.step(0, 1)
    board_after_step = game.get_game_state()["board"]
    assert board_after_step != board_before  # sanity check

    state = game.undo()

    assert state["board"] == board_before


def test_undo_decrements_move_count():
    game = Game(size=4, seed=0, mode="all_on", current_board_state=_one_cell_on())

    game.step(0, 1)
    assert game.get_game_state()["moves_made"] == 1

    game.undo()
    assert game.get_game_state()["moves_made"] == 0


def test_undo_removes_move_from_history():
    game = Game(size=4, seed=0, mode="all_on", current_board_state=_one_cell_on())

    game.step(1, 2)
    assert game.moves_history == [[1, 2]]

    game.undo()
    assert game.moves_history == []


def test_undo_on_empty_history_raises():
    game = Game(size=4, seed=0, mode="all_on", current_board_state=_one_cell_on())

    with pytest.raises(ValueError, match="No moves to undo"):
        game.undo()


def test_undo_after_game_solved_reopens_game():
    """Undoing the winning move should clear the completed state."""
    game = Game(size=4, seed=0, mode="all_on", current_board_state=_one_cell_on())

    game.step(0, 0)
    # Manually force solved state so the test is board-layout independent.
    game._end_time = 9999.0

    game.undo()

    assert game._end_time is None
    assert game.get_game_state()["game_over"] is False
