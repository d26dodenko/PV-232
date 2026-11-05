"""Очередность ходов в партии между игроком и компьютером."""

from enum import Enum
from random import Random

from .board import Board, CELLS, Cell, Shot, place_fleet


class Side(Enum):
    PLAYER = "Игрок"
    COMPUTER = "Компьютер"


class Game:
    def __init__(self, player: Board, enemy: Board, rng: Random):
        self.player = player
        self.enemy = enemy
        self.rng = rng
        self.turn = Side.PLAYER
        self.winner: Side | None = None
        self.last_shot: tuple[Side, Cell, Shot] | None = None

    @classmethod
    def new(cls, rng: Random) -> "Game":
        return cls(Board(place_fleet(rng)), Board(place_fleet(rng)), rng)

    def player_shot(self, cell: Cell) -> None:
        if self.winner is None and self.turn is Side.PLAYER:
            self._shoot(self.enemy, cell, Side.COMPUTER)

    def computer_shot(self) -> None:
        if self.winner is None and self.turn is Side.COMPUTER:
            targets = [cell for cell in CELLS if cell not in self.player.shots]
            self._shoot(self.player, self.rng.choice(targets), Side.PLAYER)

    def _shoot(self, target: Board, cell: Cell, opponent: Side) -> None:
        result = target.fire(cell)
        if result is None:
            return
        self.last_shot = (self.turn, cell, result)
        if target.afloat == 0:
            self.winner = self.turn
        elif result is Shot.MISS:
            self.turn = opponent
