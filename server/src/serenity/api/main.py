from typing import Dict
import asyncio
from datetime import datetime
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
import orjson

from serenity.api.websockets_manager import WebsocketsManager
from serenity.common.config import settings
from serenity.common.definitions import MessageType, ServiceType, Topic
from serenity.common.redis_client import RedisClient, RedisMessage
from serenity.common.service import Service
from serenity.sonar.sonar_service import SonarService
from serenity.switch.switch_service import SwitchService
from serenity.travel.definitions import ShipState, TravelState
from serenity.travel.nx_to_flow_adapter import NxToFlowAdapter
from serenity.sonar.definitions import Ship
from serenity.travel.planet_graph import PlanetGraph
from serenity.travel.travel_service import TravelService

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
)

websockets_manager = WebsocketsManager()
redis = RedisClient()

services_dict: Dict[Topic, Service] = {
    ServiceType.TRAVEL: TravelService,
    ServiceType.SONAR: SonarService,
    ServiceType.SWITCH: SwitchService,
}

if settings.restore_persisted_state:
    services = {key: service.restore() for key, service in services_dict.items()}
else:
    services = {key: service.default_service() for key, service in services_dict.items()}


@app.on_event("startup")
async def startup_event() -> None:
    await redis.release_all_locks()
    for service in services.values():
        asyncio.create_task(service.start())

    for topic in Topic:
        if topic != Topic.BROADCAST_STATUS:
            continue
        asyncio.create_task(websockets_manager.broadcast_loop(topic))


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await websockets_manager.disconnect_all()
    await redis.release_all_locks()
    await redis.terminate_all_channels()


@app.websocket("/dashboard")
async def dashboard(websocket: WebSocket) -> None:
    await websockets_manager.subscribe_to_broadcast(websocket, {Topic.BROADCAST_STATUS})
    await websockets_manager.add_adapter(websocket, Topic.BROADCAST_STATUS, NxToFlowAdapter)

    print("TOREMOVE TOREMOVE TEROMEVE")
    await services[ServiceType.TRAVEL].resume()
    print("TOREMOVE TOREMOVE TEROMEVE")

    await services[ServiceType.TRAVEL].broadcast_status()
    await services[ServiceType.SONAR].broadcast_status()

    await websockets_manager.forward_socket_messages(websocket)


@app.get("/game_state")
async def game_state() -> dict:
    return services[ServiceType.TRAVEL].to_dict()


@app.get("/resume")
async def resume() -> None:
    await services[ServiceType.TRAVEL].resume()


@app.get("/take_off/{target_id}")
async def take_off(target_id: str) -> None:
    await services[ServiceType.TRAVEL].takeoff(target_id)


@app.get("/start_battle")
async def start_battle() -> None:
    await redis.publish(
        RedisMessage(
            topic=Topic.COMMAND,
            type=MessageType.START_BATTLE,
            data={"map": "alpha", "ship": Ship(name="Yow", hp=3, owner="npcs")},
        )
    )

@app.get("/broadcast")
async def broadcast() -> None:
    await services[ServiceType.TRAVEL]._broadcast_state()
    await services[ServiceType.SONAR]._broadcast_state()
