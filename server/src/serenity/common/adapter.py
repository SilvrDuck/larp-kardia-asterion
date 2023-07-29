from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from typing import Type

from serenity.common.definitions import Jsonable, StatusBaseModel
from serenity.common.redis_client import RedisMessage
from pydantic import ValidationError

T = TypeVar("T", bound=StatusBaseModel)


class Adapter(ABC, Generic[T]):
    @property
    @abstractmethod
    def status_model(self) -> Type[T]:
        pass

    @classmethod
    def adapt_if_needed(cls, message: RedisMessage) -> RedisMessage:
        """Adapts a message for its downstream use, e.g. in a websocket message."""

        try:
            modeled_data = cls.status_model(**message.data)  # pylint: disable=assignment-from-no-return
        except ValidationError:
            # Message does not concern this adapter
            return message

        new_data = cls._adapt(modeled_data)
        return RedisMessage(
            topic=message.topic,
            type=message.type,
            concerns=message.concerns,
            data=new_data,
        )

    @classmethod
    @abstractmethod
    def _adapt(cls, model: T) -> Jsonable:
        pass
