from pathlib import Path
from typing import Optional

import pygame

from .model import Direction, SnakeGame, State
from .storage import load_record, save_record
from .view import SIZE, SPEEDS, View

DIRECTIONS = {
    pygame.K_UP: Direction.UP,
    pygame.K_w: Direction.UP,
    pygame.K_RIGHT: Direction.RIGHT,
    pygame.K_d: Direction.RIGHT,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_s: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_a: Direction.LEFT,
}


class App:
    def __init__(self, record_path: Optional[Path] = None) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(SIZE)
        pygame.display.set_caption("Mint Snake")
        self.view = View(self.screen)
        self.game = SnakeGame()
        self.record_path = record_path or Path.home() / ".mint_snake/best.json"
        self.best = load_record(self.record_path)
        self.save_failed = False
        self.speed = 1
        self.running = True
        self.elapsed = 0.0
        self.previous = self.game.snake.copy()

    def run(self) -> None:
        clock = pygame.time.Clock()
        try:
            while self.running:
                dt = min(clock.tick(60) / 1000, 0.25)
                for event in pygame.event.get():
                    self.handle_event(event)
                self.update(dt)
                self.draw()
                pygame.display.flip()
        finally:
            pygame.quit()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.WINDOWFOCUSLOST:
            if self.game.state is State.RUNNING:
                self.game.toggle_pause()
                self.sync_animation()
        elif event.type == pygame.KEYDOWN:
            self.handle_key(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(event.pos)

    def handle_key(self, key: int) -> None:
        if key in DIRECTIONS:
            self.game.turn(DIRECTIONS[key])
        elif key == pygame.K_ESCAPE:
            if self.game.state is State.READY:
                self.running = False
            else:
                self.game.reset()
                self.sync_animation()
        elif key == pygame.K_r:
            self.start()
        elif key in (pygame.K_SPACE, pygame.K_p):
            self.game.toggle_pause()
            self.sync_animation()
        elif key == pygame.K_RETURN:
            self.activate()
        elif key in (pygame.K_1, pygame.K_2, pygame.K_3):
            self.set_speed(key - pygame.K_1)

    def handle_click(self, position: tuple[int, int]) -> None:
        if self.game.state is State.RUNNING:
            return
        if self.view.play_button.collidepoint(position):
            self.activate()
        for i, rect in enumerate(self.view.speed_buttons):
            if rect.collidepoint(position):
                self.set_speed(i)

    def activate(self) -> None:
        if self.game.state is State.PAUSED:
            self.game.toggle_pause()
            self.sync_animation()
        elif self.game.state is not State.RUNNING:
            self.start()

    def start(self) -> None:
        self.game.start()
        self.sync_animation()

    def set_speed(self, speed: int) -> None:
        if self.game.state is not State.RUNNING:
            self.speed = speed
            self.sync_animation()

    def sync_animation(self) -> None:
        self.previous = self.game.snake.copy()
        self.elapsed = 0.0

    def update(self, dt: float) -> None:
        if self.game.state is not State.RUNNING:
            return
        self.elapsed += dt
        interval = 1 / SPEEDS[self.speed][1]
        while self.elapsed >= interval and self.game.state is State.RUNNING:
            self.previous = self.game.snake.copy()
            self.game.step()
            self.elapsed -= interval
        if self.game.score > self.best:
            self.best = self.game.score
            self.save_failed = not save_record(self.record_path, self.best)
        if self.game.state is not State.RUNNING:
            self.sync_animation()

    def draw(self) -> None:
        alpha = min(1.0, self.elapsed * SPEEDS[self.speed][1])
        self.view.draw(
            self.game,
            self.previous,
            alpha,
            self.best,
            self.speed,
            self.save_failed,
        )
