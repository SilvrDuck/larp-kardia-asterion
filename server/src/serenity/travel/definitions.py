from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from serenity.common.definitions import Jsonable, StatusBaseModel, PlanetaryConfig, ServiceType
from serenity.travel.planet_graph import PlanetGraph


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
    def to_key() -> str:
        return ServiceType.TRAVEL


class TravelConfig(StatusBaseModel):
    travel_tick_seconds: float

    @staticmethod
    def to_key() -> str:
        return ServiceType.TRAVEL
