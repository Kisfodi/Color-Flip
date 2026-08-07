import time
from backend.game_mode import GameMode
from .board import ColorFlipBoard


class Game:

    VALID_MODES = tuple(GameMode)

    def __init__(self, size: int, seed: int | None = None, mode: GameMode = GameMode.MIXED):
        # Validate size
        if not isinstance(size, int):
            raise ValueError("Board size must be an integer")
        if size % 2 != 0:
            raise ValueError("Board size must be even")
        if size < 2 or size > 20:
            raise ValueError("Board size must be between 2 and 20")
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid game mode '{mode}'. Valid modes: {self.VALID_MODES}")
        
        self._size = size
        self._seed = seed
        self._mode = mode

        self._start_time = None
        self._end_time = None
        self._solve_mode = False

        self.reset()

    def step(self, row: int, col: int):
        self._board.do_step(row, col)
        self._moves_made += 1
        return self.get_game_state()

    def get_game_state(self, serialize: bool = True):
        elapsed_time = self._get_elapsed_time()
        return {
            "board": self._board.get_board(serialize=serialize),
            "game_over": self.is_solved(),
            "moves_made": self._moves_made,
            "board_size": (self._size, self._size),
            "elapsed_time": elapsed_time,
            "mode": self._mode,
            "solve_mode": self._solve_mode,
            "solution_cells": self._get_solution_cells() if self._solve_mode else []
        }

    def _get_elapsed_time(self):

        if self._start_time is None:
            return 0
        end_time = self._end_time if self._end_time is not None else time.time()

        return end_time - self._start_time

    def reset(self):
        self._board = ColorFlipBoard(size=self._size, seed=self._seed)
        self._moves_made = 0
        self._solve_mode = False

        self._start_time = time.time()
        self._end_time = None

    def save_state(self):
        pass
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
    
    def is_game_over(self):
        """Check if game is over based on the current mode."""

        if self._mode == GameMode.ALL_ON:
            goal_reached = self._board.is_all_on()
        elif self._mode == GameMode.ALL_OFF:
            goal_reached = self._board.is_all_off()
        else:  # "mixed" mode
            goal_reached = self._board.is_all_on() or self._board.is_all_off()

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

    def _get_solution_cells(self):
        if self._mode == GameMode.ALL_ON:
            off_positions_to_press = self._get_positions_to_press(select_on_positions=False)
            return [[int(row), int(col)] for row, col in off_positions_to_press]

        if self._mode == GameMode.ALL_OFF:
            on_positions_to_press = self._get_positions_to_press(select_on_positions=True)
            return [[int(row), int(col)] for row, col in on_positions_to_press]

        on_positions_to_press = self._get_positions_to_press(select_on_positions=True)
        off_positions_to_press = self._get_positions_to_press(select_on_positions=False)

        if len(on_positions_to_press) <= len(off_positions_to_press):
            positions_to_press = list(on_positions_to_press.keys())
        else:
            positions_to_press = list(off_positions_to_press.keys())

        return [[int(row), int(col)] for row, col in positions_to_press]

    def _get_positions_to_press(self, select_on_positions: bool = True):
        positions_to_press = {}

        positions = self._board.get_on_positions() if select_on_positions else self._board.get_off_positions()

        for position in positions:

            row, col = position

            if position not in positions_to_press:
                positions_to_press[position] = 0
            positions_to_press[position] += 1

            for i in range(self._size):
                if (row, i) not in positions_to_press:
                    positions_to_press[(row, i)] = 0
                positions_to_press[(row, i)] += 1

                if (i, col) not in positions_to_press:
                    positions_to_press[(i, col)] = 0
                positions_to_press[(i, col)] += 1

        positions_to_press_filtered = dict(filter(lambda p: p[1] % 2 > 0, positions_to_press.items()))

        return positions_to_press_filtered
