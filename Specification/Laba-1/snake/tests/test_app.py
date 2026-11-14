import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import pytest

from snake_game.app import App
from snake_game.model import Direction, State


@pytest.fixture
def app(tmp_path):
    result = App(tmp_path / "best.json")
    yield result
    pygame.quit()


def key(app, code):
    app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=code))


def test_menu_speed_start_pause_resume_restart_exit(app):
    app.draw()
    key(app, pygame.K_3)
    assert app.speed == 2
    key(app, pygame.K_RETURN)
    assert app.game.state is State.RUNNING
    key(app, pygame.K_1)
    assert app.speed == 2
    key(app, pygame.K_w)
    assert app.game.pending_direction is Direction.UP
    key(app, pygame.K_SPACE)
    assert app.game.state is State.PAUSED
    before = app.game.snake.copy()
    app.update(1)
    assert app.game.snake == before
    key(app, pygame.K_2)
    key(app, pygame.K_RETURN)
    assert app.game.state is State.RUNNING
    assert app.speed == 1
    key(app, pygame.K_r)
    assert app.game.score == 0
    key(app, pygame.K_ESCAPE)
    assert app.game.state is State.READY
    key(app, pygame.K_ESCAPE)
    assert not app.running


def test_focus_loss_and_clicks(app):
    app.handle_click(app.view.speed_buttons[0].center)
    assert app.speed == 0
    app.handle_click(app.view.play_button.center)
    app.handle_click(app.view.speed_buttons[2].center)
    assert app.speed == 0
    app.handle_event(pygame.event.Event(pygame.WINDOWFOCUSLOST))
    assert app.game.state is State.PAUSED
    app.handle_event(
        pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=app.view.play_button.center,
        )
    )
    assert app.game.state is State.RUNNING


def test_tick_record_and_loss(app):
    app.start()
    x, y = app.game.snake[0]
    app.game.food = (x + 1, y)
    app.update(0.101)
    assert app.best == 10
    assert app.record_path.exists()
    for _ in range(30):
        app.update(0.101)
    assert app.game.state is State.LOST
    app.draw()
    key(app, pygame.K_RETURN)
    assert app.game.score == 0
    assert app.best == 10


def test_all_screens_render(app):
    for state in State:
        app.game.state = state
        app.draw()
    app.game.food = None
    app.save_failed = True
    app.draw()


def test_real_event_loop_exits(app):
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    app.run()
    assert not pygame.get_init()
