import asyncio
import logging

import orjson
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from serenity.common.definitions import RedisChannel
from serenity.common.redis_client import RedisClient


class WebsocketsBroadcaster:
    def __init__(self, target_channel: RedisChannel):
        self._active_connections: set[WebSocket] = set()
        self._redis = RedisClient()
        self._target_channel = target_channel

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self._active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self._active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self._active_connections:
            print("sending message", message, "to", connection)
            print(self._active_connections)
            await connection.send_json(message)

    async def broadcast_loop(self):
        subscription = self._redis.subscribtion_iterator(self._target_channel)
        while True:
            message = await anext(subscription)
            await self.broadcast(message)

    async def receive_loop(self, websocket: WebSocket):
        try:
            while True:
                await self._receive_and_publish(websocket)
        except WebSocketDisconnect:
            self.disconnect(websocket)

    async def _receive_and_publish(self, websocket):
        message = await websocket.receive_text()
        message = orjson.loads(message)

        try:
            target_channel = RedisChannel(message["channel"])
            await self._redis.publish(target_channel, message)
        except (KeyError, ValueError) as err:
            logging.error(f"Invalid message received: {message}, reason: {err}.")
