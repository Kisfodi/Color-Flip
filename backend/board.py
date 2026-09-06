from __future__ import annotations
import numpy as np

from .rulesets import BasePuzzleRuleset


class Board:
    def __init__(
            self,
            size: int,
            ruleset: BasePuzzleRuleset,
            seed: int | None = None,
            initial_state: list | None = None,
    ):
        ruleset.validate_size(size)
        self._size = size
        self._seed = seed
        self.ruleset = ruleset

        if initial_state is not None:
            self._board = np.array(initial_state, dtype=bool)
        else:
            rng = np.random.default_rng(seed)
            self._board = self.ruleset.generate_board(size, rng)

    def apply_step(self, row: int, col: int) -> np.ndarray:
        """Apply the ruleset's tile-toggle logic to the board."""
        return self.ruleset.apply_step(self._board, row, col)

    def do_step(self, row: int, col: int) -> np.ndarray:
        """Alias for apply_step for backwards compatibility."""
        return self.apply_step(row, col)

    def get_board(self, serialize: bool = False) -> np.ndarray | list:
        return self._board.tolist() if serialize else self._board

    def get_position_state(self, row: int, col: int) -> bool:
        return bool(self._board[row, col])

    def is_all_on(self) -> bool:
        return self.ruleset.is_all_on(self._board)

    def is_all_off(self) -> bool:
        return self.ruleset.is_all_off(self._board)

    def get_on_positions(self) -> list[tuple[int, int]]:
        return self.ruleset.get_on_positions(self._board)

    def get_off_positions(self) -> list[tuple[int, int]]:
        return self.ruleset.get_off_positions(self._board)