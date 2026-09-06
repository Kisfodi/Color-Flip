from pydantic import BaseModel, Field, ConfigDict, model_validator
from backend.game_mode import GameMode

# ---------- Request Schemas ----------
class NewGameRequest(BaseModel):
    size: int | None = Field(default=None, ge=2, le=20, description="Board size (2-20)")
    seed: int | None = Field(default=None, ge=0, description="Seed for reproducible board generation")
    mode: GameMode | None = Field(default=None, description="Game mode: all_on, all_off, or mixed")
    ruleset: str | None = Field(default="color_flip", description="Ruleset variant: color_flip or lights_out")

    @model_validator(mode="after")
    def validate_size_for_ruleset(self) -> "NewGameRequest":
        if self.size is not None:
            ruleset_name = self.ruleset or "color_flip"
            if ruleset_name == "color_flip" and self.size % 2 != 0:
                raise ValueError("Size must be even for Color Flip")
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"size": 6, "seed": 42, "mode": GameMode.MIXED, "ruleset": "color_flip"},
            ]
        }
    )

class StepRequest(BaseModel):
    row: int = Field(ge=0, description="Row index of the cell to flip")
    col: int = Field(ge=0, description="Column index of the cell to flip")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"row": 0, "col": 0}
            ]
        }
    )


class SolveGameRequest(BaseModel):
    enabled: bool | None = Field(default=None, description="Enable or disable solver hints")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"enabled": True}
            ]
        }
    )

# ---------- Response Schemas ----------

class ConfigResponse(BaseModel):
    size: int = Field(description="Default board size")
    seed: int | None = Field(description="Seed for reproducible board generation")
    color_scheme: str = Field(description="Default color scheme name")
    mode: GameMode = Field(description="Default game mode")
    ruleset: str = Field(default="color_flip", description="Default ruleset")
    rulesets: list[str] = Field(default_factory=lambda: ["color_flip", "lights_out"], description="Available rulesets")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"size": 6, "seed": 42, "color_scheme": "black_gold_elegance", "mode": "mixed", "ruleset": "color_flip"},
            ]
        }
    )

class BoardColors(BaseModel):
    on_cell: str
    off_cell: str
    solution_highlight: str
    solution_glow_inner: str
    solution_glow_outer: str
    solution_border: str
    border: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "on_cell": "#fca311",
                    "off_cell": "#14213d",
                    "solution_highlight": "#E5E5E5",
                    "solution_glow_inner": "rgba(229, 229, 229, 0.9)",
                    "solution_glow_outer": "rgba(229, 229, 229, 0.7)",
                    "solution_border": "#E5E5E5",
                    "border": "#000000",
                }
            ]
        }
    )

class ColorScheme(BaseModel):
    label: str
    board: BoardColors

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "label": "Black & Gold Elegance",
                    "board": {
                        "on_cell": "#fca311",
                        "off_cell": "#14213d",
                        "solution_highlight": "#E5E5E5",
                        "solution_glow_inner": "rgba(229, 229, 229, 0.9)",
                        "solution_glow_outer": "rgba(229, 229, 229, 0.7)",
                        "solution_border": "#E5E5E5",
                        "border": "#000000",
                    }
                }
            ]
        }
    )


class GameStateResponse(BaseModel):
    game_id: str | None = Field(default=None, description="Unique UUID for this game session")
    seed: int | None = Field(default=None, description="Seed used for reproducible board generation")
    board: list[list[bool]] = Field(description="Current state of the game board, in row-major order")
    initial_board: list[list[bool]] | None = Field(default=None, description="Initial state of the game board")
    game_over: bool
    moves_made: int
    board_size: tuple[int, int]
    elapsed_time: float
    mode: GameMode
    ruleset: str = Field(default="color_flip", description="Current ruleset")
    solve_mode: bool
    solution_cells: list[list[int]] | list[tuple[int, int]] = Field(
        description="List of coordinates for solution cells, only populated if solve_mode is true"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "board": [[True, False], [False, True]],
                    "game_over": False,
                    "moves_made": 3,
                    "board_size": [2, 2],
                    "elapsed_time": 12.4,
                    "mode": "mixed",
                    "ruleset": "color_flip",
                    "solve_mode": True,
                    "solution_cells": [[0, 1], [1, 0]]
                }
            ]
        }
    )