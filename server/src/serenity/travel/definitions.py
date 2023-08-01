from pydantic import Field
from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel
from serenity.common.definitions import StatusBaseModel, ServiceType


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
    period: str
    satellites: str
    radius: str


class PlanetLink(Step):
    source: str
    target: str
    max_step_minutes: float = Field(..., ge=0)


class PlanetaryConfig(BaseModel):
    directed: bool = True
    multigraph: bool = False
    nodes: List[PlanetNode]
    links: List[PlanetLink]


class ShipState(str, Enum):
    Paused = "paused"
    Landed = "landed"
    Traveling = "traveling"


class TravelState(StatusBaseModel):
    ship_state: ShipState
    planetary_config: PlanetaryConfig
    step_start: datetime
    pause_start: datetime
    step_duration_minutes: float
    current_step_id: str | tuple[str, str]

    @staticmethod
    def to_key() -> ServiceType:
        return ServiceType.TRAVEL


class TravelConfig(StatusBaseModel):
    travel_tick_seconds: float

    @staticmethod
    def to_key() -> ServiceType:
        return ServiceType.TRAVEL
