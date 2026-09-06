from .base_puzzle_ruleset import BasePuzzleRuleset
from .color_flip_ruleset import ColorFlipRuleSet
from .lights_out_ruleset import LightsOutRuleset

__all__ = [
    'BasePuzzleRuleset',
    'ColorFlipRuleSet',
    'LightsOutRuleset',
    'RULESETS',
    'get_ruleset',
]

RULESETS: dict[str, type[BasePuzzleRuleset]] = {
    "color_flip": ColorFlipRuleSet,
    "lights_out": LightsOutRuleset,
}

def get_ruleset(ruleset: str | BasePuzzleRuleset) -> BasePuzzleRuleset:

    if isinstance(ruleset, BasePuzzleRuleset):
        return ruleset

    if ruleset not in RULESETS:
        raise ValueError(f"Ruleset '{ruleset}' is not supported. Supported rulesets: {list(RULESETS.keys())}")
    return RULESETS[ruleset]()