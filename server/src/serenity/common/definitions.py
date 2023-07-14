from __future__ import annotations

from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Tuple

from pydantic import BaseModel, Field

Jsonable = None | int | str | bool | List[Any] | Dict[str, Any] | datetime | Enum


class RedisChannel(Enum):
    TRAVEL = auto()


class Owner(Enum):
    PLAYERS = auto()
    NPCS = auto()


class ShipModel(BaseModel):
    name: str
    hp: int


class GameState(BaseModel):
    current_step_id: str | Tuple[str, str]
    is_in_battle: bool
    step_completion: float = Field(..., ge=0.0, le=1.0)


class Step(BaseModel):
    max_step_minutes: float = Field(..., ge=0.0)


class PlanetNode(Step):
    id: str
    name: str
    description: str
    min_step_minutes: float = Field(..., ge=0)


class PlanetLink(Step):
    source: str
    target: str


class PlanetaryConfig(BaseModel):
    directed: bool = True
    multigraph: bool = False
    nodes: List[PlanetNode]
    links: List[PlanetLink]
