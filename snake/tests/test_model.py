import random

import pytest

from snake_game.model import Direction, SnakeGame, State


@pytest.fixture
def game():
    model = SnakeGame(8, 6, random.Random(42))
    model.start()
    model.food = (0, 0)
    return model


@pytest.mark.parametrize("width,height", [(3, 6), (8, 1), (0, 0), (-1, 8)])
def test_rejects_small_boards(width, height):
    with pytest.raises(ValueError):
        SnakeGame(width, height)


def test_initial_state_and_default_rng():
    game = SnakeGame()
    assert game.state is State.READY
    assert len(game.snake) == 3
    assert game.food not in game.snake
    assert game.score == 0


@pytest.mark.parametrize(
    "direction,delta",
    [
        (Direction.UP, (0, -1)),
        (Direction.DOWN, (0, 1)),
        (Direction.RIGHT, (1, 0)),
    ],
)
def test_direction_and_movement(game, direction, delta):
    old = game.snake[0]
    game.turn(direction)
    game.step()
    assert game.snake[0] == (old[0] + delta[0], old[1] + delta[1])
    assert len(game.snake) == 3
    assert game.score == 0


def test_left_turn_after_up(game):
    game.turn(Direction.UP)
    game.step()
    assert game.turn(Direction.LEFT)
    game.step()
    assert game.snake[0] == (3, 2)


def test_reverse_rejected(game):
    assert not game.turn(Direction.LEFT)
    game.step()
    assert game.direction is Direction.RIGHT


def test_two_turns_before_tick_do_not_reverse(game):
    assert game.turn(Direction.UP)
    assert not game.turn(Direction.LEFT)
    game.step()
    assert game.direction is Direction.UP
    assert game.turn(Direction.LEFT)


def test_same_direction_does_not_consume_turn(game):
    assert not game.turn(Direction.RIGHT)
    assert game.turn(Direction.UP)


@pytest.mark.parametrize(
    "state", [State.READY, State.PAUSED, State.LOST, State.WON]
)
def test_inactive_states_do_not_move_or_turn(game, state):
    game.state = state
    before = game.snake.copy()
    assert not game.turn(Direction.UP)
    game.step()
    assert game.snake == before
    assert game.state is state


def test_pause_resume(game):
    game.toggle_pause()
    assert game.state is State.PAUSED
    game.toggle_pause()
    assert game.state is State.RUNNING
    game.state = State.LOST
    game.toggle_pause()
    assert game.state is State.LOST


def test_growth_and_score(game):
    game.food = (5, 3)
    game.step()
    assert game.snake[0] == (5, 3)
    assert len(game.snake) == 4
    assert game.score == 10
    assert game.food not in game.snake
    game.food = (6, 3)
    game.step()
    assert game.score == 20


def test_food_always_free_and_within_board(game):
    for _ in range(500):
        x, y = game.generate_food()
        assert 0 <= x < game.width
        assert 0 <= y < game.height
        assert (x, y) not in game.snake


def test_food_last_free_and_full_board(game):
    game.snake = [(x, y) for y in range(6) for x in range(8)]
    game.snake.remove((2, 2))
    assert game.generate_food() == (2, 2)
    game.snake.append((2, 2))
    assert game.generate_food() is None


@pytest.mark.parametrize(
    "head,direction",
    [
        ((7, 3), Direction.RIGHT),
        ((0, 3), Direction.LEFT),
        ((4, 0), Direction.UP),
        ((4, 5), Direction.DOWN),
    ],
)
def test_all_walls(game, head, direction):
    game.snake = [head]
    game.pending_direction = direction
    before = game.snake.copy()
    game.step()
    assert game.state is State.LOST
    assert game.snake == before
    assert game.score == 0


def test_self_collision(game):
    game.snake = [(3, 2), (3, 3), (4, 3), (4, 2), (4, 1)]
    game.step()
    assert game.state is State.LOST


def test_can_enter_vacating_tail(game):
    game.snake = [(3, 2), (3, 3), (4, 3), (4, 2)]
    game.step()
    assert game.state is State.RUNNING
    assert game.snake == [(4, 2), (3, 2), (3, 3), (4, 3)]


def test_last_food_wins():
    game = SnakeGame(4, 2)
    game.start()
    game.snake = [(2, 0), (1, 0), (0, 0), (0, 1), (1, 1), (2, 1), (3, 1)]
    game.food = (3, 0)
    game.step()
    assert game.state is State.WON
    assert game.food is None
    assert game.score == 10
    assert len(game.snake) == 8
    game.step()
    assert len(game.snake) == 8


def test_restart_clears_round(game):
    game.food = (5, 3)
    game.step()
    game.turn(Direction.UP)
    game.state = State.LOST
    game.start()
    assert game.state is State.RUNNING
    assert game.snake == [(4, 3), (3, 3), (2, 3)]
    assert game.score == 0
    assert game.direction is Direction.RIGHT
    assert game.pending_direction is Direction.RIGHT
    assert not game.turn_pending
    assert game.food not in game.snake


def test_seed_reproducible():
    first = SnakeGame(rng=random.Random(123))
    second = SnakeGame(rng=random.Random(123))
    assert first.food == second.food


def test_random_play_invariants():
    for seed in range(30):
        game = SnakeGame(8, 6, random.Random(seed))
        game.start()
        inputs = random.Random(seed + 100)
        for _ in range(100):
            game.turn(inputs.choice(list(Direction)))
            game.step()
            assert len(game.snake) == len(set(game.snake))
            assert all(0 <= x < 8 and 0 <= y < 6 for x, y in game.snake)
            assert len(game.snake) == 3 + game.score // 10
            assert game.food not in game.snake
            if game.state is State.LOST:
                break
