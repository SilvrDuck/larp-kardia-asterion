import orjson
from redis.asyncio import StrictRedis

from serenity.common.config import settings
from serenity.common.definitions import Jsonable, RedisChannel


class RedisClient:
    def __init__(self):
        host = settings.redis_host
        port = settings.redis_port

        self._client = StrictRedis(host=host, port=port)

    async def get(self, key: str) -> str:
        value = await self._client.get(key)
        if value is None:
            return None
        return orjson.loads(value)

    async def set(self, key: str, value: Jsonable) -> None:
        await self._client.set(key, orjson.dumps(value))

    async def publish(self, channel: RedisChannel, message: Jsonable) -> None:
        await self._client.publish(channel, orjson.dumps(message))

    async def subscribtion_iterator(self, channel: str) -> None:
        async with self._client.pubsub() as pubsub:
            await pubsub.subscribe(channel)
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    data = message["data"]
                    if data is not None:
                        yield orjson.loads(data)
