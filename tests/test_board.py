import numpy as np
import pytest

from backend.board import ColorFlipBoard

# -------------------------
# Fixtures
# -------------------------

@pytest.fixture
def board():
    return ColorFlipBoard(size=6)

# -------------------------
# Initialization tests
# -------------------------

def test_board_size(board):
    assert board.get_board().shape == (6, 6)


def test_init_board_seed_reproducible():
    b1 = ColorFlipBoard(size=6, seed=0)
    b2 = ColorFlipBoard(size=6, seed=0)
    assert np.array_equal(b1.get_board(), b2.get_board())

def test_init_board_seed_changes_output():
    b1 = ColorFlipBoard(size=4, seed=0)
    b2 = ColorFlipBoard(size=4, seed=1)
    assert not np.array_equal(b1._board, b2._board)

def test_is_all_on():
    """Test is_all_on method returns True when all cells are ON."""
    board = ColorFlipBoard(size=4)
    board._board = np.ones_like(board._board, dtype=bool)
    assert board.is_all_on()
    assert not board.is_all_off()


def test_is_all_off():
    """Test is_all_off method returns True when all cells are OFF."""
    board = ColorFlipBoard(size=4)
    board._board = np.zeros_like(board._board, dtype=bool)
    assert board.is_all_off()
    assert not board.is_all_on()


def test_init_board_not_completed():
    """Test that initialized board is never in a completed state."""
    for _ in range(10):  # Multiple iterations to account for randomness
        board = ColorFlipBoard(size=4)
        # Board should never start in a completed state (all ON or all OFF)
        assert not (board.is_all_on() or board.is_all_off())

# -------------------------
# Step tests
# -------------------------

@pytest.mark.parametrize('row, col', [
    (0, 0),
    (1, 2),
    (3, 3)
])
def test_do_step_flips_value(board, row, col):

    board_before = board.get_board().copy()
    board.do_step(row, col)

    assert np.array_equal(
        board.get_board()[row, :], ~board_before[row, :]
    )
    assert np.array_equal(
        board.get_board()[:, col], ~board_before[:, col]
    )

def test_off_positions(board):
    board._board = np.array([[True, False, True],
                             [False, False, True],
                             [True, True, True]])
    off_positions = board.get_off_positions()
    expected_positions = [(0, 1), (1, 0), (1, 1)]
    assert set(off_positions) == set(expected_positions)

def test_on_positions(board):
    board._board = np.array([[True, False, True],
                             [False, False, True],
                             [True, True, True]])
    on_positions = board.get_on_positions()
    expected_positions = [(0, 0), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2)]
    assert set(on_positions) == set(expected_positions)

# -------------------------
# Randomness tests
# -------------------------

def test_board_contains_only_booleans(board):
    assert board.get_board().dtype == bool

def test_board_values(board):
    assert set(np.unique(board.get_board())).issubset({True, False})
