from random import Random
import runpy
from statistics import median
from time import perf_counter_ns

import pygame as pg
import pytest

from battleship.app import (
    AMBER, CORAL, CPU_DELAY, HOME, HULL, MUTED, RESTART, SEA, TARGET, TILE, WINDOW, App,
)
from battleship.board import CELLS, Shot
from battleship.game import Side


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    pg.display.init()
    pg.font.init()
    try:
        yield App(pg.display.set_mode(WINDOW), Random(232))
    finally:
        pg.quit()


def center(area, cell):
    x, y = cell
    return area.x + x * TILE + TILE // 2, area.y + y * TILE + TILE // 2


def click(pos, button=1):
    return pg.event.Event(pg.MOUSEBUTTONDOWN, pos=pos, button=button)


def test_own_fleet_is_visible_enemy_stays_hidden_until_shot(app):
    app.draw()
    own = next(iter(app.game.player.ship_at))
    assert app.screen.get_at(center(HOME, own)) == pg.Color(HULL)
    ship = next(ship for ship in app.game.enemy.ship_at.values() if len(ship) == 2)
    first, last = ship
    assert app.screen.get_at(center(TARGET, first)) == pg.Color(SEA)
    app.handle(click(center(TARGET, first)), 0)
    app.draw()
    assert app.screen.get_at(center(TARGET, first)) == pg.Color(AMBER)
    assert app.screen.get_at(center(TARGET, last)) == pg.Color(SEA)
    app.handle(click(center(TARGET, last)), 1)
    app.draw()
    assert all(app.screen.get_at(center(TARGET, cell)) == pg.Color(CORAL) for cell in ship)


def test_miss_allows_exactly_one_delayed_computer_shot(app):
    water = next(cell for cell in CELLS if cell not in app.game.enemy.ship_at)
    app.handle(click(center(TARGET, water)), 100)
    app.draw()
    assert app.screen.get_at(center(TARGET, water)) == pg.Color(MUTED)
    assert app.game.turn is Side.COMPUTER
    app.handle(click(center(TARGET, (9, 9))), 200)
    assert app.game.enemy.shots == {water: Shot.MISS}
    app.update(100 + CPU_DELAY - 1)
    assert not app.game.player.shots
    app.update(100 + CPU_DELAY)
    app.update(100 + CPU_DELAY)
    assert len(app.game.player.shots) == 1


def test_board_boundaries_and_mouse_buttons(app):
    for pos in [center(HOME, (0, 0)), (TARGET.right, TARGET.top), (TARGET.left, TARGET.bottom)]:
        app.handle(click(pos), 0)
    app.handle(pg.event.Event(pg.KEYDOWN, key=pg.K_SPACE), 0)
    app.handle(click(center(TARGET, (0, 0)), button=3), 0)
    assert not app.game.enemy.shots
    app.handle(click((TARGET.right - 1, TARGET.bottom - 1)), 0)
    assert (9, 9) in app.game.enemy.shots


@pytest.mark.parametrize("event", [
    pg.event.Event(pg.KEYDOWN, key=pg.K_r),
    click(RESTART.center),
])
def test_new_game_restores_both_fleets(event, app):
    old = app.game
    old.player_shot((0, 0))
    assert app.handle(event, 10)
    assert app.game is not old
    assert app.game.turn is Side.PLAYER and app.game.winner is None
    for board in (app.game.player, app.game.enemy):
        assert board.afloat == 10 and not board.shots


@pytest.mark.parametrize("winner, caption", [
    (Side.PLAYER, "Вы победили!"),
    (Side.COMPUTER, "Победил компьютер"),
])
def test_end_screen_names_winner_and_stops_turns(winner, caption, app, monkeypatch):
    app.game.winner = winner
    app.game.turn = winner
    labels = []
    monkeypatch.setattr(app, "label", lambda text, *args: labels.append(text))
    app.update(CPU_DELAY)
    app.handle(click(TARGET.center), CPU_DELAY)
    app.draw()
    assert caption in labels
    assert not app.game.player.shots and not app.game.enemy.shots


@pytest.mark.parametrize("event", [
    pg.event.Event(pg.KEYDOWN, key=pg.K_ESCAPE), pg.event.Event(pg.QUIT),
])
def test_exit_controls(event, app):
    assert not app.handle(event, 0)


def test_click_to_frame(monkeypatch):
    """От отправки щелчка сразу после первого кадра до кадра с отметкой."""
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    real_flip = pg.display.flip
    pos = center(TARGET, (9, 9))
    samples = []

    def flip():
        nonlocal started
        real_flip()
        pixel = pg.display.get_surface().get_at(pos)
        if started is None:
            assert pixel == pg.Color(SEA)
            started = perf_counter_ns()
            assert pg.event.post(click(pos))
        else:
            elapsed = (perf_counter_ns() - started) / 1_000_000
            assert pixel in [pg.Color(c) for c in (MUTED, AMBER, CORAL)]
            samples.append(elapsed)
            assert pg.event.post(pg.event.Event(pg.QUIT))

    monkeypatch.setattr(pg.display, "flip", flip)
    for _ in range(9):
        started = None
        runpy.run_module("battleship", run_name="__main__")
    assert len(samples) == 9
    print(f"Клик → кадр, мс: {[round(v, 2) for v in samples]}; медиана {median(samples):.2f}")
