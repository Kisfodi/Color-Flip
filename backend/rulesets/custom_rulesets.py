from .pattern_ruleset import PatternRuleSet

diagonal_ruleset = PatternRuleSet(
    name="Diagonals",
    pattern=(
    (-1, -1),
    (-1, 1),
    (0, 0),
    (1, -1),
    (1, 1)
    )
)

moore_ruleset = PatternRuleSet(
    name="3x3 Block",
    pattern=(
    (-1, -1),   (-1, 0),    (-1, 1),
    (0, -1),    (0, 0),     (0, 1),
    (1, -1),    (1, 0),     (1, 1)
    )
)