import asyncio
import logging

from fastapi import FastAPI

from serenity.common.config import settings
from serenity.common.definitions import GameState
from serenity.common.io import RedisClient
from serenity.travel.travel_service import TravelService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
RedisClient().release_all_locks()

if settings.restore_persisted_state:
    travel_service = TravelService.restore()
else:
    travel_service = TravelService()


@app.on_event("startup")
async def startup_event() -> None:
    asyncio.create_task(travel_service.run())


@app.get("/game_state")
async def game_state() -> dict:
    return travel_service._game_state()


@app.get("/resume")
async def resume() -> None:
    await travel_service.resume()


@app.get("/take_off/{target_id}")
async def take_off(target_id: str) -> None:
    await travel_service.take_off(target_id)
