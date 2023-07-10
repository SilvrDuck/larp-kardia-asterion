import asyncio

import redis.asyncio as redis

STOPWORD = "STOP"


async def reader(channel: redis.client.PubSub):
    while True:
        message = await channel.get_message(ignore_subscribe_messages=True)
        if message is not None:
            print(f"(Reader) Message Received: {message}")
            if message["data"].decode() == STOPWORD:
                print("(Reader) STOP")
                break


async def main():
    r = await redis.from_url("redis://localhost")
    async with r.pubsub() as pubsub:
        await pubsub.psubscribe("channel:*")

        future = asyncio.create_task(reader(pubsub))

        await r.publish("channel:1", "Hello")
        await r.publish("channel:2", "World")
        await r.publish("channel:1", STOPWORD)

        await future


if __name__ == "__main__":
    asyncio.run(main())
