import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket

from serenity.api.websockets_manager import WebsocketsManager
from serenity.common.config import settings
from serenity.common.definitions import MessageType, PlanetaryConfig, Topic, ShipModel
from serenity.common.redis_client import RedisClient, RedisMessage
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

if settings.restore_persisted_state:
    travel_service = TravelService.restore()
else:
    travel_service = TravelService.default_service()


@app.on_event("startup")
async def startup_event() -> None:
    await redis.release_all_locks()
    asyncio.create_task(travel_service.start())
    for topic in Topic:
        asyncio.create_task(websockets_manager.broadcast_loop(topic))


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await websockets_manager.disconnect_all()
    await redis.release_all_locks()
    await redis.terminate_all_channels()


def test_func(dico: RedisMessage) -> dict:
    if isinstance(dico, dict):
        print("ITSADICT")
        print(dico)
        return dico
    if dico.type != MessageType.STATE:
        return dico.model_dump()

    dico = dico.model_dump()
    print(dico)
    return {
        "current_step_id": dico["data"]["current_step_id"],
        "is_in_battle": False,
        "step_completion": dico["data"]["step_duration_minutes"],
        "react_flow_graph": PlanetGraph(PlanetaryConfig(**dico["data"]["planetary_config"])).to_dict(),
    }


@app.websocket("/dashboard")
async def dashboard(websocket: WebSocket) -> None:
    await websockets_manager.subscribe_to_broadcast(websocket, {Topic.BROADCAST_STATE})
    websockets_manager.register_callback_for_topic(websocket, Topic.BROADCAST_STATE, test_func)
    await websockets_manager.forward_socket_messages(websocket)


@app.get("/game_state")
async def game_state() -> dict:
    return travel_service.to_dict()


@app.get("/resume")
async def resume() -> None:
    await travel_service.resume()


@app.get("/take_off/{target_id}")
async def take_off(target_id: str) -> None:
    await travel_service.takeoff(target_id)


@app.post("/start_battle")
async def start_battle(attacking_ship: ShipModel) -> None:
    pass
    # await redis.publish(attacking_ship, Topic.BATTLE)
