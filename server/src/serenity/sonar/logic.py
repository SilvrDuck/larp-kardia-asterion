from copy import deepcopy
from dataclasses import asdict, dataclass
from enum import Enum, auto
from hmac import new
from typing import Dict, List, Optional, Self, Set, Tuple
from serenity.common.definitions import Direction
import math
from serenity.sonar.definitions import (
    Asteroid,
    CellModel,
    Damage,
    GameActor,
    GridPosition,
    Launchable,
    MapModel,
    Mine,
    Owner,
    Ship,
    Torpedo,
    Trail,
)
from serenity.sonar.exceptions import CannotBeAddedToCell, ShipDestroyed


class Cell:
    def __init__(self, cell: CellModel) -> None:
        self._content = cell.content
        self._has_asteroid = cell.has_asteroid

    def to_model(self) -> CellModel:
        return CellModel(
            content=[actor for actor in self._content],
            has_asteroid=self._has_asteroid,
        )

    def _has_trail_for(self, owner: Owner) -> bool:
        return any(isinstance(actor, Trail) and actor.owner == owner for actor in self._content)

    def has_asteroid(self) -> bool:
        return self._has_asteroid

    def ship_for(self, owner: Owner) -> Optional[Ship]:
        for actor in self._content:
            if isinstance(actor, Ship) and actor.owner == owner:
                return actor
        return None

    def find_mine(self, mine_uid: str) -> Optional[Mine]:
        for actor in self._content:
            if isinstance(actor, Mine) and actor.uid == mine_uid:
                return actor
        return None

    def add(self, actor: GameActor):
        if self._has_asteroid and not isinstance(actor, Torpedo):
            raise CannotBeAddedToCell()

        match actor:
            case Asteroid():
                self._has_asteroid = True
            case Ship(owner=owner):
                if self._has_trail_for(owner):
                    raise CannotBeAddedToCell()
                self._content.add(actor)
            case Trail():
                self._content.add(actor)
            case Mine():
                self._content.add(actor)
            case Torpedo():
                pass  # Do not raise
            case _:
                raise ValueError(f"Unknown actor type: {actor}")

    def remove(self, actor: GameActor):
        self._content.remove(actor)

    def apply_damage(self, damage: int) -> List[Damage]:
        inflicted = []
        old_objects = []
        new_objects = []
        for actor in self._content:
            try:
                new_actor = actor.apply_damage(damage)
                inflicted.append(Damage(amount=damage, owner=new_actor.owner))
                old_objects.append(actor)
                new_objects.append(new_actor)
            except AttributeError:
                pass

        for old_actor in old_objects:
            self._content.remove(old_actor)

        for new_actor in new_objects:
            self._content.add(new_actor)

        return inflicted


@dataclass(frozen=True)
class CellDistance:
    cell: Cell
    distance: int
    position: GridPosition


