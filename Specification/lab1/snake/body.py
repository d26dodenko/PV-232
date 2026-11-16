from enum import Enum

Cell = tuple[int, int]


class Direction(Enum):
  UP = (0, -1)
  DOWN = (0, 1)
  LEFT = (-1, 0)
  RIGHT = (1, 0)

  @property
  def opposite(self) -> "Direction":
    dx, dy = self.value
    return Direction((-dx, -dy))


class Snake:
  START_LENGTH = 3

  def __init__(self, head: Cell):
    x, y = head
    self.body = tuple((x - i, y) for i in range(self.START_LENGTH))
    self.direction = Direction.RIGHT
    self._next_direction = self.direction

  def turn(self, direction: Direction) -> None:
    if self._next_direction != self.direction:
      return
    if direction != self.direction.opposite:
      self._next_direction = direction

  def next_head(self) -> Cell:
    x, y = self.body[0]
    dx, dy = self._next_direction.value
    return x + dx, y + dy

  def move_to(self, head: Cell, grow: bool) -> None:
    self.body = (head,) + (self.body if grow else self.body[:-1])
    self.direction = self._next_direction
