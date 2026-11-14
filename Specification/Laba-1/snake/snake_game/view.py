import math
from typing import Optional

import pygame

from .model import Cell, SnakeGame, State

BACKGROUND = (13, 20, 28)
PANEL = (21, 32, 42)
TEXT = (234, 245, 241)
MUTED = (132, 157, 163)
MINT = (130, 235, 181)
CORAL = (255, 135, 122)
CELL = 28
ORIGIN = (44, 166)
SIZE = (760, 748)
SPEEDS = (("RELAXED", 6), ("CLASSIC", 10), ("QUICK", 15))


class View:
    def __init__(self, surface: pygame.Surface) -> None:
        self.surface = surface
        self.fonts = {
            size: pygame.font.SysFont("Arial", size, bold=size >= 28)
            for size in (14, 16, 20, 28, 42, 60)
        }
        self.play_button = pygame.Rect(250, 444, 260, 52)
        self.speed_buttons = [
            pygame.Rect(152 + i * 154, 374, 148, 42) for i in range(3)
        ]

    def text(
        self,
        value: str,
        size: int,
        position: tuple[int, int],
        color: tuple[int, int, int] = TEXT,
        center: bool = False,
    ) -> None:
        image = self.fonts[size].render(value, True, color)
        rect = image.get_rect()
        if center:
            rect.center = position
        else:
            rect.topleft = position
        self.surface.blit(image, rect)

    def button(
        self,
        rect: pygame.Rect,
        label: str,
        selected: bool = False,
    ) -> None:
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        color = MINT if selected else (38, 56, 65)
        if hovered and not selected:
            color = (51, 75, 83)
        pygame.draw.rect(self.surface, color, rect, border_radius=12)
        self.text(
            label,
            16,
            rect.center,
            BACKGROUND if selected else TEXT,
            center=True,
        )

    def draw(
        self,
        game: SnakeGame,
        previous: list[Cell],
        alpha: float,
        best: int,
        speed: int,
        save_failed: bool,
    ) -> None:
        self.surface.fill(BACKGROUND)
        self.text("MINT / ARCADE", 14, (44, 24), MINT)
        self.text("Snake", 42, (42, 44))
        self.text("A little focus. One more apple.", 16, (45, 100), MUTED)
        self._stat("SCORE", f"{game.score:03}", 456)
        self._stat("BEST", f"{best:03}", 596)
        self._board(game, previous, alpha)
        self.text("WASD / ARROWS  Move", 14, (44, 697), MUTED)
        self.text(
            "SPACE  Pause     R  Restart     ESC  Menu", 14, (350, 697), MUTED
        )
        status = (
            "Record stays in memory: file unavailable"
            if save_failed
            else f"{SPEEDS[speed][0]} / {SPEEDS[speed][1]} steps per second"
        )
        self.text(status, 14, (44, 724), CORAL if save_failed else MUTED)
        if game.state is not State.RUNNING:
            self._overlay(game, speed)

    def _stat(self, label: str, value: str, x: int) -> None:
        pygame.draw.rect(
            self.surface, PANEL, (x, 42, 120, 82), border_radius=16
        )
        self.text(label, 14, (x + 18, 53), MUTED)
        self.text(value, 28, (x + 18, 76), MINT)

    def _board(
        self,
        game: SnakeGame,
        previous: list[Cell],
        alpha: float,
    ) -> None:
        ox, oy = ORIGIN
        frame = pygame.Rect(
            ox - 8, oy - 8, game.width * CELL + 16, game.height * CELL + 16
        )
        pygame.draw.rect(self.surface, PANEL, frame, border_radius=16)
        for y in range(game.height):
            for x in range(game.width):
                pygame.draw.circle(
                    self.surface,
                    (39, 55, 63),
                    (ox + x * CELL + 14, oy + y * CELL + 14),
                    1,
                )
        self._food(game.food)
        for i in reversed(range(len(game.snake))):
            cell = game.snake[i]
            old = previous[min(i, len(previous) - 1)]
            x = ox + (old[0] + (cell[0] - old[0]) * alpha) * CELL
            y = oy + (old[1] + (cell[1] - old[1]) * alpha) * CELL
            color = MINT if i == 0 else (55, 164, 130)
            rect = pygame.Rect(round(x) + 2, round(y) + 2, CELL - 4, CELL - 4)
            pygame.draw.rect(self.surface, color, rect, border_radius=8)
            if i == 0:
                self._eyes(rect.center, game.direction.value)

    def _food(self, cell: Optional[Cell]) -> None:
        if cell is None:
            return
        x = ORIGIN[0] + cell[0] * CELL + CELL // 2
        y = ORIGIN[1] + cell[1] * CELL + CELL // 2
        radius = 8 + round(math.sin(pygame.time.get_ticks() / 220))
        pygame.draw.circle(self.surface, (70, 43, 45), (x, y), 13)
        pygame.draw.circle(self.surface, CORAL, (x, y), radius)
        pygame.draw.circle(self.surface, (255, 215, 192), (x - 2, y - 3), 2)

    def _eyes(self, center: tuple[int, int], direction: Cell) -> None:
        x, y = center
        dx, dy = direction
        for side in (-1, 1):
            position = (x + dx * 5 - dy * side * 5, y + dy * 5 + dx * side * 5)
            pygame.draw.circle(self.surface, BACKGROUND, position, 2)

    def _overlay(self, game: SnakeGame, speed: int) -> None:
        veil = pygame.Surface(SIZE, pygame.SRCALPHA)
        veil.fill((7, 14, 21, 185))
        self.surface.blit(veil, (0, 0))
        pygame.draw.rect(
            self.surface, PANEL, (116, 236, 528, 308), border_radius=24
        )
        titles = {
            State.READY: "Find your flow.",
            State.PAUSED: "Take a breath.",
            State.LOST: "One more round?",
            State.WON: "Perfect garden!",
        }
        self.text(titles[game.state], 42, (380, 286), center=True)
        subtitle = "Choose your pace. Make every turn count."
        if game.state in (State.LOST, State.WON):
            subtitle = f"Round complete / {game.score} points"
        self.text(subtitle, 16, (380, 334), MUTED, center=True)
        for i, rect in enumerate(self.speed_buttons):
            self.button(rect, SPEEDS[i][0], selected=i == speed)
        label = (
            "RESUME / SPACE"
            if game.state is State.PAUSED
            else "LET'S PLAY / ENTER"
        )
        self.button(self.play_button, label, selected=True)
        self.text(
            "1 / 2 / 3  Speed     ESC  Menu / Quit",
            14,
            (380, 520),
            MUTED,
            center=True,
        )
