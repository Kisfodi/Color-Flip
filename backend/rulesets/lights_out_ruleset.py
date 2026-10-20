from backend.game_mode import GameMode
from .pattern_ruleset import PatternRuleSet


class LightsOutRuleset(PatternRuleSet):

    """
    Classic Light Out puzzle ruleset.
    The goal is to turn off all lights on the board. Clicking a cell toggles its state and the states of its immediate neighbors (up, down, left, right).
    """

    CLASSIC_CROSS_OFFSETS = (
        (-1, 0),
        (1, 0),
        (0, 0),
        (0, -1),
        (0, 1)
    )

    def __init__(self, min_size: int | None = None, max_size: int = 20):
        super().__init__(
            name="Lights Out",
            pattern=self.CLASSIC_CROSS_OFFSETS,
            supported_modes=(GameMode.ALL_OFF, ),
            min_size=min_size,
            max_size=max_size,
        )
