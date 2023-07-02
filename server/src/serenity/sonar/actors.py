import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Union


class Owner(Enum):
    Players = auto()
    NPCs = auto()


@dataclass(frozen=True)
class Trail:
    owner: Owner


@dataclass(frozen=True)
class Ship:
    name: str
    hp: int
    owner: Owner

    def __post_init__(self):
        if self.hp <= 0:
            raise ShipDestroyed()

    def apply_damage(self, damage: int) -> Ship:
        return Ship(self.name, self.hp - damage, self.owner)


@dataclass(frozen=True)
class Launchable:
    owner: Owner
    damage: int
    reach: int
    radius: int


class Mine(Launchable):
    uid: str = field(init=False)

    def __post_init__(self):
        self.uid = str(uuid.uuid4())


class Torpedo(Launchable):
    pass


@dataclass(frozen=True)
class Asteroid:
    """Asteroid."""


GameActor = Union[Ship, Asteroid, Trail, Mine]
