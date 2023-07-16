from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from serenity.common.definitions import Jsonable, PlanetaryConfig
from serenity.travel.planet_graph import PlanetGraph


class ShipState(str, Enum):
    Paused = "paused"
    Landed = "landed"
    Travelling = "travelling"


class TravelState(BaseModel):
    ship_state: ShipState
    planetary_config: PlanetaryConfig
    step_start: datetime
    pause_start: datetime
    step_duration_minutes: float
    current_step_id: str | tuple[str, str]


class TravelConfig(BaseModel):
    pass
