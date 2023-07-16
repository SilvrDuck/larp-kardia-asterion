from abc import ABC, abstractmethod
from typing import Self

from serenity.common.redis_client import RedisClient


class Persistable(ABC):
    redis = RedisClient()

    def persist(self) -> None:
        self.redis.set(self._get_save_key, self.to_dict())

    @classmethod
    def restore(cls) -> Self:
        return cls.from_dict(cls.redis.get(cls._get_save_key()))

    def update(self, data: dict) -> None:
        try:
            prepared_data = self._prepare_from_dict(data)
        except Exception as err:
            raise ValueError(f"Invalid data for {type(self).__name__}: {err}")

        self.__dict__.update(prepared_data)

    @classmethod
    def _get_save_key(cls) -> str:
        return f"__PERSISTED_OBJECT__{cls.__name__}"

    @abstractmethod
    def to_dict(self) -> dict:
        """Class that serialize underlying data for this class."""

    @classmethod
    @abstractmethod
    def _prepare_from_dict(cls, data: dict) -> dict:
        """Class that deserialize underlying data for this class."""

    @classmethod
    def from_dict(cls, data: dict) -> Self:  # type: ignore
        #  type: ignore
        try:
            prepared_data = cls._prepare_from_dict(data)
        except Exception as err:
            raise ValueError(f"Invalid data for {cls.__name__}: {err}")

        class Blank:
            """Blank class for initialising from existing data."""

        obj = Blank()
        obj.__dict__.update(prepared_data)
        obj.__class__ = cls
        return obj
