from abc import abstractmethod
from abc import ABC

import numpy as np

from backend.game_mode import GameMode

class BasePuzzleRuleset(ABC):

    def __init__(
            self,
            min_size: int = 2,
            max_size: int = 20,
            even_only: bool = False,
    ):

        self.min_size = min_size
        self.max_size = max_size
        self.even_only = even_only

    @property
    @abstractmethod
    def supported_modes(self) -> tuple[GameMode, ...]:
        """Modes supported by this puzzle variant"""

        raise NotImplementedError

    @property
    def default_mode(self) -> GameMode:
        return self.supported_modes[0]


    @abstractmethod
    def apply_step(self, board: np.ndarray, row: int, col: int) -> np.ndarray:
        """Toggle cells according to the game's mechanics"""

        raise NotImplementedError('Subclasses must implement this method')

    @abstractmethod
    def generate_board(self, size: int, rng: np.random.Generator) -> np.ndarray:
        """Generate a guaranteed-solvable starting board"""
        raise NotImplementedError('Subclasses must implement this method')

    @property
    def valid_sizes(self) -> list[int]:
        """
        Return a list of valid board sizes for this ruleset.
        :return:
        """

        step = 2 if self.even_only else 1
        start = self.min_size if not self.even_only or self.min_size % 2 == 0 else self.min_size + 1

        return [s for s in range(start, self.max_size + 1, step)]

    def validate_size(self, size: int) -> None:
        """Common validation shared by all rulesets."""

        if size not in self.valid_sizes:
            raise ValueError(f"Board size {size} is not valid for this ruleset. Valid sizes: {self.valid_sizes}")

        self.validate_custom_size(size)

    def validate_custom_size(self, size: int) -> None:
        """Optional hook for subclasses/strategies to enforce extra constraints."""
        pass


    @abstractmethod
    def is_solved(self, board: np.ndarray, mode: GameMode | None = None) -> bool:
        """Check if the board is in a solved state."""
        
        raise NotImplementedError('Subclasses must implement this method')

    @abstractmethod
    def solve(self, board: np.ndarray, mode: GameMode | None = None) -> list[tuple[int, int]]:
        """Compute optimal solution clicks."""
        raise NotImplementedError('Subclasses must implement this method')

    @staticmethod
    def is_all_on(board: np.ndarray) -> bool:
        return bool(np.all(board))

    @staticmethod
    def is_all_off(board: np.ndarray) -> bool:
        return bool(np.all(~board))

    @staticmethod
    def get_on_positions(board: np.ndarray) -> list[tuple[int, int]]:
        return list(zip(*np.where(board)))

    @staticmethod
    def get_off_positions(board: np.ndarray) -> list[tuple[int, int]]:
        return list(zip(*np.where(~board)))