import asyncio

import random
from datetime import datetime, timedelta

from typing import Self


from serenity.common.config import settings
from serenity.common.definitions import (
    MessageType,
    Topic,
)

from serenity.common.redis_client import RedisMessage
from serenity.common.service import Service
from serenity.travel.definitions import ShipState, TravelConfig, TravelState
from serenity.travel.exceptions import CannotTakeOffException
from serenity.travel.planet_graph import PlanetGraph


class TravelService(Service[TravelState, TravelConfig]):
    state = TravelState
    config = TravelConfig

    _ship_state: ShipState
    _planet_graph: PlanetGraph
    _step_start: datetime
    _pause_start: datetime
    _current_step_id: str | tuple[str, str]
    _travel_tick_seconds: float

    @classmethod
    def default_service(cls) -> Self:
        planetary_config = PlanetGraph.default_planetary_config()
        planet_graph = PlanetGraph(planetary_config)
        state = TravelState(
            ship_state=ShipState.Paused,
            planetary_config=planetary_config,
            step_start=datetime.utcnow(),
            pause_start=datetime.utcnow(),
            step_duration_minutes=0.0,
            current_step_id=planet_graph.starting_planet(),
        )
        config = TravelConfig(travel_tick_seconds=settings.travel_tick_seconds)
        return cls(state, config)

    def _update_state(self, state: TravelState) -> None:
        self._ship_state = state.ship_state
        self._planet_graph = PlanetGraph(state.planetary_config)
        self._step_start = state.step_start
        self._pause_start = state.pause_start
        self._current_step_id = state.current_step_id

        self._set_visited(self._current_step_id)

    def _to_state(self) -> TravelState:
        return TravelState(
            ship_state=self._ship_state,
            planetary_config=self._planet_graph.to_planetary_config(),
            step_start=self._step_start,
            pause_start=self._pause_start,
            step_duration_minutes=self._step_elapsed_minutes(),
            current_step_id=self._current_step_id,
        )

    def _update_config(self, config: TravelConfig) -> None:
        self._travel_tick_seconds = config.travel_tick_seconds

    def _to_config(self) -> TravelConfig:
        return TravelConfig(travel_tick_seconds=self._travel_tick_seconds)

    async def _start(self) -> None:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._command_subscription())
            tg.create_task(self._run_tick_loop())

    async def _command_subscription(self) -> None:
        subscription = self.redis.subscribtion_iterator(Topic.COMMAND)
        async for message in subscription:
            match message:
                case RedisMessage(type=MessageType.TAKEOFF, data=target_id):
                    await self.takeoff(target_id)

    async def takeoff(self, target_id: str) -> None:
        if self._ship_state != ShipState.Landed:
            raise CannotTakeOffException("Cannot take off when not landed, maybe paused?")
        if self._step_elapsed_minutes() < self._step_min_minutes():
            raise CannotTakeOffException("Cannot take off before minimum stop time")

        reachable_planets = self._planet_graph.reachable_planets(self._current_step_id)
        if target_id not in reachable_planets:
            raise CannotTakeOffException(
                f"Target {target_id} is not reachable from {self._current_step_id}. "
                f"Reachable planets: {reachable_planets}."
            )

        async with self.get_self_lock():
            await self._takeoff(target_id)

    def _set_state(self, state: ShipState) -> None:
        self._ship_state = state

    async def _run_tick_loop(self) -> None:
        while True:
            async with self.get_self_lock():
                await self._tick()
            await asyncio.sleep(self._travel_tick_seconds)

    async def pause(self) -> None:
        if self._ship_state == ShipState.Paused:
            return
        async with self.get_self_lock():
            self._set_state(ShipState.Paused)
            self._pause_start = datetime.utcnow()
            await self._broadcast_state()

    async def resume(self) -> None:
        if self._ship_state != ShipState.Paused:
            return
        async with self.get_self_lock():
            # Create a fake start time assuming pause didn't happen
            self._step_start = datetime.utcnow() - self._pause_duration()
            self._set_state(self._infer_state_from_current_step_id())
            await self._broadcast_state()

    async def _tick(self) -> None:
        match self._ship_state:
            case ShipState.Paused:
                pass
            case ShipState.Landed:
                await self._update_landed()
            case ShipState.Traveling:
                await self._update_travel()

    def _infer_state_from_current_step_id(self) -> ShipState:
        if isinstance(self._current_step_id, str):
            return ShipState.Landed
        elif isinstance(self._current_step_id, tuple):
            return ShipState.Traveling
        else:
            raise ValueError(f"Invalid current step id {self._current_step_id}")

    def _step_elapsed_minutes(self) -> float:
        time_from_start = datetime.utcnow() - self._step_start
        pause_duration = self._pause_duration()
        return (time_from_start - pause_duration).total_seconds() / 60.0

    def _pause_duration(self) -> timedelta:
        if self._ship_state != ShipState.Paused:
            return timedelta()
        return datetime.utcnow() - self._pause_start

    async def _update_landed(self) -> None:
        if self._step_elapsed_minutes() >= self._step_max_minutes():
            target = self._get_random_destination()
            await self._takeoff(target)

    def _get_random_destination(self) -> str:
        assert isinstance(self._current_step_id, str), "current step should be a str"
        return random.choice(list(self._planet_graph.reachable_planets(self._current_step_id)))

    async def _update_travel(self) -> None:
        if self._step_elapsed_minutes() >= self._step_max_minutes():
            await self._land()

    async def _land(self) -> None:
        self._set_state(ShipState.Landed)
        self._step_start = datetime.utcnow()
        self._current_step_id = self._current_step_id[1]  # target of edge
        self._set_visited(self._current_step_id)

        await self._broadcast_state()

    def _set_visited(self, node_id: str) -> None:
        self._planet_graph.nodes[node_id]["visited"] = True

    async def _takeoff(self, target_planet_id: str) -> None:
        self._set_state(ShipState.Traveling)
        self._step_start = datetime.utcnow()
        assert isinstance(self._current_step_id, str), "current step should be a single element during take off"
        self._current_step_id = (self._current_step_id, target_planet_id)

        await self._broadcast_state()

    def _step_min_minutes(self) -> float:
        if self._ship_state != ShipState.Landed:
            raise ValueError(f"Invalid state to get min minutes {self._ship_state}")
        return self._planet_graph.nodes[self._current_step_id]["min_step_minutes"]

    def _is_in_space(self) -> bool:
        return self._infer_state_from_current_step_id() == ShipState.Traveling

    def _step_max_minutes(self) -> float:
        if self._is_in_space():
            graph_element = self._planet_graph.get_edge_data(*self._current_step_id)
            if graph_element is None:
                raise ValueError(f"Invalid edge {self._current_step_id}")
        else:
            graph_element = self._planet_graph.nodes[self._current_step_id]

        return graph_element["max_step_minutes"]

    def _current_step_completion(self) -> float:
        return self._step_elapsed_minutes() / self._step_max_minutes()
