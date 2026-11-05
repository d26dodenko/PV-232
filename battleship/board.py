"""Расстановка флота и результаты выстрелов по одному полю."""

from enum import Enum
from random import Random

Cell = tuple[int, int]
Ship = frozenset[Cell]
SIZE = 10
FLEET = (4, 3, 3, 2, 2, 2, 1, 1, 1, 1)
CELLS = tuple((x, y) for y in range(SIZE) for x in range(SIZE))


class Shot(Enum):
    MISS = "мимо"
    HIT = "попадание"
    SUNK = "корабль потоплен"


def placements(length: int) -> list[Ship]:
    """Все горизонтальные и вертикальные позиции корабля на поле."""
    directions = [(1, 0)] if length == 1 else [(1, 0), (0, 1)]
    return [
        frozenset((x + i * dx, y + i * dy) for i in range(length))
        for dx, dy in directions
        for x, y in CELLS
        if x + (length - 1) * dx < SIZE and y + (length - 1) * dy < SIZE
    ]


POSITIONS = {length: placements(length) for length in set(FLEET)}


def place_fleet(rng: Random) -> list[Ship]:
    def place(index: int, blocked: set[Cell]) -> list[Ship] | None:
        if index == len(FLEET):
            return []
        options = [ship for ship in POSITIONS[FLEET[index]] if ship.isdisjoint(blocked)]
        rng.shuffle(options)
        for ship in options:
            margin = {
                (x + dx, y + dy)
                for x, y in ship
                for dx in (-1, 0, 1)
                for dy in (-1, 0, 1)
            }
            rest = place(index + 1, blocked | margin)
            if rest is not None:
                return [ship, *rest]
        return None

    fleet = place(0, set())
    if fleet is None:
        raise ValueError("Флот не помещается на поле")
    return fleet


class Board:
    def __init__(self, fleet: list[Ship]):
        self.ship_at = {cell: ship for ship in fleet for cell in ship}
        self.afloat = len(fleet)
        self.shots: dict[Cell, Shot] = {}

    def fire(self, cell: Cell) -> Shot | None:
        """Вернуть результат нового выстрела. Недопустимый ход ничего не меняет."""
        if cell not in CELLS or cell in self.shots:
            return None
        ship = self.ship_at.get(cell)
        if ship is None:
            self.shots[cell] = Shot.MISS
            return Shot.MISS

        self.shots[cell] = Shot.HIT
        if ship <= self.shots.keys():
            self.shots.update(dict.fromkeys(ship, Shot.SUNK))
            self.afloat -= 1
        return self.shots[cell]
