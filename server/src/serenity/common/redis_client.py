import asyncio
from functools import singledispatchmethod
import logging
from math import log
from typing import Any, Optional, Type

import orjson
from pydantic import BaseModel
from redis.asyncio import StrictRedis
from redis.asyncio.lock import Lock

from serenity.common.config import settings
from serenity.common.definitions import (
    MessageType,
    Jsonable,
    ServiceType,
    Topic,
    RedisSignal,
)


class RedisMessage(BaseModel):
    type: MessageType
    concerns: Optional[ServiceType] = None
    data: Optional[Any] = None


class RedisClient:
    def __init__(self) -> None:
        host = settings.redis_host
        port = settings.redis_port

        self._client: StrictRedis = StrictRedis(host=host, port=port)

    async def get(self, key: str) -> Optional[Jsonable]:
        value = await self._client.get(key)
        if value is None:
            return None
        return orjson.loads(value)  # pylint: disable=maybe-no-member

    async def set(self, key: str, value: Jsonable) -> None:
        await self._client.set(key, orjson.dumps(value))  # pylint: disable=maybe-no-member

    async def publish(self, message: RedisMessage, topic: Topic) -> None:
        logging.debug("REDIS: Publishing, %s, %s", topic, str(message)[:70])
        await self._client.publish(topic.value, orjson.dumps(message.model_dump()))  # pylint: disable=maybe-no-member

    async def subscribtion_iterator(self, topic: Topic) -> RedisMessage:
        async with self._client.pubsub() as pubsub:
            await pubsub.subscribe(topic.value)
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)

                if message is not None:
                    logging.debug("REDIS: Subscription iterator tick, %s, %s", topic, str(message)[:70])
                    message = RedisMessage(**orjson.loads(message["data"]))  # pylint: disable=maybe-no-member

                    match message:
                        case RedisMessage(type=MessageType.SYSTEM, data=RedisSignal.SHUTDOWN):
                            return
                        case _:
                            yield message

    def get_lock(self, key: str) -> Lock:
        return self._client.lock(f"__lock__{hash(key)}")

    async def release_all_locks(self) -> None:
        await self._client.delete("__lock__*")

    async def terminate_all_channels(self) -> None:
        for topic in Topic:
            await self.publish(
                RedisMessage(type=MessageType.SYSTEM, data=RedisSignal.SHUTDOWN),
                topic,
            )
