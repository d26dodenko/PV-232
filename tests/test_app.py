import runpy
from random import Random
from time import perf_counter

import pygame
import pytest

from snake.app import PygameApp
from snake.body import Direction
from snake.game import SnakeGame, Status

@pytest.fixture
def app(monkeypatch):
  monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
  monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
  pygame.init()
  try:
    yield PygameApp(SnakeGame(rng=Random(1)))
  finally:
    pygame.quit()


def key(code):
  return pygame.event.Event(pygame.KEYDOWN, key=code)


@pytest.mark.parametrize(("key_code", "direction"), [
  (pygame.K_UP, Direction.UP), (pygame.K_DOWN, Direction.DOWN),
  (pygame.K_LEFT, Direction.LEFT), (pygame.K_RIGHT, Direction.RIGHT),
])
def test_arrow_and_timer_move_the_head(app, key_code, direction):
  if direction is Direction.LEFT:
    app.handle(key(pygame.K_UP))
    app.handle(pygame.event.Event(app.MOVE_EVENT))

  x, y = app.game.snake.body[0]
  dx, dy = direction.value
  assert app.handle(key(key_code))
  assert app.game.snake.body[0] == (x, y)
  assert app.handle(pygame.event.Event(app.MOVE_EVENT))
  assert app.game.snake.body[0] == (x + dx, y + dy)


def test_restart_key_only_restarts_finished_game(app):
  initial = app.game.snake.body
  app.game.step()
  assert app.handle(key(pygame.K_r))
  assert app.game.snake.body != initial
  while app.game.status is Status.PLAYING:
    app.game.step()

  assert app.game.status is Status.LOST
  assert app.handle(key(pygame.K_r))
  assert app.game.snake.body == initial
  assert app.game.status is Status.PLAYING


def test_unmapped_key_window_event_and_exits(app):
  initial = app.game.snake.body
  assert app.handle(key(pygame.K_SPACE))
  assert app.handle(pygame.event.Event(pygame.MOUSEMOTION))
  assert app.game.snake.body == initial
  assert not app.handle(key(pygame.K_ESCAPE))
  assert not app.handle(pygame.event.Event(pygame.QUIT))


def test_board_draws_head_body_and_food(app):
  def pixel_at(cell):
    x, y = cell
    return app.screen.get_at(
      (x * app.CELL + app.CELL // 2, app.HEADER + y * app.CELL + app.CELL // 2)
    )

  app.draw()
  head = app.game.snake.body[0]
  body = app.game.snake.body[1]
  food = app.game.food
  assert pixel_at(head) == pygame.Color("#b8e994")
  assert pixel_at(body) == pygame.Color("#72b970")
  assert pixel_at(food) == pygame.Color("#ff866e")
  app.game.status = Status.WON
  app.game.food = None
  app.draw()
  assert pixel_at(food) == pygame.Color("#19232c")


def test_entrypoint_response(monkeypatch):
  monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
  monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
  draw = PygameApp.draw
  sent = None
  target = None
  elapsed_ms = None

  def observe_frame(app):
    nonlocal sent, target, elapsed_ms
    draw(app)
    head = app.game.snake.body[0]
    if sent is None:
      pygame.time.set_timer(pygame.QUIT, 2000, loops=1)
      target = (head[0], head[1] - 1)
      sent = perf_counter()
      pygame.event.post(key(pygame.K_UP))
    elif head == target and elapsed_ms is None:
      elapsed_ms = (perf_counter() - sent) * 1000
      pygame.event.post(pygame.event.Event(pygame.QUIT))

  monkeypatch.setattr(PygameApp, "draw", observe_frame)
  runpy.run_module("snake", run_name="__main__")
  assert not pygame.get_init()
  assert elapsed_ms is not None, "The turn did not appear before the timeout"
  print(f"Input to frame: {elapsed_ms:.1f} ms")
