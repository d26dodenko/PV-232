from random import Random

import pytest

from battleship import board as board_module
from battleship.board import Board, CELLS, FLEET, POSITIONS, Shot, place_fleet


def test_entire_fleet_fits_without_touching():
    arrangements = set()
    for seed in range(64):
        fleet = place_fleet(Random(seed))
        arrangements.add(frozenset(fleet))
        assert sorted(map(len, fleet), reverse=True) == list(FLEET)
        occupied = set()
        for ship in fleet:
            assert ship <= set(CELLS)
            xs, ys = zip(*ship)
            assert (len(set(xs)) == 1 and max(ys) - min(ys) + 1 == len(ship)) or (
                len(set(ys)) == 1 and max(xs) - min(xs) + 1 == len(ship)
            )
            assert not occupied.intersection(
                (x + dx, y + dy) for x, y in ship
                for dx in (-1, 0, 1) for dy in (-1, 0, 1)
            )
            occupied.update(ship)
    assert len(arrangements) == 64


def test_placement_revises_a_choice_that_would_block_the_last_ship(monkeypatch):
    blocked_choice = frozenset({(1, 0), (2, 0)})
    safe_choice = frozenset({(8, 9), (9, 9)})
    last_ship = frozenset({(0, 0)})
    monkeypatch.setattr(board_module, "FLEET", (2, 1))
    monkeypatch.setitem(POSITIONS, 2, [blocked_choice, safe_choice])
    monkeypatch.setitem(POSITIONS, 1, [last_ship])
    # При seed=0 первым рассматривается корабль рядом с (0, 0).
    assert place_fleet(Random(0)) == [safe_choice, last_ship]
    monkeypatch.setitem(POSITIONS, 2, [blocked_choice])
    with pytest.raises(ValueError, match="Флот не помещается"):
        place_fleet(Random(0))


def test_positions_include_ships_flush_with_right_and_bottom_edges():
    positions = POSITIONS[4]
    assert frozenset((9, y) for y in range(6, 10)) in positions
    assert frozenset((x, 9) for x in range(6, 10)) in positions
    assert len(set(POSITIONS[1])) == len(POSITIONS[1]) == 100


@pytest.mark.parametrize("cell", [(-1, 0), (0, -1), (10, 9), (9, 10)])
def test_out_of_bounds_shot_changes_nothing(cell):
    board = Board([frozenset({(0, 0)})])
    assert board.fire(cell) is None
    assert (board.shots, board.afloat) == ({}, 1)


@pytest.mark.parametrize("cell", [(9, 9), (0, 0)])
def test_corner_miss_and_repeat(cell):
    board = Board([frozenset({(2, 2)})])
    assert board.fire(cell) is Shot.MISS
    assert board.fire(cell) is None
    assert board.shots == {cell: Shot.MISS}
    assert board.afloat == 1


def test_sink_marks_whole_ship_and_counts_it_once():
    ship = frozenset({(8, 9), (9, 9)})
    board = Board([ship, frozenset({(0, 0)})])
    assert board.fire((9, 9)) is Shot.HIT
    assert board.fire((9, 9)) is None
    assert board.afloat == 2
    assert board.fire((8, 9)) is Shot.SUNK
    assert board.fire((8, 9)) is None
    assert board.afloat == 1
    assert board.shots == dict.fromkeys(ship, Shot.SUNK)
