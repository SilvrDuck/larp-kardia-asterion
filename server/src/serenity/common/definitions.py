from __future__ import annotations
from abc import ABC, abstractmethod

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
    PROPOSE_STATUS = "propose_status"
    BROADCAST_STATUS = "broadcast_status"
    SOUND = "sound"
    LIGHT = "light"


class MessageType(str, Enum):
    SYSTEM = "system"
    INIT = "init"
    STATE = "state"
    CONFIG = "config"
    TAKEOFF = "takeoff"


class ServiceType(str, Enum):
    SONAR = "sonar"
    TRAVEL = "travel"
    BATTLE = "battle"


class Owner(str, Enum):
    PLAYERS = "players"
    NPCS = "npcs"


class KeyedBaseModel(BaseModel, ABC):
    @staticmethod
    @abstractmethod
    def to_key() -> ServiceType:
        pass


class ShipModel(BaseModel):
    name: str
    hp: int


class Step(BaseModel):
    max_step_minutes: float = Field(..., ge=0.0)


class PlanetNode(Step):
    id: str
    name: str
    visited: bool
    description: str
    min_step_minutes: float = Field(..., ge=0)
    max_step_minutes: float = Field(..., ge=0)
    position_x: float
    position_y: float


class PlanetLink(Step):
    source: str
    target: str
    max_step_minutes: float = Field(..., ge=0)


class PlanetaryConfig(BaseModel):
    directed: bool = True
    multigraph: bool = False
    nodes: List[PlanetNode]
    links: List[PlanetLink]
