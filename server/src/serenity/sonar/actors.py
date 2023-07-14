import uuid
from dataclasses import dataclass, field
from typing import List, Self, Union

from serenity.common.definitions import Owner
from serenity.sonar.exceptions import ShipDestroyed


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

    def apply_damage(self, damage: int) -> Self:
        return Ship(self.name, self.hp - damage, self.owner)


@dataclass(frozen=True)
class Launchable:
    owner: Owner
    damage: int
    reach: int
    radius: int


class Mine(Launchable):
    uid: str = field(init=False)

    def __post_init__(self) -> None:
        self.uid = str(uuid.uuid4())


class Torpedo(Launchable):
    pass


@dataclass(frozen=True)
class Asteroid:
    """Asteroid."""


GameActor = Union[Ship, Asteroid, Trail, Mine]
