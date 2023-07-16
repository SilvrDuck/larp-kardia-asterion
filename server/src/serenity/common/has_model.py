from abc import ABC, abstractmethod, ABCMeta
from typing import Generic, Self, TypeVar


from pydantic import BaseModel
from serenity.common.definitions import Jsonable


class HasDictRepr(ABC):
    @abstractmethod
    def to_dict(self) -> Jsonable:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Jsonable) -> Self:
        pass
