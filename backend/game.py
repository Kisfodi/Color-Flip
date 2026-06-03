from .board import ColorFlipBoard
import time

class Game:

    VALID_MODES = ("all_on", "all_off", "mixed")

    def __init__(self, size: int, seed: int = None, mode: str = "mixed"):
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
        self._elapsed_time = 0

        self.reset()

    def step(self, row: int, col: int):
        self._board.do_step(row, col)
        self._moves_made += 1
        return self.get_game_state()

    def get_game_state(self, serialize: bool = True):
        elapsed = time.time() - self._start_time if self._start_time else 0
        return {
            "board": self._board.get_board(serialize=serialize),
            "game_over": self.is_solved(),
            "moves_made": self._moves_made,
            "board_size": (self._size, self._size),
            "elapsed_time": elapsed,
            "mode": self._mode
        }

    def reset(self):
        self._board = ColorFlipBoard(size=self._size, seed=self._seed)
        self._moves_made = 0

        self._start_time = time.time()
        self._elapsed_time = 0

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
        return self.get_game_state()

    @property
    def board(self):
        """Return the current board state in a reusable format."""
        return self._board.get_board(serialize=True)
    
    def is_solved(self):
        """Check if game is over based on the current mode."""
        goal_reached = False

        if self._mode == "all_on":
            # Goal: all cells are ON (True)
            goal_reached = self._board.is_all_on()
        elif self._mode == "all_off":
            # Goal: all cells are OFF (False)
            goal_reached = self._board.is_all_off()
        else:  # "mixed" mode
            # Goal: either all ON or all OFF
            goal_reached = self._board.is_all_on() or self._board.is_all_off()

        if goal_reached and self._start_time:
            self._elapsed_time = time.time() - self._start_time
            self._start_time = None

        return goal_reached

    def solve_game(self):
        """Solve the game based on the current mode."""
        if self._mode == "all_on":
            return self._solve_to_all_on()
        elif self._mode == "all_off":
            return self._solve_to_all_off()
        else:  # "mixed" mode
            return self._solve_to_mixed()

    def _solve_to_all_on(self):
        """Solve the game to get all cells to ON state."""
        # Find which cells are currently OFF
        off_positions_to_press = self._get_positions_to_press(select_on_positions=False)

        # Convert to list of [row, col] pairs
        solution_cells = [[int(row), int(col)] for row, col in off_positions_to_press]

        game_state = self.get_game_state()
        game_state["solution_cells"] = solution_cells
        return game_state

    def _solve_to_all_off(self):
        """Solve the game to get all cells to OFF state."""
        # Find which cells are currently ON
        on_positions_to_press = self._get_positions_to_press(select_on_positions=True)

        # Convert to list of [row, col] pairs
        solution_cells = [[int(row), int(col)] for row, col in on_positions_to_press]

        game_state = self.get_game_state()
        game_state["solution_cells"] = solution_cells
        return game_state

    def _solve_to_mixed(self):
        """Solve the even board for mixed mode (either all ON or all OFF)."""
        on_positions_to_press = self._get_positions_to_press(select_on_positions=True)
        off_positions_to_press = self._get_positions_to_press(select_on_positions=False)

        # Choose the set with fewer moves
        if len(on_positions_to_press) <= len(off_positions_to_press):
            positions_to_press = list(on_positions_to_press.keys())
        else:
            positions_to_press = list(off_positions_to_press.keys())

        # Convert positions to serializable format
        solution_cells = [[int(row), int(col)] for row, col in positions_to_press]

        game_state = self.get_game_state()
        game_state["solution_cells"] = solution_cells
        return game_state


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
