import asyncio
import logging

import orjson
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from serenity.common.definitions import Topic
from serenity.common.redis_client import RedisClient


class WebsocketsManager:
    def __init__(self, topic: Topic) -> None:
        self._active_connections: set[WebSocket] = set()
        self._redis = RedisClient()
        self._topic = topic

    async def subscribe_to_broadcast(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._active_connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        try:
            await websocket.close(code=1001)
            self._active_connections.remove(websocket)
        except RuntimeError:
            logging.warning(f"Websocket {websocket} already closed.")
        except KeyError:
            logging.warning(f"Websocket {websocket} not found in active connections.")

    async def disconnect_all(self) -> None:
        await asyncio.gather(*[self.disconnect(connection) for connection in self._active_connections])

    async def broadcast(self, message: str):
        for connection in self._active_connections:
            try:
                await connection.send_json(message)
            except RuntimeError:
                logging.warning(f"Trying to broadcast to {connection} already closed.")
                self._active_connections.remove(connection)

    async def broadcast_loop(self):
        subscription = self._redis.subscribtion_iterator(self._topic)

        async for message in subscription:
            logging.debug(f"Broadcasting message: {message}")
            await self.broadcast(message)

    async def publish_socket_messages(self, websocket: WebSocket):
        try:
            while True:
                await self._receive_and_publish(websocket)
        except WebSocketDisconnect:
            self.disconnect(websocket)

    async def _receive_and_publish(self, websocket):
        message = await websocket.receive_text()
        message = orjson.loads(message)

        try:
            target_channel = Topic(message["channel"])
            logging.debug(f"Publishing message: {message} to channel: {target_channel}")
            await self._redis.publish(message, target_channel)
        except (KeyError, ValueError) as err:
            logging.error(f"Invalid message received: {message}, reason: {err}.")
