from .base_puzzle_ruleset import BasePuzzleRuleset
from backend.game_mode import GameMode
import numpy as np

class ColorFlipRuleSet(BasePuzzleRuleset):

    def __init__(self, min_size: int = 2, max_size: int = 20):
        super().__init__(min_size=min_size, max_size=max_size, even_only=True)

    @property
    def supported_modes(self) -> tuple[GameMode, ...]:
        return GameMode.ALL_OFF, GameMode.ALL_ON, GameMode.MIXED

    def apply_step(self, board: np.ndarray, row: int, col: int) -> np.ndarray:

        # Flipping the target cell to make sure it changes states after the row and column of the cell are flipped
        board[row, col] = ~board[row, col]
        board[:, col] = ~board[:, col]
        board[row, :] = ~board[row, :]

        return board

    def generate_board(self, size: int, rng: np.random.Generator) -> np.ndarray:
        while True:
            board = rng.integers(2, size=(size, size), dtype=bool)
            if not (BasePuzzleRuleset.is_all_on(board) or BasePuzzleRuleset.is_all_off(board)):
                return board

    def validate_custom_size(self, size: int) -> None:
        if size % 2 == 1:
            raise ValueError("Board size must be even for Color Flip.")

    def is_solved(self, board: np.ndarray, mode: GameMode | None = None) -> bool:
        if mode == GameMode.ALL_ON:
            return BasePuzzleRuleset.is_all_on(board)
        elif mode == GameMode.ALL_OFF:
            return BasePuzzleRuleset.is_all_off(board)
        else:
            goal_reached = BasePuzzleRuleset.is_all_on(board) or BasePuzzleRuleset.is_all_off(board)

            return goal_reached

    def solve(self, board: np.ndarray, mode: GameMode | None = None) -> list[tuple[int, int]]:
        return ColorFlipRuleSet._get_solution_cells(board, mode)

    # Helper methods
    @staticmethod
    def get_positions_to_press(board: np.ndarray, select_on_positions: bool = True):

        positions_to_press = {}
        positions = BasePuzzleRuleset.get_on_positions(board) if select_on_positions else BasePuzzleRuleset.get_off_positions(board)

        for position in positions:

            row, col = position

            if position not in positions_to_press:
                positions_to_press[position] = 0
            positions_to_press[position] += 1

            for i in range(board.shape[0]):
                if (row, i) not in positions_to_press:
                    positions_to_press[(row, i)] = 0
                positions_to_press[(row, i)] += 1

                if (i, col) not in positions_to_press:
                    positions_to_press[(i, col)] = 0
                positions_to_press[(i, col)] += 1

        return dict(filter(lambda p: p[1] % 2 > 0, positions_to_press.items()))

    @staticmethod
    def _get_solution_cells(board: np.ndarray, mode: GameMode | None = None) -> list[tuple[int, int]]:

        on_positions_to_press = ColorFlipRuleSet.get_positions_to_press(board, select_on_positions=True)
        off_positions_to_press = ColorFlipRuleSet.get_positions_to_press(board, select_on_positions=False)

        if mode == GameMode.ALL_ON:
            return [
                (int(row), int(col)) for row, col in off_positions_to_press
            ]
        elif mode == GameMode.ALL_OFF:
            return [
                (int(row), int(col)) for row, col in on_positions_to_press
            ]

        if len(on_positions_to_press) <= len(off_positions_to_press):
            solution_cells = list(on_positions_to_press.keys())
        else:
            solution_cells = list(off_positions_to_press.keys())

        return [(int(row), int(col)) for row, col in solution_cells]
