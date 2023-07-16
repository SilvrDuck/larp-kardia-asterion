from __future__ import annotations

from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Tuple

from pydantic import BaseModel, Field

Jsonable = None | int | str | bool | List[Any] | Dict[str, Any] | datetime | Enum


class RedisSignal(str, Enum):
    SHUTDOWN = "__shutdown__"
    STOP_BATTLE = "__stop_battle__"


class Topic(str, Enum):
    COMMAND = "command"
    STATE = "state"
    STATE_TO_UPDATE = "state_to_update"
    CONFIG = "config"
    CONFIG_TO_UPDATE = "config_to_update"
    SOUND = "sound"
    LIGHT = "light"


class MessageType(str, Enum):
    SYSTEM = "system"
    SONAR_STATE = "sonar_state"
    SONAR_CONFIG = "sonar_config"
    TRAVEL_STATE = "travel_state"
    TRAVEL_CONFIG = "travel_config"
    TRAVEL_TAKEOFF = "travel_takeoff"


class Owner(str, Enum):
    PLAYERS = "players"
    NPCS = "npcs"


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
