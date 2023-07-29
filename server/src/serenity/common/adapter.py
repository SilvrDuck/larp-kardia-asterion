from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from typing import Type

from serenity.common.definitions import Jsonable, StatusBaseModel
from serenity.common.redis_client import RedisMessage
import logging

T = TypeVar("T", bound=StatusBaseModel)


class Adapter(ABC, Generic[T]):
    @property
    @abstractmethod
    def status_model(self) -> Type[T]:
        pass

    @classmethod
    def adapt(cls, message: RedisMessage) -> Jsonable:
        """Adapts a message for its downstream use, e.g. in a websocket message."""

        model = cls.status_model(**message.data)  # pylint: disable=assignment-from-no-return

        return cls._adapt(model)

    @classmethod
    @abstractmethod
    def _adapt(cls, model: T) -> Jsonable:
        pass
