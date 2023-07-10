import orjson
from redis import StrictRedis

from serenity.config import settings


class RedisClient:
    def __init__(self):
        host = settings.redis_host
        port = settings.redis_port

        self._client = StrictRedis(host=host, port=port)

    def get(self, key: str) -> str:
        return orjson.loads(self._client.get(key))

    def set(self, key: str, value: str) -> None:
        self._client.set(key, orjson.dumps(value))

    def delete(self, key: str) -> None:
        self._client.delete(key)
