from enum import Enum
from typing import Optional
from pydantic import BaseModel
from serenity.common.definitions import ServiceType, StatusBaseModel



class SoundState(StatusBaseModel):
    pass

    @staticmethod
    def to_key() -> ServiceType:
        return ServiceType.SOUND

class SoundConfig(StatusBaseModel):
    pass

    @staticmethod
    def to_key() -> ServiceType:
        return ServiceType.SOUND