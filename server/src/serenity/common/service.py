import asyncio
from typing import Generic, List, Self, TypeVar
from pydantic import BaseModel
from abc import ABC, ABCMeta, abstractmethod
from serenity.common.definitions import Jsonable, KeyedBaseModel, MessageType, ServiceType, Topic
import logging
from serenity.common.redis_client import RedisClient, RedisMessage
from serenity.common.dict_convertible import DictConvertible
from redis.asyncio.lock import Lock


StateModel = TypeVar("StateModel", bound=KeyedBaseModel)
ConfigModel = TypeVar("ConfigModel", bound=KeyedBaseModel)


class Service(DictConvertible, ABC, Generic[StateModel, ConfigModel]):
    # -----------------------------------------------
    # Abstract methods
    # -----------------------------------------------

    @property
    @classmethod
    @abstractmethod
    def state(cls) -> StateModel:
        pass

    @property
    @classmethod
    @abstractmethod
    def config(cls) -> ConfigModel:
        pass

    @classmethod
    @abstractmethod
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

    state: StateModel = StateModel

    redis = RedisClient()

    def __init__(self, state: StateModel, config: ConfigModel) -> None:
        self._update_state(state)
        self._update_config(config)

    def get_self_lock(self) -> Lock:
        return self.redis.get_lock(type(self).__name__)

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
        subscription = self.redis.subscribtion_iterator(Topic.PROPOSE_STATUS)
        async for message in subscription:
            key = self.state.to_key()
            match message:
                case RedisMessage(type=MessageType.STATE, data=config):
                    if key == message.concerns:
                        await self.update_state(config)
                case RedisMessage(type=MessageType.INIT):
                    if key == message.concerns:
                        await self._broadcast_config()

    async def _state_subscription(self) -> None:
        subscription = self.redis.subscribtion_iterator(Topic.PROPOSE_STATUS)
        async for message in subscription:
            key = self.state.to_key()
            match message:
                case RedisMessage(type=MessageType.CONFIG, data=state):
                    if key == message.concerns:
                        await self.update_state(state)
                case RedisMessage(type=MessageType.INIT):
                    if key == message.concerns:
                        await self._broadcast_state()

    async def _broadcast_config(self) -> None:
        await self.redis.publish(
            RedisMessage(type=MessageType.CONFIG, concerns=self.config.to_key(), data=self._to_config()),
            Topic.BROADCAST_STATUS,
        )

    async def update_config(self, config: ConfigModel) -> None:
        async with self.get_self_lock():
            self._update_config(config)
            await self._persist()
            await self._broadcast_config()

    async def _broadcast_state(self) -> None:
        await self.redis.publish(
            RedisMessage(type=MessageType.STATE, concerns=self.state.to_key(), data=self._to_state()),
            Topic.BROADCAST_STATUS,
        )

    async def update_state(self, state: StateModel) -> None:
        async with self.get_self_lock():
            self._update_state(state)
            await self._persist()
            await self._broadcast_state()

    def to_dict(self) -> Jsonable:
        return {
            "state": self._to_state().model_dump(),
            "config": self._to_config().model_dump(),
        }

    @classmethod
    def from_dict(cls, data: Jsonable) -> Self:
        return cls(
            state=cls.state(**data["state"]),
            config=cls.config(**data["config"]),
        )
