from abc import ABC, abstractmethod
from typing import Self

from serenity.common.io import RedisClient


class Persistable(ABC):
    client = RedisClient()

    def persist(self) -> None:
        self.client.set(self._get_save_key, self.to_dict())

    @classmethod
    def load(cls) -> Self:
        return cls.from_dict(cls.client.get(cls._get_save_key()))

    @classmethod
    def _get_save_key(cls) -> str:
        return f"SAVED_SERVICE_{cls.__name__}"

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @classmethod
    @abstractmethod
    def _prepare_from_dict(cls, data: dict) -> dict:
        """Class that deserialize underlying data for this class."""
        pass

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        prepared_data = cls._prepare_from_dict(data)

        class Blank:
            """Blank class for initialising from existing data."""

        obj = Blank()
        obj.__dict__.update(prepared_data)
        obj.__class__ = cls
        return obj
