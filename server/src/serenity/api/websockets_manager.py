from ast import Tuple
from typing import Dict, Set, Callable
import asyncio
import logging

from collections import defaultdict
import orjson
from fastapi import WebSocket, WebSocketDisconnect


from serenity.common.definitions import MessageType, ServiceType, Topic
from serenity.common.redis_client import RedisClient, RedisMessage


class WebsocketsManager:
    def __init__(self) -> None:
        self._active_connections: Dict[Topic, Set[WebSocket]] = defaultdict(set)
        self._redis = RedisClient()

    async def subscribe_to_broadcast(self, websocket: WebSocket, topics: Set[Topic]) -> None:
        await websocket.accept()

        async with self._redis.get_lock(__name__):
            for topic in topics:
                self._active_connections[topic].add(websocket)

    async def _remove_websocket(self, websocket: WebSocket) -> None:
        async with self._redis.get_lock(__name__):
            for websockets in self._active_connections.values():
                if websocket in websockets:
                    websockets.remove(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        try:
            await websocket.close(code=1001)
            await self._remove_websocket(websocket)
        except RuntimeError:
            logging.warning("Websocket %s already closed.", websocket)
        except KeyError:
            logging.warning("Websocket %s not found.", websocket)

    async def disconnect_all(self) -> None:
        async with self._redis.get_lock(__name__):
            all_websockets = set(
                [websocket for websockets in self._active_connections.values() for websocket in websockets]
            )
        await asyncio.gather(*[self.disconnect(connection) for connection in all_websockets])

    async def broadcast(self, message: RedisMessage, topic: Topic):
        async with self._redis.get_lock(__name__):
            websockets = self._active_connections[topic]

            for connection in websockets:
                try:
                    logging.debug("WEBSOCK: Broadcast, %s, %s", topic, str(message)[:70])
                    message = message.model_dump(mode="json")
                    await connection.send_json(message)
                except RuntimeError as err:
                    logging.warning("Trying to broadcast to %s, but connection is closed (%s).", connection, err)
                    await self._remove_websocket(connection)

    async def broadcast_loop(self, topic: Topic):
        subscription = self._redis.subscribtion_iterator(topic)
        logging.debug("Starting broadcast loop for topic: %s", topic)

        async for message in subscription:
            await self.broadcast(message, topic)

    async def forward_socket_messages(self, websocket: WebSocket):
        try:
            while True:
                await self._receive_and_publish(websocket)
        except WebSocketDisconnect:
            await self.disconnect(websocket)

    async def _receive_and_publish(self, websocket):
        message = await websocket.receive_text()
        message = orjson.loads(message)  # pylint: disable=maybe-no-member

        try:
            topic = Topic(message["topic"])
            logging.debug("WEBSOCK: Reveive publish, %s, %s", topic, str(message)[:70])
            redis_message = RedisMessage(
                type=MessageType(message["type"]), concerns=ServiceType(message["concerns"]), data=message["data"]
            )
            await self._redis.publish(redis_message, topic)
        except (KeyError, ValueError) as err:
            logging.error("Invalid message received: %s, %s", message, err)
