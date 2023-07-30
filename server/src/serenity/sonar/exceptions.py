from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from serenity.sonar.definitions import Ship


class ShipDestroyed(Exception):
    """Raised when a ship is destroyed."""

    def __init__(self, ship: Ship):
        super().__init__(f"Ship {ship.name} was destroyed.")
        self.ship = ship


class CannotBeAddedToCell(Exception):
    """Raised when an actor cannot be added to a cell."""
