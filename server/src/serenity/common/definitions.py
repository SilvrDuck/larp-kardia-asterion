from enum import Enum, auto

from pydantic import BaseModel


class Owner(Enum):
    Players = auto()
    NPCs = auto()


class ShipModel(BaseModel):
    name: str
    hp: int
