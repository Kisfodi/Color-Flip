import numpy as np

class ColorFlipBoard:

    def __init__(self, size, seed=None):
        assert size > 0, "Board size must be greater than 0"
        assert size % 2 == 0, "Board size must be even"

        self._size = size
        self._seed = seed

        self._init_board()

    def _init_board(self):
        """Initialize an even-sized board with a random state that is not already completed."""
        if self._seed is not None:
            rng = np.random.default_rng(self._seed)

        # For even boards, ensure the board is not completed at initialization
        while True:
            if self._seed is not None:
                self._board = rng.integers(2, size=(self._size, self._size)).astype(bool)
            else:
                self._board = np.random.randint(2, size=(self._size, self._size)).astype(bool)
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

    def get_off_positions(self) -> list[tuple[int, int]]:
        off_positions = np.argwhere(self._board == False)

        return [tuple(pos) for pos in off_positions]

    def get_on_positions(self) -> list[tuple[int, int]]:
        on_positions = np.argwhere(self._board == True)

        return [tuple(pos) for pos in on_positions]
