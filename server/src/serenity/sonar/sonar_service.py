import asyncio

from redis.asyncio import StrictRedis

from serenity.common.persistable import Persistable


class SonarService(Persistable):
    def __init__(self):
        self.redis = StrictRedis.from_url("redis://localhost:6379")
        self.grid = {"lol": "lol"}

    async def run(self):
        async with self.redis.pubsub() as pubsub:
            await pubsub.subscribe("chat:c")

            consumer_task = asyncio.create_task(self.produce(self.redis))
            producer_task = asyncio.create_task(self.consume(pubsub))

            done, pending = await asyncio.wait(
                [consumer_task, producer_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()

    async def consume(self, redis):
        while True:
            message = await redis.get_message(ignore_subscribe_messages=True)
            if message is not None:
                data = message["data"].decode()
                print("client told us that sonar is:", data)
                self.grid["lol"] = data

    async def produce(self, pubsub):
        while True:
            await asyncio.sleep(4)
            self.grid["lol"] = self.grid["lol"] + "acted"
            print("sonar is now:", self.grid["lol"])
            await pubsub.publish("chat:c", str(self.grid["lol"]))

    def from_dict(self, d: dict):
        pass

    def to_dict(self) -> dict:
        pass
