from __future__ import annotations

from enum import Enum, auto
from typing import Any, List, Dict

from pydantic import BaseModel
from datetime import datetime


Jsonable = None | int | str | bool | List[Any] | Dict[str, Any] | datetime | Enum


class RedisChannel(Enum):
    Travel = auto()


class Owner(Enum):
    Players = auto()
    NPCs = auto()


class ShipModel(BaseModel):
    name: str
    hp: int