class Map:
    def __init__(
        self,
        map: MapModel,
    ):
        self.width = map.width
        self.height = map.height

        self._grid = [[Cell(cell) for cell in row] for row in map.grid]

        self._mine_positions: Dict[str, GridPosition] = {}

        self._ship_positions = map.ship_positions

        for owner, ship in [(Owner.PLAYERS, map.player_ship), (Owner.NPCS, map.npc_ship)]:
            ship_position = self._ship_positions[owner]
            self._grid[ship_position.y][ship_position.x].add(ship)

    def to_model(self) -> MapModel:
        return MapModel(
            width=self.width,
            height=self.height,
            grid=[[cell.to_model() for cell in row] for row in self._grid],
            player_ship=self.ship_for(Owner.PLAYERS),
            npc_ship=self.ship_for(Owner.NPCS),
            ship_positions=self._ship_positions,
            mine_positions=self._mine_positions,
        )

    def get_asteroid_positions(self) -> List[GridPosition]:
        # search asteroid positions
        asteroid_positions = []
        for y in range(self.height):
            for x in range(self.width):
                if isinstance(self._grid[y][x], Asteroid):
                    asteroid_positions.append(GridPosition(x, y))
        return asteroid_positions

    def ship_for(self, owner: Owner) -> Ship:
        ship_position = self._ship_positions[owner]
        ship_cell = self._grid[ship_position.y][ship_position.x]
        return ship_cell.ship_for(owner)

    def move_ship(self, owner: Owner, move_direction: Direction) -> None:
        if move_direction not in self.available_moves_for_ship(owner):
            raise ValueError(f"Invalid move direction: {move_direction}")

        ship_position = self._ship_positions[owner]
        current_cell = self._grid[ship_position.y][ship_position.x]
        ship = current_cell.ship_for(owner)

        current_cell.remove(ship)
        current_cell.add(Trail(owner=owner))

        new_pos = self._position_at(ship_position, move_direction)

        self._grid[new_pos.y][new_pos.x].add(ship)
        self._ship_positions[owner] = new_pos

    def _position_at(self, position: GridPosition, direction: Direction) -> GridPosition:
        match direction:
            case Direction.North:
                return GridPosition(position.x, position.y - 1)
            case Direction.South:
                return GridPosition(position.x, position.y + 1)
            case Direction.East:
                return GridPosition(position.x + 1, position.y)
            case Direction.West:
                return GridPosition(position.x - 1, position.y)

    def remove_hp(self, owner: Owner, hp: int) -> None:
        cell = self._grid[self._ship_positions[owner].y][self._ship_positions[owner].x]
        cell.apply_damage(hp)

    def available_moves_for_ship(self, owner: Owner) -> List[Direction]:
        ship_position = self._ship_positions[owner]
        current_cell = self._grid[ship_position.y][ship_position.x]
        ship = current_cell.ship_for(owner)

        surrounding_cells = {}

        if ship_position.y > 0:
            surrounding_cells[Direction.North] = self._grid[ship_position.y - 1][ship_position.x]
        if ship_position.y < self.height - 1:
            surrounding_cells[Direction.South] = self._grid[ship_position.y + 1][ship_position.x]
        if ship_position.x > 0:
            surrounding_cells[Direction.West] = self._grid[ship_position.y][ship_position.x - 1]
        if ship_position.x < self.width - 1:
            surrounding_cells[Direction.East] = self._grid[ship_position.y][ship_position.x + 1]

        available_moves = []

        for direction, cell in surrounding_cells.items():
            if self._can_be_added_to_cell(ship, cell):
                available_moves.append(direction)

        return available_moves

    def _can_be_added_to_cell(self, actor: GameActor, cell: Cell) -> bool:
        try:
            test_cell = deepcopy(cell)
            test_cell.add(actor)
            return True
        except CannotBeAddedToCell:
            return False

    def possible_object_launch(self, launchable: Launchable) -> Set[GridPosition]:
        ship_position = self._ship_positions[launchable.owner]

        in_radius = self._cells_in_radius(ship_position, launchable.reach)

        possible_positions = set()
        for cell_distance in in_radius:
            if self._can_be_added_to_cell(launchable, cell_distance.cell):
                possible_positions.add(cell_distance.position)

        return possible_positions

    def launch_torpedo(self, torpedo: Torpedo, target: GridPosition) -> List[Damage]:
        if target not in self.possible_object_launch(torpedo):
            raise ValueError(f"Invalid target position: {target}")
        inflicted = self._apply_damage_with_falloff(torpedo, target)
        return inflicted

    def place_mine(self, mine: Mine, position: GridPosition) -> None:
        if position not in self.possible_object_launch(mine):
            raise ValueError(f"Invalid mine placement: {position}")
        self._grid[position.y][position.x].add(mine)
        self._mine_positions[mine.uid] = position

    def _find_mine(self, mine_uid: str) -> Tuple[Mine, GridPosition]:
        for mine_uid, position in self._mine_positions.items():
            mine = self._grid[position.y][position.x].find_mine(mine_uid)
            if mine is not None:
                return mine, position
        raise ValueError(f"Mine {mine_uid} not found")

    def _apply_damage_with_falloff(self, launchable: Launchable, target: GridPosition) -> List[Damage]:
        damaged_cells = self._cells_in_radius(target, launchable.radius)

        inflicted_damages = []
        for cell_distance in damaged_cells:
            damage = launchable.damage - cell_distance.distance
            print(cell_distance.cell._content, cell_distance.distance)
            inflicted = cell_distance.cell.apply_damage(damage)
            inflicted_damages.extend(inflicted)
        return inflicted_damages

    def detonate_mine(self, mine_uid: str) -> List[Damage]:
        mine, mine_position = self._find_mine(mine_uid)
        inflicted = self._apply_damage_with_falloff(mine, mine_position)
        self._grid[mine_position.y][mine_position.x].remove(mine)
        del self._mine_positions[mine_uid]
        return inflicted

    def _grid_distance(self, a: GridPosition, b: GridPosition) -> int:
        dx = abs(a.x - b.x)
        dy = abs(a.y - b.y)

        return max(dx, dy)

    def _cells_in_radius(self, position: GridPosition, reach: int) -> List[CellDistance]:
        cell_distances = []
        for y in range(position.y - reach, position.y + reach + 1):
            for x in range(position.x - reach, position.x + reach + 1):
                if x < 0 or x >= self.width or y < 0 or y >= self.height:
                    continue

                target = GridPosition(x, y)
                distance = self._grid_distance(position, target)

                if distance > reach:
                    continue

                cell = self._grid[y][x]
                cell_distances.append(CellDistance(cell, distance, target))

        return cell_distances
