import numpy as np

from backend.game import Game


def test_solve_game_can_be_toggled_off():
    game = Game(size=4, seed=0, mode="all_on")
    game._board._board = np.array(
        [
            [True, False, False, False],
            [False, False, False, False],
            [False, False, False, False],
            [False, False, False, False],
        ],
        dtype=bool,
    )

    state = game.solve_game(enabled=False)

    assert state["solve_mode"] is False
    assert state["solution_cells"] == []


def test_solve_game_returns_hint_cells_when_enabled():
    game = Game(size=4, seed=0, mode="all_on")
    game._board._board = np.array(
        [
            [True, False, False, False],
            [False, False, False, False],
            [False, False, False, False],
            [False, False, False, False],
        ],
        dtype=bool,
    )

    state = game.solve_game(enabled=True)

    assert state["solve_mode"] is True
    assert isinstance(state["solution_cells"], list)


def test_step_recomputes_solution_cells_when_solve_mode_is_on():
    game = Game(size=4, seed=0, mode="all_on")
    game._board._board = np.array(
        [
            [True, False, False, False],
            [False, False, False, False],
            [False, False, False, False],
            [False, False, False, False],
        ],
        dtype=bool,
    )

    game.solve_game(enabled=True)
    state = game.step(0, 1)

    assert state["solve_mode"] is True
    assert state["solution_cells"] != []
