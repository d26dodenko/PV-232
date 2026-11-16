from random import Random
from unittest.mock import Mock

import pytest

from snake.body import Direction
from snake.game import SnakeGame, Status

def game_with_food(*cells):
  rng = Mock(spec=Random)
  placements = iter(cells)

  def choose(free):
    cell = next(placements)
    assert cell in free
    return cell

  rng.choice.side_effect = choose
  return SnakeGame(4, 2, rng)


def test_start_and_first_step():
  game = SnakeGame(rng=Random(1))
  assert game.snake.body == ((10, 8), (9, 8), (8, 8))
  assert game.food not in game.snake.body
  assert game.status is Status.PLAYING
  game.step()
  assert game.snake.body == ((11, 8), (10, 8), (9, 8))
  assert game.score == 0


@pytest.mark.parametrize(("width", "height"), [(3, 2), (4, 1)])
def test_board_too_small(width, height):
  with pytest.raises(ValueError, match="at least 4 by 2"):
    SnakeGame(width, height)


def test_reverse_then_two_turns_before_one_step():
  game = game_with_food((0, 0))
  game.turn(Direction.LEFT)
  game.turn(Direction.UP)
  game.turn(Direction.LEFT)
  game.step()
  assert game.snake.body == ((2, 0), (2, 1), (1, 1))
  game.turn(Direction.LEFT)
  game.step()
  assert game.snake.body[0] == (1, 0)


def test_growth_score_and_new_food():
  game = game_with_food((3, 1), (3, 0))
  game.step()
  assert game.snake.body == ((3, 1), (2, 1), (1, 1), (0, 1))
  assert game.score == 1
  assert game.food == (3, 0)


@pytest.mark.parametrize("turns", [
  (Direction.RIGHT, Direction.RIGHT),
  (Direction.DOWN,),
  (Direction.UP, Direction.UP),
  (Direction.UP, Direction.LEFT, Direction.LEFT, Direction.LEFT),
])
def test_all_walls_stop_the_game(turns):
  game = game_with_food((3, 0))
  for direction in turns:
    game.turn(direction)
    last_body = game.snake.body
    game.step()

  assert game.status is Status.LOST
  assert game.snake.body == last_body
  game.turn(Direction.RIGHT)
  game.step()
  assert game.status is Status.LOST
  assert game.snake.body == last_body


def test_vacated_tail_is_safe():
  game = game_with_food((3, 1), (0, 0))
  for direction in (Direction.RIGHT, Direction.UP, Direction.LEFT):
    game.turn(direction)
    game.step()

  tail = game.snake.body[-1]
  game.turn(Direction.DOWN)
  game.step()
  assert game.snake.body[0] == tail
  assert len(set(game.snake.body)) == 4
  assert game.status is Status.PLAYING


def test_hit_occupied_body():
  game = game_with_food((3, 1), (3, 0), (2, 0), (1, 0))
  for direction in (Direction.RIGHT, Direction.UP, Direction.LEFT):
    game.turn(direction)
    game.step()

  last_body = game.snake.body
  game.turn(Direction.DOWN)
  game.step()
  assert game.status is Status.LOST
  assert game.snake.body == last_body
  assert game.score == 3


def test_last_free_cell_wins_and_restart_clears_the_round():
  game = game_with_food((3, 1), (3, 0), (2, 0), (1, 0), (0, 0), (1, 0))
  for direction in (Direction.RIGHT, Direction.UP, Direction.LEFT,
                    Direction.LEFT, Direction.LEFT):
    game.turn(direction)
    game.step()

  assert game.status is Status.WON
  assert game.food is None
  assert game.score == 5
  full_board = game.snake.body
  assert len(set(full_board)) == game.width * game.height
  game.step()
  assert game.snake.body == full_board
  game.restart()
  assert game.status is Status.PLAYING
  assert game.snake.body == ((2, 1), (1, 1), (0, 1))
  assert game.snake.direction is Direction.RIGHT
  assert game.score == 0
  assert game.food == (1, 0)
