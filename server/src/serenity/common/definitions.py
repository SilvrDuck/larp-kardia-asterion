from __future__ import annotations
from abc import ABC, abstractmethod

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel


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
    START_BATTLE = "start_battle"
    END_BATTLE = "end_battle"
    LAUNCH_TORPEDO = "launch_torpedo"
    LAUNCH_MINE = "launch_mine"
    MOVE = "move"
    REPAIR = "repair"


class ServiceType(str, Enum):
    SONAR = "sonar"
    TRAVEL = "travel"
    LIGHT = "light"
    SWITCH = "switch"
    SOUND = "sound"


class Owner(str, Enum):
    PLAYERS = "players"
    NPCS = "npcs"


class StatusBaseModel(BaseModel, ABC):
    @staticmethod
    @abstractmethod
    def to_key() -> ServiceType:
        pass

class Direction(str, Enum):
    North = "north"
    South = "south"
    East = "east"
    West = "west"
