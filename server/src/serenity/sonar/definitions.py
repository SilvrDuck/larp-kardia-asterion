from __future__ import annotations
from enum import Enum
from typing import Dict, Set
from mimetypes import init

from typing import List, Self
from dataclasses import dataclass
from dataclasses import field
import uuid

from pydantic import BaseModel, Field, PrivateAttr
from typing import Optional
from serenity.common.definitions import Owner, StatusBaseModel, ServiceType
from serenity.sonar.exceptions import ShipDestroyed
from abc import ABC


@dataclass(frozen=True)
class GridPosition:
    x: int
    y: int


class GameActor(BaseModel, ABC):
    type: str
    owner: Optional[Owner] = Field(None, examples=[Owner.NPCS])

    class Config:
        frozen = True


class Damage(GameActor):
    type: str = "damage"
    amount: int


class Trail(GameActor):
    type: str = "trail"


class Ship(GameActor):
    type: str = "ship"
    name: str = Field(..., examples=["Reaver"])

    total_hp: int = Field(..., ge=0, examples=[3])
    hp: Optional[int] = Field(None, ge=1, examples=[3])

    def __init__(self, **data) -> None:
        if "hp" not in data or data["hp"] is None:
            data["hp"] = data["total_hp"]

        if data["hp"] > data["total_hp"]:
            data["hp"] = data["total_hp"]

        super().__init__(**data)

    def apply_damage(self, damage: int) -> Self:
        if self.hp - damage <= 0:
            raise ShipDestroyed(self)
        return Ship(name=self.name, hp=self.hp - damage, total_hp=self.total_hp, owner=self.owner)


class Launchable(GameActor):
    damage: int
    reach: int
    radius: int


class Mine(Launchable):
    type: str = "mine"
    uid: str = "__unset__"

    def __init__(self, **data) -> None:
        data["uid"] = str(uuid.uuid4())
        super().__init__(**data)


class Torpedo(Launchable):
    type: str = "torpedo"


class Asteroid(GameActor):
    type: str = "asteroid"


class CellModel(BaseModel):
    content: Set[GameActor]
    has_asteroid: bool


class MapModel(BaseModel):
    width: int
    height: int
    grid: List[List[CellModel]]
    player_ship: Ship
    npc_ship: Ship
    ship_positions: Dict[Owner, GridPosition]
    mine_positions: Dict[str, GridPosition]


class SonarState(StatusBaseModel):
    in_battle: bool
    map: Optional[MapModel]

    @staticmethod
    def to_key() -> ServiceType:
        return ServiceType.SONAR


class SonarConfig(StatusBaseModel):
    torpedo_damage: int
    torpedo_reach: int
    torpedo_radius: int
    mine_damage: int
    mine_reach: int
    mine_radius: int
    player_default_hp: int
    use_control_panel: bool

    @staticmethod
    def to_key() -> ServiceType:
        return ServiceType.SONAR


class MapType(str, Enum):
    ALPHA = "alpha"
    BRAVO = "bravo"
    CHARLIE = "charlie"


class Battle(BaseModel):
    map: MapType
    ship: Ship
