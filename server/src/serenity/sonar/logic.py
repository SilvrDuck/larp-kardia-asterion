from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Tuple

from serenity.sonar.actors import Asteroid, GameActor, Launchable, Mine, Owner, Ship, Torpedo, Trail
from serenity.sonar.exceptions import CannotBeAddedToCell
from serenity.sonar.game_config import GameConfig


@dataclass(frozen=True)
class GridPosition:
    x: int
    y: int


class Cell:
    def __init__(self):
        self._content = set()
        self._has_asteroid = False

    def _has_trail_for(self, owner: Owner) -> bool:
        return any(isinstance(actor, Trail) and actor.owner == owner for actor in self._content)

    def ship_for(self, owner: Owner) -> Optional[Ship]:
        for actor in self._content:
            if isinstance(actor, Ship) and actor.owner == owner:
                return actor
        raise None

    def find_mine(self, mine_uid: str) -> Optional[Mine]:
        for actor in self._content:
            if isinstance(actor, Mine) and actor.uid == mine_uid:
                return actor
        return None

    def add(self, actor: GameActor):
        if self._has_asteroid:
            raise CannotBeAddedToCell()

        match actor:
            case Asteroid():
                self._has_asteroid = True
            case Ship(name, hp, owner):
                if self._has_trail_for(owner):
                    raise CannotBeAddedToCell()
            case Trail():
                self._content.add(actor)
            case Mine():
                self._content.add(actor)
            case _:
                raise ValueError(f"Unknown actor type: {actor}")

    def remove(self, actor: GameActor):
        self._content.remove(actor)

    def apply_damage(self, damage: int):
        for actor in self._content:
            try:
                actor = actor.apply_damage(damage)
            except AttributeError:
                pass


class Direction(Enum):
    North = auto()
    South = auto()
    East = auto()
    West = auto()


@dataclass(frozen=True)
class CellDistance:
    cell: Cell
    distance: int


class Map:
    def __init__(
        self,
        width: int,
        height: int,
        player_ship: Ship,
        npc_ship: Ship,
        player_ship_position: GridPosition,
        npc_ship_position: GridPosition,
        asteroid_positions: List[GridPosition],
        game_config: GameConfig,
    ):
        self.game_config = game_config

        self.width = width
        self.height = height
        self._grid = [[Cell() for _ in range(width)] for _ in range(height)]
        self._ship_positions = {
            Owner.Players: player_ship_position,
            Owner.NPCs: npc_ship_position,
        }

        for owner, ship in [(Owner.Players, player_ship), (Owner.NPCs, npc_ship)]:
            ship_position = self._ship_positions[owner]
            for ship_position in ship_position:
                self._grid[ship_position.y][ship_position.x].add(ship)

        for asteroid in asteroid_positions:
            self._grid[asteroid.y][asteroid.x] = Asteroid()

    def move_ship(self, owner: Owner, move_direction: Direction) -> None:
        ship_position = self._ship_positions[owner]
        current_cell = self._grid[ship_position.y][ship_position.x]
        ship = current_cell.ship_for(owner)
        current_cell.remove(ship)

        match move_direction:
            case Direction.North:
                self._grid[ship_position.y - 1][ship_position.x].add(ship)
            case Direction.South:
                self._grid[ship_position.y + 1][ship_position.x].add(ship)
            case Direction.East:
                self._grid[ship_position.y][ship_position.x + 1].add(ship)
            case Direction.West:
                self._grid[ship_position.y][ship_position.x - 1].add(ship)

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

    def _can_be_added_to_cell(self, actor: GameActor, cell: Cell) -> bool:
        try:
            test_cell = cell.copy()
            test_cell.add(actor)
            return True
        except CannotBeAddedToCell:
            return False

    def possible_object_launch(self, launchable: Launchable) -> List[GridPosition]:
        ship_position = self._ship_positions[launchable.owner]

        in_radius = self._cells_in_radius(ship_position, launchable.reach)

        possible_positions = []
        for cell_distance in in_radius:
            if self._can_be_added_to_cell(launchable, cell_distance.cell):
                possible_positions.append(cell_distance.cell.position)

        return possible_positions

    def launch_torpedo(self, torpedo: Torpedo, target: GridPosition) -> None:
        assert self.possible_object_launch(torpedo).contains(target)
        self._apply_damage_with_falloff(torpedo, target)

    def place_mine(self, mine: Mine, position: GridPosition) -> str:
        assert self.possible_object_launch(mine).contains(position)
        self._grid[position.y][position.x].add(mine)
        return mine.uid

    def _find_mine(self, mine_uid: str) -> Tuple[Mine, GridPosition]:
        for row in self._grid:
            for cell in row:
                mine = cell.find_mine(mine_uid)
                if mine is not None:
                    return mine, cell.position
        raise ValueError(f"Mine {mine_uid} not found")

    def _apply_damage_with_falloff(self, launchable: Launchable, target: GridPosition) -> None:
        damaged_cells = self._cells_in_radius(target, launchable.radius)
        for cell_distance in damaged_cells:
            damage = launchable.damage - cell_distance.distance
            cell_distance.cell.apply_damage(damage)

    def detonate_mine(self, mine_uid: str) -> None:
        mine, mine_position = self._find_mine(mine_uid)
        self._apply_damage_with_falloff(mine, mine_position)

    def _cells_in_radius(self, position: GridPosition, reach: int) -> List[CellDistance]:
        cell_distances = []
        for y in range(position.y - reach, position.y + reach + 1):
            for x in range(position.x - reach, position.x + reach + 1):
                if x < 0 or x >= self.width or y < 0 or y >= self.height:
                    continue
                if abs(position.x - x) + abs(position.y - y) > reach:
                    continue

                cell = self._grid[y][x]
                distance = abs(position.x - x) + abs(position.y - y)
                cell_distances.append(CellDistance(cell, distance))

        return cell_distances
