from typing import Dict, Optional, Type
import asyncio
from datetime import datetime
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
import orjson
from pydantic import Json
from pydantic.utils import deep_update
from serenity.api.websockets_manager import WebsocketsManager
from serenity.common.config import settings
from serenity.common.definitions import Jsonable, MessageType, Owner, ServiceType, StatusBaseModel, Topic
from serenity.common.redis_client import RedisClient, RedisMessage
from serenity.common.service import Service
from serenity.light.light_service import LightService
from serenity.sonar.sonar_service import SonarService
from serenity.sound.sound_service import SoundService
from serenity.switch.switch_service import SwitchService
from serenity.travel.definitions import ShipState, TravelState
from serenity.travel.nx_to_flow_adapter import NxToFlowAdapter
from serenity.sonar.definitions import Battle, Ship
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

services_dict: Dict[Topic, Type[Service]] = {
    ServiceType.TRAVEL: TravelService,
    ServiceType.SONAR: SonarService,
    ServiceType.SWITCH: SwitchService,
    ServiceType.LIGHT: LightService,
    ServiceType.SOUND: SoundService,
}
services: Dict[Topic, Service] = {}


async def init_services(service: Service) -> None:
    if settings.restore_persisted_state:
        for key, service in services_dict.items():
            services[key] = await service.restore()
    else:
        for key, service in services_dict.items():
            services[key] = service.default_service()


@app.on_event("startup")
async def startup_event() -> None:
    await redis.release_all_locks()

    await init_services(services)

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

    await services[ServiceType.TRAVEL].broadcast_status()
    await services[ServiceType.SONAR].broadcast_status()

    await websockets_manager.forward_socket_messages(websocket)


# @app.websocket("/sound")
# async def sound(websocket: WebSocket) -> None:
#     await websockets_manager.subscribe_to_broadcast(websocket, {Topic.SOUND})


@app.get("/state/{service_type}")
async def get_state(service_type: ServiceType) -> Jsonable:
    async with services[service_type].get_self_lock():
        return services[service_type].to_state().model_dump(mode="json")


@app.post("/state/{service_type}")
async def set_state(service_type: ServiceType, state: Jsonable) -> None:
    service = services[service_type]
    curr_state = service.to_state().model_dump(mode="json")
    new_state = service.state_type(**deep_update(curr_state, state))
    await service.update_state(new_state)


@app.get("/config/{service_type}")
async def get_config(service_type: ServiceType) -> Jsonable:
    async with services[service_type].get_self_lock():
        return services[service_type].to_config().model_dump()


@app.post("/config/{service_type}")
async def set_config(service_type: ServiceType, config: Jsonable) -> None:
    service = services[service_type]
    curr_config = service.to_config().model_dump()
    new_config = service.config_type(**deep_update(curr_config, config))
    service.update_config(new_config)


@app.post("/start_battle")
async def start_battle(battle: Battle) -> None:
    await redis.publish(
        RedisMessage(
            topic=Topic.COMMAND,
            type=MessageType.START_BATTLE,
            data=battle,
        )
    )


@app.post("/command/{command}")
async def command(command: MessageType, data: Optional[dict] = None) -> None:
    await redis.publish(
        RedisMessage(
            topic=Topic.COMMAND,
            type=command,
            data=data,
        )
    )


@app.get("/repair/{owner}/{hp}")
async def repair(owner: Owner, hp: int) -> None:
    await redis.publish(
        RedisMessage(
            topic=Topic.COMMAND,
            type=MessageType.REPAIR,
            data={
                "owner": owner,
                "hp": hp,
            },
        )
    )


@app.get("/pause_travel")
async def pause_travel() -> None:
    await services[ServiceType.TRAVEL].pause()


@app.get("/resume_travel")
async def resume_travel() -> None:
    await services[ServiceType.TRAVEL].resume()


@app.get("/broadcast_all")
async def broadcast_all() -> None:
    for service in services.values():
        await service.broadcast_status()
