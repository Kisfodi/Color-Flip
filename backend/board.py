import numpy as np

class ColorFlipBoard:

    def __init__(self, size, seed=None, initial_state: list | None = None):
        assert size > 0, "Board size must be greater than 0"
        assert size % 2 == 0, "Board size must be even"

        self._size = size
        self._seed = seed

        if initial_state is not None:
            self._board = np.array(initial_state, dtype=bool)
        else:
            self._init_board()

    def _init_board(self):
        """Initialize an even-sized board with a random state that is not already completed."""
        rng = np.random.default_rng(self._seed)

        # For even boards, ensure the board is not completed at initialization
        while True:
            self._board = rng.integers(2, size=(self._size, self._size)).astype(bool)
            if not (self.is_all_on() or self.is_all_off()):
                break


    def do_step(self, row, col):

        self._board[row, col] = ~self._board[row, col]
        self._board[:, col] = ~self._board[:, col]
        self._board[row, :] = ~self._board[row, :]

    def get_board(self, serialize = False) -> np.ndarray | list:
        return self._board.tolist() if serialize else self._board

    def get_position_state(self, row, col) -> bool:
        return self._board[row, col]


    def is_all_on(self) -> bool:
        """Check if all cells are ON (True)."""
        return bool(np.all(self._board))

    def is_all_off(self) -> bool:
        """Check if all cells are OFF (False)."""
        return bool(np.all(~self._board))

    def get_off_positions(self):
        off_positions = np.argwhere(self._board == False)

        return [tuple(pos) for pos in off_positions]

    def get_on_positions(self):
        on_positions = np.argwhere(self._board == True)

        return [tuple(pos) for pos in on_positions]
