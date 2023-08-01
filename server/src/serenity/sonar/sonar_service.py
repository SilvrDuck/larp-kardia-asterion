from __future__ import annotations


import asyncio
import logging
import random

from typing import Callable, List
import orjson


from redis.asyncio import StrictRedis
from serenity.common.definitions import MessageType, Owner, Topic


from serenity.common.redis_client import RedisMessage
from serenity.common.service import Service
from serenity.sonar.definitions import Asteroid, CellModel, Mine, Ship, Torpedo
from serenity.sonar.definitions import MapModel, SonarConfig, SonarState
from serenity.sonar.exceptions import ShipDestroyed
from serenity.sonar.logic import Direction, GridPosition, Map

from serenity.common.config import settings


class SonarService(Service[SonarState, SonarConfig]):
    state_type = SonarState
    config_type = SonarConfig

    @classmethod
    def default_service(cls) -> SonarService:
        default_state = SonarState(
            in_battle=False,
            map=None,
        )
        default_config = SonarConfig(
            torpedo_damage=settings.sonar_torpedo_damage,
            torpedo_reach=settings.sonar_torpedo_reach,
            torpedo_radius=settings.sonar_torpedo_radius,
            mine_damage=settings.sonar_mine_damage,
            mine_reach=settings.sonar_mine_reach,
            mine_radius=settings.sonar_mine_radius,
            player_default_hp=settings.sonar_player_default_hp,
        )
        return cls(default_state, default_config)

    def _update_state(self, state: SonarState) -> None:
        self._in_battle = state.in_battle
        if state.map is not None:
            self._map = Map(state.map)
        self._map = None

    def _to_state(self) -> SonarState:
        map_ = None
        if self._map is not None:
            map_ = self._map.to_model()
        return SonarState(
            in_battle=self._in_battle,
            map=map_,
        )

    def _update_config(self, config: SonarConfig) -> None:
        self._config = config

    def _to_config(self) -> SonarConfig:
        return self._config

    async def _start(self) -> None:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._command_subscription())

    async def _command_subscription(self) -> None:
        subscription = self.redis.subscription_iterator(Topic.COMMAND)
        async for message in subscription:
            try:
                if not self._in_battle:
                    match message:
                        case RedisMessage(type=MessageType.START_BATTLE, data=data):
                            await self.execute(self.start_battle, data["map"], Ship(**data["ship"]))
                        case _:
                            raise ValueError(f"Not in battle, cannot resolve: {message}.")
                else:
                    match message:
                        case RedisMessage(type=MessageType.END_BATTLE):
                            await self.execute(self.end_battle)
                        case RedisMessage(type=MessageType.MOVE, data=data):
                            await self.execute(self.move, Owner(data["owner"]), Direction(data["direction"]))
                        case RedisMessage(type=MessageType.LAUNCH_TORPEDO, data=data):
                            await self.execute(
                                self.launch_torpedo, Owner(data["owner"]), GridPosition(**data["target"])
                            )
                        case RedisMessage(type=MessageType.LAUNCH_MINE, data=data):
                            await self.execute(self.place_mine, Owner(data["owner"]), GridPosition(**data["target"]))
                        case RedisMessage(type=MessageType.REPAIR, data=data):
                            await self.execute(self.repair, Owner(**data))
                        case RedisMessage(type=MessageType.START_BATTLE):
                            raise ValueError("Can only start battle if not in battle.")
                        case _:
                            raise ValueError(f"Unknown message type: {message.type}.")
            except Exception as err:
                logging.error("SONAR: Error while processing command: %s\n%s", message, err)

    async def execute(self, action: Callable, *args, **kwargs) -> None:
        """Exectutes an action with lock and brodcasts the state afterwards."""
        async with self.redis.get_lock(__file__):
            try:
                await action(*args, **kwargs)
            except ShipDestroyed as err:
                logging.info("SONAR: Ship %s destroyed, ending battle.", err.ship.name)
                await self.end_battle()
            await self._broadcast_state()

    def _get_asteroid_positions(self, map_file_name: str) -> List[GridPosition]:
        with open(settings.asteroid_map_dir / f"{map_file_name}.json", encoding="utf-8") as file:
            map_data = orjson.loads(file.read())  # type: ignore

        return [GridPosition(x=asteroid["x"] - 1, y=asteroid["y"] - 1) for asteroid in map_data["asteroids"]]

    def _init_grid(self, asteroids: List[GridPosition]) -> List[List[CellModel]]:
        grid = [
            [
                CellModel(
                    content=[],
                    has_asteroid=False,
                )
                for _ in range(settings.sonar_map_width)
            ]
            for _ in range(settings.sonar_map_height)
        ]

        for asteroid in asteroids:
            grid[asteroid.y][asteroid.x] = CellModel(
                content=[Asteroid()],
                has_asteroid=True,
            )

        return grid

    def _prepare_battle(self, map_name: str, npc_ship: Ship) -> None:
        player_ship = Ship(
            name=settings.serenity_name,
            hp=self._config.player_default_hp,
            owner=Owner.PLAYERS,
        )
        asteroids = self._get_asteroid_positions(map_name)

        starting_position = self._select_position(asteroids)
        other_position = self._select_position(asteroids + [starting_position])

        grid = self._init_grid(asteroids)

        map_model = MapModel(
            width=settings.sonar_map_width,
            height=settings.sonar_map_height,
            grid=grid,
            player_ship=player_ship,
            npc_ship=npc_ship,
            ship_positions={
                Owner.PLAYERS: starting_position,
                Owner.NPCS: other_position,
            },
            mine_positions={},
        )

        return Map(map_model)

    async def start_battle(self, map_name: str, npc_ship: Ship) -> None:
        self._in_battle = True
        self._map = self._prepare_battle(map_name, npc_ship)

    async def move(self, owner: Owner, direction: Direction) -> None:
        self._map.move_ship(owner, direction)

    async def launch_torpedo(self, owner: Owner, target: GridPosition) -> None:
        torpedo = Torpedo(
            owner=owner,
            damage=self._config.torpedo_damage,
            reach=self._config.torpedo_reach,
            radius=self._config.torpedo_radius,
        )
        self._map.launch_torpedo(torpedo, target)

    async def place_mine(self, owner: Owner, target: GridPosition) -> None:
        mine = Mine(
            owner=owner,
            damage=settings.sonar_mine_damage,
            reach=settings.sonar_mine_reach,
            radius=settings.sonar_mine_radius,
        )
        self._map.place_mine(mine, target)

    async def repair(self, owner: Owner) -> None:
        raise NotImplementedError()

    def _select_position(self, unavailable: List[GridPosition]) -> GridPosition:
        """Choses a starting position at random within the map,
        avoiding asteroids and within a margin from the border.
        """

        margin = settings.sonar_spawn_margin

        while True:
            position = GridPosition(
                x=random.randint(margin, settings.sonar_map_width - margin),
                y=random.randint(margin, settings.sonar_map_height - margin),
            )
            if position not in unavailable:
                return position

    async def end_battle(self) -> None:
        self._map = None
        self._in_battle = False
