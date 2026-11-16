import pygame

from .body import Cell, Direction
from .game import SnakeGame, Status

class PygameApp:
  CELL = 24
  HEADER = 40
  MOVE_MS = 140
  MOVE_EVENT = pygame.USEREVENT + 1
  ARROWS = {
    pygame.K_UP: Direction.UP,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
  }
  MESSAGES = {
    Status.PLAYING: "Arrows to steer",
    Status.LOST: "Game over!  R to restart",
    Status.WON: "You won!  R to restart",
  }

  def __init__(self, game: SnakeGame):
    self.game = game
    size = (game.width * self.CELL, self.HEADER + game.height * self.CELL)
    self.screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Snake")
    self.font = pygame.font.Font(None, 24)

  def handle(self, event: pygame.event.Event) -> bool:
    if event.type == pygame.QUIT:
      return False
    if event.type == self.MOVE_EVENT:
      self.game.step()
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        return False
      if event.key in self.ARROWS:
        self.game.turn(self.ARROWS[event.key])
      elif event.key == pygame.K_r and self.game.status is not Status.PLAYING:
        self.game.restart()
    return True

  def draw_cell(self, cell: Cell, color: str) -> None:
    x, y = cell
    rect = (x * self.CELL, self.HEADER + y * self.CELL, self.CELL, self.CELL)
    pygame.draw.rect(self.screen, color, pygame.Rect(rect).inflate(-2, -2))

  def draw(self) -> None:
    self.screen.fill("#19232c")
    pygame.draw.rect(self.screen, "#263642", (0, 0, self.screen.get_width(), self.HEADER))
    for cell in self.game.snake.body[1:]:
      self.draw_cell(cell, "#72b970")
    self.draw_cell(self.game.snake.body[0], "#b8e994")
    if self.game.food is not None:
      self.draw_cell(self.game.food, "#ff866e")
    label = f"Score {self.game.score}    {self.MESSAGES[self.game.status]}"
    self.screen.blit(self.font.render(label, True, "#f1f5f8"), (8, 10))
    pygame.display.flip()

  def run(self) -> None:
    pygame.time.set_timer(self.MOVE_EVENT, self.MOVE_MS)
    self.draw()
    while self.handle(pygame.event.wait()):
      self.draw()


def main() -> None:
  pygame.init()
  try:
    PygameApp(SnakeGame()).run()
  finally:
    pygame.quit()
