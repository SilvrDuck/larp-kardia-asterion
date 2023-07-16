import asyncio
import random
from typing import Callable, List
import orjson

from redis.asyncio import StrictRedis
from serenity.common.definitions import Owner, Topic, RedisSignal, ShipModel

from serenity.common.persistable import Persistable
from serenity.sonar.actors import Mine, Ship, Torpedo
from serenity.sonar.logic import Direction, GridPosition, Map

from serenity.common.config import settings


class SonarService(Persistable):
    def __init__(self):
        self._map = None
        self._player_ship = Ship(
            name=settings.serenity_name,
            hp=settings.serenity_hp,
            owner=Owner.PLAYER,
        )
        self._asteroid_positions = self._get_asteroid_positions(
            settings.sonar_map_file_name
        )

    async def start_battle(self, npc_ship: ShipModel) -> None:
        async with self.redis.get_lock(__file__):
            npc_ship = Ship(
                name=npc_ship.name,
                hp=npc_ship.hp,
                owner=Owner.NPC,
            )

            asteroids = self._asteroid_positions

            starting_position = self._select_position(asteroids)
            other_position = self._select_position(asteroids + [starting_position])

            self._map = Map(
                width=settings.sonar_map_width,
                height=settings.sonar_map_height,
                player_ship=self._player_ship,
                npc_ship=npc_ship,
                player_ship_position=starting_position,
                npc_ship_position=other_position,
                asteroid_positions=asteroids,
            )

    async def _resolve_action(self, map_function: Callable[[Map], None]) -> None:
        async with self.redis.get_lock(__file__):
            if self._map is None:
                return

            map_function(self._map)

            await self.redis.publish(self._battle_state(), Topic.DASHBOARDS)

    async def move_ship(self, owner: Owner, direction: Direction) -> None:
        await self._resolve_action(lambda map: map.move_ship(owner, direction))

    async def launch_torpedo(self, owner: Owner, target: GridPosition) -> None:
        torpedo = Torpedo(
            owner=owner,
            damage=settings.sonar_torpedo_damage,
            reach=settings.sonar_torpedo_reach,
            radius=settings.sonar_torpedo_radius,
        )
        await self._resolve_action(lambda map: map.launch_torpedo(torpedo, target))

    async def place_mine(self, owner: Owner, target: GridPosition) -> None:
        mine = Mine(
            owner=owner,
            damage=settings.sonar_mine_damage,
            reach=settings.sonar_mine_reach,
            radius=settings.sonar_mine_radius,
        )
        await self._resolve_action(lambda map: map.place_mine(mine, target))

    def _battle_state(self) -> dict:
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

    def _get_asteroid_positions(self, map_file_name: str) -> List[GridPosition]:
        with open(settings.asteroid_map_dir / map_file_name) as file:
            map_data = orjson.loads(file.read())

        return [
            GridPosition(x=asteroid["x"], y=asteroid["y"])
            for asteroid in map_data["asteroids"]
        ]

    async def end_battle(self) -> None:
        async with self.redis.get_lock(__file__):
            self._map = None
            await self.redis.publish(RedisSignal.STOP_BATTLE, Topic.BATTLE)

    def from_dict(self, d: dict):
        raise NotImplementedError()

    def to_dict(self) -> dict:
        raise NotImplementedError()
