from abc import abstractmethod
from abc import ABC

import numpy as np

from backend.game_mode import GameMode

class BasePuzzleRuleset(ABC):

    MIN_SIZE = 2
    MAX_SIZE = 20

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
    
    def validate_size(self, size: int) -> None:
        """Common validation shared by all rulesets."""
         
        if not isinstance(size, int):
            raise TypeError("Board size must be an integer.")
        if not (self.MIN_SIZE <= size <= self.MAX_SIZE):
            raise ValueError(f"Board size must be between {self.MIN_SIZE} and {self.MAX_SIZE}.")

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