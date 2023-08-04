from enum import Enum
from typing import Optional
from pydantic import BaseModel
from serenity.common.definitions import ServiceType, StatusBaseModel


LIGHT_TOPIC = "color"

class Color(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    BLACK = "black"
    WHITE = "white"
    PURPLE = "purple"
    YELLOW = "yellow"
    CYAN = "cyan"

class Mode(str, Enum):
    SET = "set"
    BLINK = "blink"

class Light(BaseModel):
    color: Color
    mode: Mode
    secondary: Optional[Color] = None

    class Config:
        frozen = True

    def to_mqtt_message(self) -> str:
        secondary = self.secondary.value if self.secondary else ""
        return f"{self.color.value};{self.mode.value};{secondary}"

class LightState(StatusBaseModel):
    light: Light

    @staticmethod
    def to_key() -> ServiceType:
        return ServiceType.LIGHT


class LightConfig(StatusBaseModel):
    pass

    @staticmethod
    def to_key() -> ServiceType:
        return ServiceType.LIGHT