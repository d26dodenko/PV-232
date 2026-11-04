from enum import Enum, auto
from random import Random

from .body import Cell, Direction, Snake

class Status(Enum):
  PLAYING = auto()
  LOST = auto()
  WON = auto()


class SnakeGame:
  def __init__(self, width: int = 20, height: int = 16, rng: Random | None = None):
    if width < 4 or height < 2:
      raise ValueError("The board must be at least 4 by 2 cells")
    self.width = width
    self.height = height
    self._rng = rng if rng is not None else Random()
    self.restart()

  def restart(self) -> None:
    self.snake = Snake((self.width // 2, self.height // 2))
    self.status = Status.PLAYING
    self.food = self._place_food()

  @property
  def score(self) -> int:
    return len(self.snake.body) - Snake.START_LENGTH

  def _place_food(self) -> Cell | None:
    occupied = set(self.snake.body)
    free = [
      (x, y) for y in range(self.height) for x in range(self.width)
      if (x, y) not in occupied
    ]
    return self._rng.choice(free) if free else None

  def turn(self, direction: Direction) -> None:
    if self.status is Status.PLAYING:
      self.snake.turn(direction)

  def step(self) -> None:
    if self.status is not Status.PLAYING:
      return
    head = self.snake.next_head()
    x, y = head
    inside = 0 <= x < self.width and 0 <= y < self.height

    if not inside or head in self.snake.body[:-1]:
      self.status = Status.LOST
      return
    grow = head == self.food
    self.snake.move_to(head, grow)
    if grow:
      self.food = self._place_food()
      if self.food is None:
        self.status = Status.WON
