"""Окно Pygame, управление мышью и отрисовка двух полей."""

from random import Random

import pygame as pg

from .board import Board, CELLS, SIZE, Shot
from .game import Game, Side

WINDOW = (960, 632)
TILE = 32
LETTERS = "АБВГДЕЖЗИК"
HOME = pg.Rect(82, 176, SIZE * TILE, SIZE * TILE)
TARGET = pg.Rect(558, 176, SIZE * TILE, SIZE * TILE)
RESTART = pg.Rect(748, 31, 174, 38)
CPU_DELAY = 450

NAVY = "#10222e"
PANEL = "#192f3c"
SEA = "#203a49"
GRID = "#395462"
TEXT = "#f1f4ea"
MUTED = "#b0c2c7"
TEAL = "#7bd5c2"
HULL = "#65a99f"
AMBER = "#ffcf78"
CORAL = "#ff9780"


class App:
    def __init__(self, screen: pg.Surface, rng: Random):
        self.screen = screen
        self.rng = rng
        self.game = Game.new(rng)
        self.cpu_due = 0
        self.title = pg.font.SysFont("dejavusans,arial", 38, bold=True)
        self.heading = pg.font.SysFont("dejavusans,arial", 21, bold=True)
        self.small = pg.font.SysFont("dejavusans,arial", 16)

    def handle(self, event: pg.event.Event, now: int) -> bool:
        if event.type == pg.QUIT:
            return False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                return False
            if event.key == pg.K_r:
                self.game = Game.new(self.rng)
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if RESTART.collidepoint(event.pos):
                self.game = Game.new(self.rng)
            elif TARGET.collidepoint(event.pos) and self.game.turn is Side.PLAYER:
                x, y = event.pos
                self.game.player_shot(((x - TARGET.x) // TILE, (y - TARGET.y) // TILE))
                if self.game.turn is Side.COMPUTER:
                    self.cpu_due = now + CPU_DELAY
        return True

    def update(self, now: int) -> None:
        if self.game.winner is None and self.game.turn is Side.COMPUTER and now >= self.cpu_due:
            self.game.computer_shot()
            self.cpu_due = now + CPU_DELAY

    def label(self, text, font, color, x, y, anchor="topleft"):
        image = font.render(text, True, color)
        self.screen.blit(image, image.get_rect(**{anchor: (x, y)}))

    def draw_board(self, board: Board, area: pg.Rect, own: bool) -> None:
        name = "Ваш флот" if own else "Флот противника"
        self.label(name, self.heading, TEXT, area.left, 114)
        self.label(f"На плаву: {board.afloat}", self.small, MUTED, area.right, 120, "topright")
        for i, letter in enumerate(LETTERS):
            self.label(letter, self.small, MUTED, area.x + i * TILE + TILE // 2,
                       area.top - 14, "center")
            self.label(str(i + 1), self.small, MUTED, area.left - 16,
                       area.y + i * TILE + TILE // 2, "center")

        self.screen.fill(GRID, area)
        for x, y in CELLS:
            tile = pg.Rect(area.x + x * TILE, area.y + y * TILE, TILE, TILE)
            pg.draw.rect(self.screen, SEA, tile.inflate(-1, -1))
            mark = board.shots.get((x, y))
            if mark is not None:
                self.draw_mark(mark, tile)
            elif own and (x, y) in board.ship_at:
                pg.draw.rect(self.screen, HULL, tile.inflate(-5, -5), border_radius=3)

    def draw_mark(self, mark: Shot, tile: pg.Rect) -> None:
        if mark is Shot.MISS:
            pg.draw.circle(self.screen, MUTED, tile.center, 4)
            return
        color = CORAL if mark is Shot.SUNK else AMBER
        arm = tile.width // 4
        x, y = tile.center
        pg.draw.line(self.screen, color, (x - arm, y - arm), (x + arm, y + arm), 2)
        pg.draw.line(self.screen, color, (x - arm, y + arm), (x + arm, y - arm), 2)
        if mark is Shot.SUNK:
            pg.draw.rect(self.screen, color, tile.inflate(-4, -4), 1)

    def draw(self) -> None:
        self.screen.fill(NAVY)
        self.label("Морской бой", self.title, TEXT, 38, 21)
        self.label("Одиночная игра против компьютера", self.small, MUTED, 40, 70)
        pg.draw.rect(self.screen, GRID, RESTART, 1, border_radius=6)
        self.label("Новая партия · R", self.small, TEXT, *RESTART.center, "center")
        pg.draw.line(self.screen, GRID, (38, 99), (922, 99))
        self.draw_board(self.game.player, HOME, own=True)
        self.draw_board(self.game.enemy, TARGET, own=False)
        pg.draw.rect(self.screen, HULL, (85, 515, 12, 12), border_radius=2)
        self.label("Корабль", self.small, MUTED, 107, 511)
        for x, text, mark in [(274, "Мимо", Shot.MISS), (558, "Попадание", Shot.HIT),
                              (740, "Потоплен", Shot.SUNK)]:
            self.draw_mark(mark, pg.Rect(x, 511, 20, 20))
            self.label(text, self.small, MUTED, x + 25, 511)

        if self.game.winner is not None:
            status = "Вы победили!" if self.game.winner is Side.PLAYER else "Победил компьютер"
        else:
            status = "Ваш ход" if self.game.turn is Side.PLAYER else "Ход компьютера"
        detail = "Для выстрела нажмите на клетку правого поля."
        if self.game.last_shot:
            side, (x, y), result = self.game.last_shot
            detail = f"{side.value} · {LETTERS[x]}{y + 1} — {result.value}."
        pg.draw.rect(self.screen, PANEL, (38, 550, 884, 65), border_radius=6)
        pg.draw.rect(self.screen, TEAL, (38, 560, 3, 45), border_radius=1)
        self.label(status, self.heading, TEAL, 58, 554)
        self.label(detail, self.small, TEXT, 58, 586)

    def run(self) -> None:
        clock = pg.time.Clock()
        while True:
            now = pg.time.get_ticks()
            for event in pg.event.get():
                if not self.handle(event, now):
                    return
            self.update(now)
            self.draw()
            pg.display.flip()
            clock.tick(60)


def main() -> None:
    pg.display.init()
    pg.font.init()
    try:
        screen = pg.display.set_mode(WINDOW)
        pg.display.set_caption("Морской бой")
        App(screen, Random()).run()
    finally:
        pg.quit()
