import pytest
import numpy as np

from backend.rulesets import (
    BasePuzzleRuleset,
    ColorFlipRuleSet,
    LightsOutRuleset,
    PatternRuleSet,
    get_ruleset,
)
from backend.rulesets.custom_rulesets import diagonal_ruleset, moore_ruleset
from backend.game_mode import GameMode


def test_color_flip_ruleset_properties():
    cf = ColorFlipRuleSet()
    assert cf.min_size == 2
    assert cf.even_only is True
    assert 2 in cf.valid_sizes
    assert 3 not in cf.valid_sizes
    assert 4 in cf.valid_sizes

    # Validation
    cf.validate_size(4)
    with pytest.raises(ValueError):
        cf.validate_size(3)
    with pytest.raises(ValueError):
        cf.validate_size(1)


def test_color_flip_apply_step():
    cf = ColorFlipRuleSet()
    board = np.zeros((4, 4), dtype=bool)

    # Click (0, 0): flips row 0, col 0, and (0, 0)
    res = cf.apply_step(board, 0, 0)
    # Check that row 0 and col 0 are flipped (True)
    assert np.all(res[0, :])
    assert np.all(res[:, 0])
    # Other cells are unchanged (False)
    assert not np.any(res[1:, 1:])


def test_lights_out_auto_min_size():
    lo = LightsOutRuleset()
    # Classic cross has span 3
    assert lo.min_size == 3
    assert 3 in lo.valid_sizes
    assert 2 not in lo.valid_sizes

    lo.validate_size(3)
    lo.validate_size(5)
    with pytest.raises(ValueError):
        lo.validate_size(2)


def test_lights_out_apply_step():
    lo = LightsOutRuleset()
    board = np.zeros((3, 3), dtype=bool)

    # Click center (1, 1) in 3x3: cross toggles (1,1), (0,1), (2,1), (1,0), (1,2)
    lo.apply_step(board, 1, 1)
    assert board[1, 1]
    assert board[0, 1]
    assert board[2, 1]
    assert board[1, 0]
    assert board[1, 2]
    # Corners are unchanged (False)
    assert not board[0, 0]
    assert not board[0, 2]
    assert not board[2, 0]
    assert not board[2, 2]



def test_pattern_ruleset_auto_min_size():
    # 1D pattern: horizontal 3-cell bar
    h_bar = PatternRuleSet("Bar", [(0, -1), (0, 0), (0, 1)])
    assert h_bar.min_size == 3

    # Knight pattern: span is 5
    knight = PatternRuleSet("Knight", [(-2, -1), (-2, 1), (2, -1), (2, 1)])
    assert knight.min_size == 5

    # Explicit override: higher min_size
    large_knight = PatternRuleSet("LargeKnight", [(-2, -1), (2, 1)], min_size=8)
    assert large_knight.min_size == 8

    # Diagonals & Moore from custom_rulesets
    assert diagonal_ruleset.min_size == 3
    assert moore_ruleset.min_size == 3


def test_get_ruleset_factory():
    cf = get_ruleset("color_flip")
    assert isinstance(cf, ColorFlipRuleSet)

    lo = get_ruleset("lights_out")
    assert isinstance(lo, LightsOutRuleset)

    # Passing existing instance returns as-is
    assert get_ruleset(cf) is cf

    # Invalid name raises ValueError
    with pytest.raises(ValueError):
        get_ruleset("unknown_variant")


def test_pattern_solve_gf2():
    lo = LightsOutRuleset()
    # 3x3 board where center is ON
    board = np.zeros((3, 3), dtype=bool)
    board[1, 1] = True
    board[0, 1] = True
    board[2, 1] = True
    board[1, 0] = True
    board[1, 2] = True

    # Clicking (1, 1) should turn all off
    solution = lo.solve(board, mode=GameMode.ALL_OFF)
    assert (1, 1) in solution
