import asyncio
from functools import singledispatchmethod
from typing import Optional

import orjson
from pydantic import BaseModel
from redis.asyncio import StrictRedis
from redis.asyncio.lock import Lock

from serenity.common.config import settings
from serenity.common.definitions import (
    SHUTDOWN_SIGNAL,
    Jsonable,
    RedisChannel,
    RedisSignal,
)


class RedisClient:
    def __init__(self) -> None:
        host = settings.redis_host
        port = settings.redis_port

        self._client: StrictRedis = StrictRedis(host=host, port=port)

    async def get(self, key: str) -> Optional[Jsonable]:
        value = await self._client.get(key)
        if value is None:
            return None
        return orjson.loads(value)

    async def set(self, key: str, value: Jsonable) -> None:
        await self._client.set(key, orjson.dumps(value))

    @singledispatchmethod
    async def publish(self, message: Jsonable, channel: RedisChannel) -> None:
        await self._client.publish(channel.value, orjson.dumps(message))

    @publish.register
    async def _(self, message: BaseModel, channel: RedisChannel) -> None:
        await self.publish(message.model_dump(), channel)

    async def subscribtion_iterator(self, channel: RedisChannel) -> Optional[Jsonable]:
        async with self._client.pubsub() as pubsub:
            await pubsub.subscribe(channel.value)
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    message = self._treat_subscription_message(message)

                    if message == RedisSignal.SHUTDOWN.value:
                        return

                    yield message

    def _treat_subscription_message(self, message: dict) -> Optional[Jsonable]:
        data = message["data"]
        if data is not None:
            return orjson.loads(data)

        return None

    def get_lock(self, key: str) -> Lock:
        return self._client.lock(f"__lock__{hash(key)}")

    async def release_all_locks(self) -> None:
        await self._client.delete("__lock__*")

    async def terminate_all_channels(self) -> None:
        for channel in RedisChannel:
            await self.publish(RedisSignal.SHUTDOWN, channel)
