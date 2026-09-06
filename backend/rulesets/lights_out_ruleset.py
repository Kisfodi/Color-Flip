import numpy as np

from .base_puzzle_ruleset import BasePuzzleRuleset
from backend.game_mode import GameMode
from backend.solvers import get_adjacency_matrix, solve_gf2

class LightsOutRuleset(BasePuzzleRuleset):

    @property
    def supported_modes(self) -> tuple[GameMode, ...]:
        return (GameMode.ALL_OFF,)

    def apply_step(self, board: np.ndarray, row: int, col: int) -> np.ndarray:

        # Flipping the target cell to make sure it changes states after neighbors are flipped
        board[row, col] = ~board[row, col]
        board[row, max(0, col-1):col+2] = ~board[row, max(0, col-1):col+2]
        board[max(0, row-1):row+2, col] = ~board[max(0, row-1):row+2, col]

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
        return BasePuzzleRuleset.is_all_off(board)


    def solve(self, board: np.ndarray, mode: GameMode | None = None) -> list[tuple[int, int]]:

        size = board.shape[0]
        A = get_adjacency_matrix(size)
        b = board.flatten().astype(bool)

        x = solve_gf2(A, b)
        if x is None:
            return []  # No solution found

        # Indices with 1 is a cell that must be pressed.
        solution = [divmod(int(idx), size) for idx in np.where(x == 1)[0]]
        return solution