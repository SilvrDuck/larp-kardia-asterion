import asyncio
from logging import Logger
import logging
import random
from datetime import datetime, timedelta
from enum import Enum
from typing import Tuple

import orjson
import pydantic

from serenity.common.config import settings
from serenity.common.definitions import GameState, RedisChannel, RedisSignal, ShipModel
from serenity.common.persistable import Persistable
from serenity.travel.exceptions import CannotTakeOffException
from serenity.travel.nx_to_flow_converter import NxToFlowGraphConverter
from serenity.travel.planet_graph import PlanetaryConfig, PlanetGraph


class State(Enum):
    Paused = "paused"
    Landed = "landed"
    Travelling = "travelling"


class TravelService(Persistable):
    def __init__(self) -> None:
        self._state = State.Paused
        self._planet_graph = self._load_planet_graph()
        self._step_start = datetime.utcnow()
        self._pause_start = datetime.utcnow()
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
        if self._step_elapsed_minutes() < self._step_min_minutes():
            raise CannotTakeOffException("Cannot take off before minimum stop time")

        reachable_planets = self._planet_graph.reachable_planets(self._current_step_id)
        if target_id not in reachable_planets:
            raise CannotTakeOffException(
                f"Target {target_id} is not reachable from {self._current_step_id}. "
                f"Reachable planets: {reachable_planets}."
            )

        async with self.redis.get_lock(__file__):
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
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._run_tick_loop())
            tg.create_task(self._run_battle_status_loop())

    async def _run_tick_loop(self) -> None:
        while True:
            async with self.redis.get_lock(__file__):
                await self._tick()
            await asyncio.sleep(settings.travel_tick_seconds)

    async def _run_battle_status_loop(self) -> None:
        subscription = self.redis.subscribtion_iterator(RedisChannel.BATTLE)

        async for message in subscription:
            if message == RedisSignal.BATTLE_STOPPED.value:
                await self.resume()
            else:
                try:
                    ShipModel.model_validate(message)
                    await self.pause()
                except pydantic.ValidationError:
                    logging.exception("Message couldn't be parsed as a Ship object: %s", message)

    async def pause(self) -> None:
        if self._state == State.Paused:
            return
        async with self.redis.get_lock(__file__):
            self._set_state(State.Paused)
            self._pause_start = datetime.utcnow()
            await self._emit_new_state()

    async def resume(self) -> None:
        if self._state != State.Paused:
            return
        async with self.redis.get_lock(__file__):
            # Create a fake start time assuming pause didn't happen
            self._step_start = datetime.utcnow() - self._pause_duration()
            self._set_state(self._infer_state_from_current_step_id())
            await self._emit_new_state()

    async def _tick(self) -> None:
        match self._state:
            case State.Paused:
                pass
            case State.Landed:
                await self._update_landed()
            case State.Travelling:
                await self._update_travel()

    def _infer_state_from_current_step_id(self) -> State:
        if isinstance(self._current_step_id, str):
            return State.Landed
        elif isinstance(self._current_step_id, tuple):
            return State.Travelling
        else:
            raise ValueError(f"Invalid current step id {self._current_step_id}")

    def _step_elapsed_minutes(self) -> float:
        time_from_start = datetime.utcnow() - self._step_start
        pause_duration = self._pause_duration()
        return (time_from_start - pause_duration).total_seconds() / 60.0

    def _pause_duration(self) -> timedelta:
        if self._state != State.Paused:
            return timedelta()
        return datetime.utcnow() - self._pause_start

    async def _update_landed(self) -> None:
        if self._step_elapsed_minutes() >= self._step_max_minutes():
            target = self._get_random_destination()
            await self._take_off(target)

    def _get_random_destination(self) -> str:
        assert isinstance(self._current_step_id, str), "current step should be a str"
        return random.choice(list(self._planet_graph.reachable_planets(self._current_step_id)))

    async def _update_travel(self) -> None:
        if self._step_elapsed_minutes() >= self._step_max_minutes():
            await self._land()

    async def _land(self) -> None:
        self._set_state(State.Landed)
        self._step_start = datetime.utcnow()
        self._current_step_id = self._current_step_id[1]  # target of edge
        self._set_visited(self._current_step_id)

        await self._emit_new_state()

    def _set_visited(self, node_id: str) -> None:
        self._planet_graph.nodes[node_id]["visited"] = True

    async def _take_off(self, target_planet_id: str) -> None:
        self._set_state(State.Travelling)
        self._step_start = datetime.utcnow()
        assert isinstance(self._current_step_id, str), "current step should be a single element during take off"
        self._current_step_id = (self._current_step_id, target_planet_id)

        await self._emit_new_state()

    def _step_min_minutes(self) -> float:
        if self._state != State.Landed:
            raise ValueError(f"Invalid state to get min minutes {self._state}")
        return self._planet_graph.nodes[self._current_step_id]["min_step_minutes"]

    def _is_in_space(self) -> bool:
        return self._infer_state_from_current_step_id() == State.Travelling

    def _step_max_minutes(self) -> float:
        if self._is_in_space():
            graph_element = self._planet_graph.get_edge_data(*self._current_step_id)
            if graph_element is None:
                raise ValueError(f"Invalid edge {self._current_step_id}")
        else:
            graph_element = self._planet_graph.nodes[self._current_step_id]

        return graph_element["max_step_minutes"]

    def _game_state(self) -> GameState:
        return GameState(
            current_step_id=self._current_step_id,
            is_in_battle=False,
            step_completion=self._current_step_completion(),
            react_flow_graph=self._current_graph_flow_state(),
        )

    async def emit_game_state(self) -> GameState:
        async with self.redis.get_lock(__file__):
            await self._emit_new_state()

    async def _emit_new_state(self) -> None:
        await self.redis.publish(self._game_state(), RedisChannel.DASHBOARDS)

    def _current_step_completion(self) -> float:
        return self._step_elapsed_minutes() / self._step_max_minutes()

    def to_dict(self) -> dict:
        return {
            "state": self._state,
            "planet_graph": self._planet_graph.to_dict(),
            "step_start": self._step_start,
            "current_step_id": self._current_step_id,
            "step_elapsed_minutes": self._step_elapsed_minutes(),
        }

    def _prepare_from_dict(self, data: dict) -> dict:
        datetime.fromisoformat(data["step_start"]),
        new_start = datetime.utcnow() - timedelta(minutes=data["step_elapsed_minutes"])
        return {
            "state": State(data["state"]),
            "planet_graph": PlanetGraph.from_dict(data["planet_graph"]),
            "step_start": new_start,
            "current_step_id": data["current_step_id"],
        }

    def _current_graph_flow_state(self) -> dict:
        return NxToFlowGraphConverter(self._planet_graph).node_link_to_flow(self._current_step_id)
