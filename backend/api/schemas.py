from pydantic import BaseModel, Field, ConfigDict, field_validator
from backend.game_mode import GameMode

# ---------- Request Schemas ----------
class NewGameRequest(BaseModel):
    size: int | None = Field(default=None, ge=2, le=20, description="Board size (must be even, 2-20)")
    seed: int | None = Field(default=None, ge=0, description="Seed for reproducible board generation")
    mode: GameMode | None = Field(default=None, description="Game mode: all_on, all_off, or mixed")

    @field_validator("size")
    @classmethod
    def size_is_even(cls, value: int | None) -> int | None:
        if value is not None and value % 2 != 0:
            raise ValueError("Size must be even")
        return value

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"size": 6, "seed": 42, "mode": GameMode.MIXED},
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

class BoardColors(BaseModel):
    on_cell: str
    off_cell: str
    solution_highlight: str
    solution_glow_inner: str
    solution_glow_outer: str
    solution_border: str
    border: str

class ColorScheme(BaseModel):
    label: str
    board: BoardColors

class GameStateResponse(BaseModel):
    board: list[list[bool]] = Field(description="Current state of the game board, in row-major order")
    game_over: bool
    moves_made: int
    board_size: tuple[int, int]
    elapsed_time: float
    mode: GameMode
    solve_mode: bool
    solution_cells: list[tuple[int, int]] = Field(
        description="List of coordinates for solution cells, only populated if solve_mode is true"
    )