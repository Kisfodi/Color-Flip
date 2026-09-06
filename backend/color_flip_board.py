from __future__ import annotations

from .board import Board
from .rulesets import ColorFlipRuleSet


class ColorFlipBoard(Board):
    """Backwards-compatible convenience subclass for Color-Flip boards."""
    def __init__(self, size: int, seed: int | None = None, initial_state: list | None = None):
        super().__init__(size=size, ruleset=ColorFlipRuleSet(), seed=seed, initial_state=initial_state)
