from __future__ import annotations

from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Tuple

from pydantic import BaseModel, Field

Jsonable = None | int | str | bool | List[Any] | Dict[str, Any] | datetime | Enum

SHUTDOWN_SIGNAL = "__shutdown__"


class RedisChannel(Enum):
    DASHBOARDS = "dashboards"


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
    react_flow_graph: dict


class Step(BaseModel):
    max_step_minutes: float = Field(..., ge=0.0)


class PlanetNode(Step):
    id: str
    name: str
    visited: bool
    description: str
    min_step_minutes: float = Field(..., ge=0)
    position_x: float
    position_y: float


class PlanetLink(Step):
    source: str
    target: str


class PlanetaryConfig(BaseModel):
    directed: bool = True
    multigraph: bool = False
    nodes: List[PlanetNode]
    links: List[PlanetLink]
