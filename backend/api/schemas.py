from typing import Optional

from pydantic import BaseModel


class NewGameRequest(BaseModel):
    size: Optional[int] = None
    seed: Optional[int] = None
    mode: Optional[str] = None


class StepRequest(BaseModel):
    row: int
    col: int


class SolveGameRequest(BaseModel):
    enabled: Optional[bool] = None
