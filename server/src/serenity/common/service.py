import asyncio
from typing import Generic, Self, TypeVar
from pydantic import BaseModel
from abc import ABC, ABCMeta, abstractmethod
from serenity.common.definitions import Jsonable, MessageType, Topic

from serenity.common.redis_client import RedisClient, RedisMessage
from serenity.common.dict_convertible import DictConvertible
from redis.asyncio.lock import Lock

StateModel = TypeVar("StateModel", bound=BaseModel)
ConfigModel = TypeVar("ConfigModel", bound=BaseModel)


class Service(DictConvertible, ABC, Generic[StateModel, ConfigModel]):
    # -----------------------------------------------
    # Abstract methods
    # -----------------------------------------------

    @abstractmethod
    @classmethod
    def default_service(cls) -> Self:
        pass

    @abstractmethod
    def _update_state(self, state: StateModel) -> None:
        pass

    @abstractmethod
    def _to_state(self) -> StateModel:
        pass

    @abstractmethod
    def _update_config(self, config: ConfigModel) -> None:
        pass

    @abstractmethod
    def _to_config(self) -> ConfigModel:
        pass

    @abstractmethod
    async def _start(self) -> None:
        pass

    # -----------------------------------------------
    # Concrete methods
    # -----------------------------------------------

    redis = RedisClient()

    def __init__(self, state: StateModel, config: ConfigModel) -> None:
        self._update_state(state)
        self._update_config(config)

    async def get_self_lock(self) -> Lock:
        return await self.redis.get_lock(type(self).__name__)

    async def _persist(self) -> None:
        await self.redis.set(self._get_save_key, self.to_dict())

    @classmethod
    async def restore(cls) -> Self:
        return cls.from_dict(await cls.redis.get(cls._get_save_key()))

    @classmethod
    def _get_save_key(cls) -> str:
        return f"__PERSISTED_OBJECT__{cls.__name__}"

    async def start(self) -> None:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._start())
            tg.create_task(self._state_subscription())
            tg.create_task(self._config_subscription())

    async def _config_subscription(self) -> None:
        subscription = self.redis.subscribtion_iterator(Topic.CONFIG_TO_UPDATE)
        async for message in subscription:
            match message:
                case RedisMessage(type=MessageType.TRAVEL_CONFIG, data=config):
                    self.update_state(config)

    async def _state_subscription(self) -> None:
        subscription = self.redis.subscribtion_iterator(Topic.STATE_TO_UPDATE)
        async for message in subscription:
            match message:
                case RedisMessage(type=MessageType.TRAVEL_STATE, data=state):
                    self.update_state(state)

    async def _broadcast_config(self) -> None:
        await self.redis.publish(
            RedisMessage(type=MessageType.TRAVEL_CONFIG, data=self.to_config()),
            Topic.CONFIG,
        )

    async def update_config(self, config: ConfigModel) -> None:
        async with self.get_self_lock():
            self._update_config(config)
            await self._persist()
            await self._broadcast_config()

    async def _broadcast_state(self) -> None:
        await self.redis.publish(
            RedisMessage(type=MessageType.TRAVEL_STATE, data=self.to_state()),
            Topic.STATE,
        )

    async def update_state(self, state: StateModel) -> None:
        async with self.get_self_lock():
            self._update_state(state)
            await self._persist()
            await self._broadcast_state()

    def to_dict(self) -> Jsonable:
        return {
            "state": self._to_state(),
            "config": self._to_config(),
        }

    @classmethod
    def from_dict(cls, data: Jsonable) -> Self:
        return cls(
            state=cls._from_state(data["state"]),
            config=cls._from_config(data["config"]),
        )
