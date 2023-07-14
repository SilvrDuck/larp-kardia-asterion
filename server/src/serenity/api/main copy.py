# noqa
# mypy: ignore-errors
import asyncio
import logging

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocket, WebSocketDisconnect
from redis.asyncio import StrictRedis

from serenity.sonar.sonar_service import SonarService
from serenity.travel.travel_service import TravelService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
travel_service = TravelService()


@app.on_event("startup")
async def startup_event():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(sonar.start())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await redis_connector(websocket)


async def consumer_handler(ws: WebSocket, redis):
    try:
        while True:
            message = await ws.receive_text()
            print("cons", message)
            if message is not None:
                await redis.publish("chat:c", message)
    except WebSocketDisconnect as exc:
        # TODO this needs handling better
        logger.error(exc)


async def producer_handler(pubsub, ws: WebSocket):
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message is not None:
                await ws.send_text(message["data"].decode())
    except Exception as exc:
        # TODO this needs handling better
        logger.error(exc)


async def redis_connector(websocket: WebSocket, redis_uri: str = "redis://localhost:6379"):
    redis = await StrictRedis.from_url(redis_uri)

    async with redis.pubsub() as pubsub:
        await pubsub.subscribe("chat:c")

        consumer_task = asyncio.create_task(consumer_handler(websocket, redis))
        producer_task = asyncio.create_task(producer_handler(pubsub, websocket))
        run_sonar = asyncio.create_task(sonar.run())

        done, pending = await asyncio.wait(
            [consumer_task, producer_task, run_sonar],
            return_when=asyncio.FIRST_COMPLETED,
        )
        logger.debug(f"Done task: {done}")
        for task in pending:
            logger.debug(f"Canceling task: {task}")
            task.cancel()
