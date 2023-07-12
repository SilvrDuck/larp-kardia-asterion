from typing import Tuple
from serenity.common.config import settings
from serenity.common.definitions import RedisChannel
from serenity.common.io import RedisClient
from serenity.common.persistable import Persistable
import asyncio
from enum import Enum, auto
import orjson
from serenity.travel.exceptions import CannotTakeOffException
from serenity.travel.planet_graph import PlanetGraph, PlanetaryConfig
from datetime import datetime, timedelta
import random


class State(Enum):
    Paused = auto()
    Landed = auto()
    Travelling = auto()


class TravelService(Persistable):
    def __init__(self):
        self._redis = RedisClient()

        self._state = State.Paused
        self._planet_graph = self._load_planet_graph()
        self._step_start = datetime.now()
        self._current_step_id: str | Tuple[str, str] = self._get_starting_planet()

    def _get_starting_planet(self) -> str | Tuple[str, str]:
        in_degrees = self._planet_graph.in_degree()

        candidates = []
        for node_id, in_degree in in_degrees:
            if in_degree == 0:
                candidates.append(node_id)

        if len(candidates) != 1:
            raise ValueError("Planet graph must have exactly one starting planet")

        return candidates[0]

    async def take_off(self, target_id: str) -> None:
        if self._state != State.Landed:
            raise CannotTakeOffException("Cannot take off when not landed")
        if self._step_duration_minutes() < self._current_min_stop_minutes():
            raise CannotTakeOffException("Cannot take off before minimum stop time")
        await self._take_off(target_id)

    @staticmethod
    def _load_planet_graph() -> PlanetGraph:
        with open(settings.planetary_config_path, "rb") as file:
            planetary_config = orjson.loads(file.read())
        planetary_config = PlanetaryConfig(**planetary_config)
        return PlanetGraph(planetary_config)

    @property
    def state(self) -> State:
        return self._state

    def _set_state(self, state: State) -> None:
        self._state = state

    async def run(self) -> None:
        while True:
            await self.tick()
            await asyncio.sleep(settings.travel_tick_seconds)

    async def tick(self) -> None:
        match self._state:
            case State.Paused:
                pass
            case State.Landed:
                await self._update_landed()
            case State.Travelling:
                await self._update_travel()

    def _step_duration_minutes(self) -> float:
        return (datetime.now() - self._step_start).total_seconds() / 60.0

    async def _update_landed(self) -> None:
        if self._step_duration_minutes() >= self._current_max_stop_minutes():
            target = self._get_random_destination()
            await self._take_off(target)

    def _get_random_destination(self) -> str:
        out_edges = list(self._planet_graph.out_edges(self._current_step_id))
        return random.choice(out_edges)[1]

    async def _update_travel(self) -> None:
        if self._step_duration_minutes() >= self._current_travel_minutes():
            await self._land()

    async def _land(self) -> None:
        self._set_state(State.Landed)
        self._time_at_place = 0.0
        self._current_step_id = self._current_step_id[1]  # target of edge
        await self._emit_new_state()

    async def _take_off(self, target_planet_id: str) -> None:
        self._set_state(State.Travelling)
        self._travel_timer = 0.0
        self._current_step_id = (self._current_step_id[0], target_planet_id)
        await self._emit_new_state()

    def _current_travel_minutes(self) -> float:
        return self._planet_graph.edges[self._current_step_id]["travel_minutes"]

    def _current_min_stop_minutes(self) -> float:
        return self._planet_graph.nodes[self._current_step_id]["min_stop_minutes"]

    def _current_max_stop_minutes(self) -> float:
        return self._planet_graph.nodes[self._current_step_id]["max_stop_minutes"]

    def to_game_state(self) -> dict:
        raise NotImplementedError()

    async def _emit_new_state(self) -> None:
        await self._redis.pusblish(RedisChannel.Travel, self.to_game_state())

    def to_dict(self) -> dict:
        raise NotImplementedError()

    def _prepare_from_dict(self, d: dict):
        raise NotImplementedError()
