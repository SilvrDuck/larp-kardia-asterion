import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket

from serenity.api.websockets import WebsocketsBroadcaster
from serenity.common.config import settings
from serenity.common.definitions import GameState, RedisChannel
from serenity.common.redis_client import RedisClient
from serenity.travel.travel_service import TravelService

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
)

dashboard_broadcaster = WebsocketsBroadcaster(RedisChannel.DASHBOARDS)

if settings.restore_persisted_state:
    travel_service = TravelService.restore()
else:
    travel_service = TravelService()


@app.websocket("/dashboard")
async def dashboard(websocket: WebSocket) -> None:
    await dashboard_broadcaster.connect(websocket)
    await travel_service.emit_game_state()
    await dashboard_broadcaster.receive_loop(websocket)


@app.on_event("startup")
async def startup_event() -> None:
    RedisClient().release_all_locks()
    asyncio.create_task(travel_service.run())
    asyncio.create_task(dashboard_broadcaster.broadcast_loop())


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await dashboard_broadcaster.disconnect_all()
    await RedisClient().terminate_all_channels()


@app.get("/game_state")
async def game_state() -> GameState:
    return travel_service._game_state()


@app.get("/resume")
async def resume() -> None:
    await travel_service.resume()


@app.get("/take_off/{target_id}")
async def take_off(target_id: str) -> None:
    await travel_service.take_off(target_id)
