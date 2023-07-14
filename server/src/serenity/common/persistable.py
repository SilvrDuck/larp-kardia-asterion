from abc import ABC, abstractmethod
from typing import Self

from serenity.common.io import RedisClient


class Persistable(ABC):
    redis = RedisClient()

    def persist(self) -> None:
        self.redis.set(self._get_save_key, self.to_dict())

    @classmethod
    def restore(cls) -> Self:
        return cls.from_dict(cls.redis.get(cls._get_save_key()))

    @classmethod
    def _get_save_key(cls) -> str:
        return f"SAVED_SERVICE_{cls.__name__}"

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
        prepared_data = cls._prepare_from_dict(data)

        class Blank:
            """Blank class for initialising from existing data."""

        obj = Blank()
        obj.__dict__.update(prepared_data)
        obj.__class__ = cls
        return obj
