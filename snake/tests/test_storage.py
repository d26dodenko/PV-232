import pytest

from snake_game.storage import load_record, save_record


@pytest.mark.parametrize(
    "content",
    [
        "garbage",
        "{}",
        "[]",
        "null",
        '{"best": -1}',
        '{"best": true}',
        '{"best": "10"}',
        '{"best": 1.5}',
        '{"best": null}',
    ],
)
def test_corrupt_record_returns_zero(tmp_path, content):
    path = tmp_path / "best.json"
    path.write_text(content)
    assert load_record(path) == 0


def test_absent_record(tmp_path):
    assert load_record(tmp_path / "absent.json") == 0


def test_record_round_trip(tmp_path):
    path = tmp_path / "nested/best.json"
    assert save_record(path, 120)
    assert load_record(path) == 120
    assert save_record(path, 130)
    assert load_record(path) == 130
    assert not path.with_suffix(".tmp").exists()


def test_io_error_returns_false(tmp_path):
    blocker = tmp_path / "not_a_directory"
    blocker.write_text("x")
    assert not save_record(blocker / "best.json", 10)
    assert load_record(blocker) == 0
