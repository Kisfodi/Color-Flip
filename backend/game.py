from __future__ import annotations
import time
import numpy as np

from backend.game_mode import GameMode
from .board import Board
from .rulesets import BasePuzzleRuleset, get_ruleset


class Game:

    def __init__(
            self,
            size: int,
            seed: int | None = None,
            mode: GameMode | str = GameMode.MIXED,
            ruleset: BasePuzzleRuleset | str = 'color_flip',
            current_board_state: list | None = None,
            moves_made: int = 0,
            moves_history: list | None = None,
            elapsed_time_offset: float = 0.0,
    ):
        if seed is None:
            seed = int(np.random.randint(1, 1_000_000))

        self._size = size
        self._seed = seed
        self._ruleset = get_ruleset(ruleset)
        self._ruleset_name = ruleset if isinstance(ruleset, str) else ruleset.__class__.__name__

        mode = GameMode(mode)
        self._ruleset.validate_size(size)
        if mode not in self._ruleset.supported_modes:
            raise ValueError(f"Mode '{mode}' not supported by ruleset '{self._ruleset_name}'. Supported modes: {self._ruleset.supported_modes}")

        self._mode = mode
        self._board = Board(size=size, ruleset=self._ruleset, seed=seed, initial_state=current_board_state)
        self._initial_board = self._board.get_board(serialize=True)
        self._moves_made = moves_made
        self._moves_history = moves_history if moves_history is not None else []
        self._solve_mode = False

        self._start_time = time.time() - elapsed_time_offset
        self._end_time = None

    def get_game_state(self, serialize: bool = True):
        elapsed_time = self._get_elapsed_time()
        return {
            "board": self._board.get_board(serialize=serialize),
            "initial_board": self._initial_board,
            "game_over": self.is_solved(),
            "moves_made": self._moves_made,
            "board_size": (self._size, self._size),
            "elapsed_time": elapsed_time,
            "mode": self._mode,
            "ruleset": self._ruleset_name,
            "solve_mode": self._solve_mode,
            "solution_cells": self._get_solution_cells() if self._solve_mode else [],
            "seed": self._seed
        }

    def _get_elapsed_time(self):
        end_time = self._end_time if self._end_time is not None else time.time()
        return end_time - self._start_time

    def step(self, row: int, col: int):
        self._board.apply_step(row, col)
        self._moves_made += 1
        self._moves_history.append([row, col])

        return self.get_game_state()

    def undo(self):
        if not self._moves_history:
            raise ValueError("No moves to undo")

        last_row, last_col = self._moves_history.pop()
        self._board.apply_step(last_row, last_col)

        self._moves_made = max(0, self._moves_made - 1)
        if self._end_time is not None:
            self._end_time = None  # Reset end time if the game was previously solved

        return self.get_game_state()

    def flip_cell(self, row: int, col: int):
        """Alias for step(row, col) to expose a clear board-action API."""
        return self.step(row, col)

    def is_solved(self):
        """Alias for is_game_over() to clarify game completion semantics."""
        return self.is_game_over()

    def get_state(self, serializable: bool = True):
        """Return the current game state snapshot."""
        return self.get_game_state(serialize=serializable)

    @property
    def board(self):
        """Return the current board state in a reusable format."""
        return self._board.get_board(serialize=True)

    @property
    def moves_history(self) -> list:
        """Return a copy of the move history (list of [row, col] pairs)."""
        return list(self._moves_history)

    def is_game_over(self):
        """Check if game is over based on the current mode via the ruleset."""

        goal_reached = self._ruleset.is_solved(self._board.get_board(), self._mode)
        if goal_reached and self._end_time is None:
            self._end_time = time.time()

        return goal_reached

    def solve_game(self, enabled: bool | None = None):
        """Toggle solver hints on or off for the current board state."""
        if enabled is None:
            enabled = not self._solve_mode

        self._solve_mode = bool(enabled)

        game_state = self.get_game_state()
        if self._solve_mode:
            game_state["solution_cells"] = self._get_solution_cells()
        else:
            game_state["solution_cells"] = []

        return game_state

    def _get_solution_cells(self) -> list[list[int]]:
        """Query solution clicks from the ruleset and format as [[r, c], ...]."""
        solution_tuples = self._ruleset.solve(self._board.get_board(), self._mode)
        return [[int(row), int(col)] for row, col in solution_tuples]

    @classmethod
    def from_dict(cls, data: dict) -> "Game":
        board_size = data["board_size"]
        if isinstance(board_size, (list, tuple)):
            board_size = board_size[0]

        return cls(
            size=board_size,
            seed=data["seed"],
            mode=data["mode"],
            ruleset=data.get("ruleset", "color_flip"),
            current_board_state=data["board"],
            moves_made=data.get("moves_made", 0),
            moves_history=data.get("moves_history", []),
            elapsed_time_offset=data.get("elapsed_time", 0.0),
        )