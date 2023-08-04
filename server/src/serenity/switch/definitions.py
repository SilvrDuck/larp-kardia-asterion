from __future__ import annotations
from enum import Enum
from typing import Dict

from numpy import number
from pydantic import BaseModel
from serenity.common.definitions import Direction, ServiceType, StatusBaseModel


class SwitchTopic(str, Enum):
    SWITCH = "switch"
    LED = "led"


class Function(str, Enum):
    WEAPON = "W"
    RADAR = "R"
    SILENCE = "S"
    NUCLEAR = "N"

class Group(str, Enum):
    RED = "R"
    BLUE = "B"
    GREEN = "G"
    NEUTRAL = "N"


class Switch(BaseModel):
    uid: str
    heading: Direction
    fixable: bool
    function: Function
    number: int
    group: Group

    class Config:
        frozen = True

    def to_message(self, is_on: bool) -> str:
        return f"{self.uid}{int(is_on)}"

    @staticmethod
    def _from_direction_code(code: str) -> Direction:
        match code:
            case "W":
                return Direction.West
            case "N":
                return Direction.North
            case "E":
                return Direction.East
            case "S":
                return Direction.South
        raise ValueError(f"Unkown direction code: {code}.")

    @classmethod
    def from_message(cls, message: str) -> Switch:
        cls.validate_message(message)
        return cls(
            uid=message[:5],
            heading=cls._from_direction_code(message[0]),
            fixable=message[1] == "F",
            function=Function(message[2]),
            number=int(message[3]),
            group=Group(message[4]),
        )

    @staticmethod
    def validate_message(message: str) -> None:
        if any(
            (
                len(message) != 5,
                message[0] not in "WESN",
                message[1] not in "NF",
                message[2] not in "WRSN",
                message[3] not in "01",
                message[4] not in "RGBN",
            )
        ):
            raise ValueError(f"Invalid switch UID: {message}")


class SwitchState(StatusBaseModel):
    switches: Dict[Switch, bool]

    @staticmethod
    def to_key() -> ServiceType:
        return ServiceType.SWITCH


class SwitchConfig(StatusBaseModel):
    pass

    @staticmethod
    def to_key() -> ServiceType:
        return ServiceType.SWITCH
