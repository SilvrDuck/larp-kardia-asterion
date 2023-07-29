from ast import List, Tuple
import json
from typing import Dict, Set, Callable
import asyncio
import logging

from collections import defaultdict
import orjson
from fastapi import WebSocket, WebSocketDisconnect
from serenity.common.adapter import Adapter

from serenity.common.definitions import Jsonable, MessageType, ServiceType, Topic
from serenity.common.redis_client import RedisClient, RedisMessage


class WebsocketsManager:
    def __init__(self) -> None:
        self._active_connections: Dict[Topic, Set[WebSocket]] = defaultdict(set)
        self._redis = RedisClient()
        self._adapters: Dict[Tuple[WebSocket, Topic], List[Adapter]] = defaultdict(list)

    async def subscribe_to_broadcast(self, websocket: WebSocket, topics: Set[Topic]) -> None:
        await websocket.accept()

        async with self._redis.get_lock(__name__):
            for topic in topics:
                self._active_connections[topic].add(websocket)

    async def _remove_websocket(self, websocket: WebSocket) -> None:
        for websockets in self._active_connections.values():
            if websocket in websockets:
                websockets.remove(websocket)

    async def _disconnect(self, websocket: WebSocket) -> None:
        try:
            await self._remove_websocket(websocket)
            await websocket.close(code=1001)
        except RuntimeError:
            logging.warning("Websocket %s already closed.", websocket)
        except KeyError:
            logging.warning("Websocket %s not found.", websocket)

    async def disconnect_all(self) -> None:
        async with self._redis.get_lock(__name__):
            all_websockets = set(
                [websocket for websockets in self._active_connections.values() for websocket in websockets]
            )
            await asyncio.gather(*[self._disconnect(connection) for connection in all_websockets])

    async def broadcast(self, message: RedisMessage):
        async with self._redis.get_lock(__name__):
            websockets = self._active_connections[message.topic]

            for connection in websockets:
                try:
                    message = self._adapt_if_needed(message, connection)
                    data = message.model_dump(mode="json")

                    logging.debug("WEBSOCK: Broadcast, %s, %s", message.topic, str(data)[:70])
                    await connection.send_json(data)
                except RuntimeError as err:
                    logging.warning("Trying to broadcast to %s, but connection is closed (%s).", connection, err)
                    await self._remove_websocket(connection)

    def _adapt_if_needed(self, message: RedisMessage, connection: WebSocket) -> RedisMessage:
        if (connection, message.topic) in self._adapters:
            adapters = self._adapters[(connection, message.topic)]
            for adapter in adapters:
                message = adapter.adapt_if_needed(message)

        return message

    async def broadcast_loop(self, topic: Topic):
        subscription = self._redis.subscribtion_iterator(topic)
        logging.debug("Starting broadcast loop for topic: %s", topic)

        async for message in subscription:
            await self.broadcast(message)

    async def forward_socket_messages(self, websocket: WebSocket):
        try:
            while True:
                await self._receive_and_publish(websocket)
        except WebSocketDisconnect:
            await self._disconnect(websocket)

    async def _receive_and_publish(self, websocket):
        message = await websocket.receive_text()
        message = orjson.loads(message)  # pylint: disable=maybe-no-member

        try:
            redis_message = RedisMessage(
                topic=Topic(message["topic"]),
                type=MessageType(message["type"]),
                concerns=ServiceType(message["concerns"]),
                data=message["data"],
            )
            logging.debug("WEBSOCK: Reveive publish, %s", str(message)[:70])
            await self._redis.publish(redis_message)
        except (KeyError, ValueError) as err:
            logging.error("Invalid message received: %s, %s", message, err)

    async def add_adapter(self, websocket: WebSocket, topic: Topic, adapter: Adapter) -> None:
        async with self._redis.get_lock(__name__):
            self._adapters[(websocket, topic)].append(adapter)
