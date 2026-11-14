from enum import Enum
from random import Random
from typing import Optional

Cell = tuple[int, int]


class Direction(Enum):
    UP = (0, -1)
    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)


class State(Enum):
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    LOST = "lost"
    WON = "won"


class SnakeGame:
    def __init__(
        self,
        width: int = 24,
        height: int = 18,
        rng: Optional[Random] = None,
    ) -> None:
        if width < 4 or height < 2:
            raise ValueError("Board must be at least 4 by 2 cells")
        self.width = width
        self.height = height
        self.rng = rng if rng is not None else Random()
        self.reset()

    def reset(self) -> None:
        x, y = self.width // 2, self.height // 2
        self.snake = [(x, y), (x - 1, y), (x - 2, y)]
        self.direction = Direction.RIGHT
        self.pending_direction = self.direction
        self.turn_pending = False
        self.score = 0
        self.state = State.READY
        self.food = self.generate_food()

    def start(self) -> None:
        self.reset()
        self.state = State.RUNNING

    def toggle_pause(self) -> None:
        if self.state is State.RUNNING:
            self.state = State.PAUSED
        elif self.state is State.PAUSED:
            self.state = State.RUNNING

    def turn(self, direction: Direction) -> bool:
        if self.state is not State.RUNNING:
            return False
        if self.turn_pending:
            return False
        dx, dy = self.direction.value
        if direction.value == (-dx, -dy):
            return False
        if direction is self.direction:
            return False
        self.pending_direction = direction
        self.turn_pending = True
        return True

    def generate_food(self) -> Optional[Cell]:
        occupied = set(self.snake)
        free = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in occupied
        ]
        return self.rng.choice(free) if free else None

    def step(self) -> None:
        if self.state is not State.RUNNING:
            return
        self.direction = self.pending_direction
        self.turn_pending = False
        dx, dy = self.direction.value
        x, y = self.snake[0]
        head = (x + dx, y + dy)
        grows = head == self.food
        body = self.snake if grows else self.snake[:-1]
        if self.collides(head, body):
            self.state = State.LOST
            return
        self.snake.insert(0, head)
        if grows:
            self.score += 10
            self.food = self.generate_food()
            if self.food is None:
                self.state = State.WON
        else:
            self.snake.pop()

    def collides(self, head: Cell, body: list[Cell]) -> bool:
        x, y = head
        if x < 0 or x >= self.width:
            return True
        if y < 0 or y >= self.height:
            return True
        return head in body
