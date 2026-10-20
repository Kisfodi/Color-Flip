import numpy as np

from backend.game_mode import GameMode
from .base_puzzle_ruleset import BasePuzzleRuleset
from backend.solvers.gf2 import build_adjacency_matrix_from_pattern, solve_gf2

class PatternRuleSet(BasePuzzleRuleset):
    """
    Ruleset for puzzles defined by fixed relative tile offsets.
    Supports Classic Lights Out, Diagonals, and so on.
    """

    def __init__(
        self,
        name: str,
        pattern: tuple[tuple[int, int], ...] | list[tuple[int, int]],
        supported_modes: tuple[GameMode, ...] = (GameMode.ALL_OFF,),
        min_size: int | None = None,
        max_size: int = 20,
        even_only: bool = False,
    ):
        self.name = name
        self.pattern = tuple(tuple(offset) for offset in pattern)
        self._supported_modes = supported_modes

        # Calculate minimum size required to fit the pattern's bounding span
        if self.pattern:
            drows = [dr for dr, dc in self.pattern]
            dcols = [dc for dr, dc in self.pattern]
            span_r = max(drows) - min(drows) + 1
            span_c = max(dcols) - min(dcols) + 1
            calc_min = max(2, span_r, span_c)
        else:
            calc_min = 2

        effective_min = calc_min if min_size is None else max(min_size, calc_min)
        super().__init__(min_size=effective_min, max_size=max_size, even_only=even_only)

    @property
    def supported_modes(self) -> tuple[GameMode, ...]:
        return self._supported_modes


    def apply_step(self, board: np.ndarray, row: int, col: int) -> np.ndarray:

        for drow, dcol in self.pattern:
            nrow, ncol = row + drow, col + dcol
            if 0<= nrow < board.shape[0] and 0 <= ncol < board.shape[1]:
                board[nrow, ncol] = ~board[nrow, ncol]

        return board

    def generate_board(self, size: int, rng: np.random.Generator) -> np.ndarray:
        total_cells = size * size

        min_flips = max(2, size)
        max_flips = max(min_flips + 1, total_cells // 2)

        while True:
            board = np.zeros((size, size), dtype=bool)
            num_flips = rng.integers(min_flips, max_flips + 1)
            flat_indices = rng.choice(total_cells, size=num_flips, replace=False)

            for idx in flat_indices:
                row, col = divmod(idx, size)
                self.apply_step(board, row, col)

            if not self.is_solved(board):
                return board


    def is_solved(self, board: np.ndarray, mode: GameMode | None = None) -> bool:
        if mode == GameMode.ALL_ON:
            return BasePuzzleRuleset.is_all_on(board)
        return BasePuzzleRuleset.is_all_off(board)

    def solve(self, board: np.ndarray, mode: GameMode | None = None) -> list[tuple[int, int]]:
        size = board.shape[0]

        A = build_adjacency_matrix_from_pattern(size, self.pattern)

        target = ~board if mode == GameMode.ALL_ON else board
        b = target.flatten().astype(bool)

        x = solve_gf2(A, b)
        if x is None:
            return []  # No solution found

        return [divmod(int(idx), size) for idx in np.where(x == 1)[0]]

