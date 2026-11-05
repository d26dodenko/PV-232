from random import Random

import pytest

from battleship.board import Board, CELLS, Shot
from battleship.game import Game, Side


def test_hit_repeat_sink_and_miss_set_the_turn():
    enemy = Board([frozenset({(0, 0), (1, 0)}), frozenset({(9, 9)})])
    game = Game(Board([frozenset({(0, 0)})]), enemy, Random(1))
    game.computer_shot()
    assert not game.player.shots
    game.player_shot((0, 0))
    assert game.last_shot == (Side.PLAYER, (0, 0), Shot.HIT)
    game.player_shot((0, 0))
    assert game.turn is Side.PLAYER
    game.player_shot((1, 0))
    assert game.turn is Side.PLAYER and game.winner is None
    assert enemy.afloat == 1
    game.player_shot((2, 0))
    assert game.turn is Side.COMPUTER
    game.player_shot((9, 9))
    assert (9, 9) not in enemy.shots


def test_last_player_hit_ends_game_before_computer_can_reply():
    game = Game(Board([frozenset({(5, 5)})]), Board([frozenset({(0, 0)})]), Random(1))
    game.player_shot((0, 0))
    assert game.winner is Side.PLAYER
    game.computer_shot()
    game.player_shot((5, 5))
    assert not game.player.shots
    assert game.last_shot == (Side.PLAYER, (0, 0), Shot.SUNK)


def test_computer_can_hit_twice_and_win():
    player = Board([frozenset({(0, 0), (1, 0)})])
    for cell in CELLS:
        if cell not in player.ship_at:
            player.fire(cell)
    game = Game(player, Board([frozenset({(5, 5)})]), Random(2))
    game.player_shot((0, 0))
    game.computer_shot()
    assert game.turn is Side.COMPUTER and game.winner is None
    assert game.last_shot[2] is Shot.HIT
    game.computer_shot()
    assert game.winner is Side.COMPUTER and game.last_shot[2] is Shot.SUNK
    game.player_shot((5, 5))
    assert game.enemy.shots == {(0, 0): Shot.MISS}


@pytest.mark.parametrize("seed", [0, 42, 232])
def test_full_match_finishes_without_repeated_shots(seed):
    game = Game.new(Random(seed))
    targets = iter(CELLS)
    for _ in range(2 * len(CELLS)):
        if game.turn is Side.PLAYER:
            game.player_shot(next(targets))
        else:
            before = len(game.player.shots)
            game.computer_shot()
            assert len(game.player.shots) == before + 1
        if game.winner is not None:
            break
    assert game.winner is not None
    defeated = game.enemy if game.winner is Side.PLAYER else game.player
    assert defeated.afloat == 0
