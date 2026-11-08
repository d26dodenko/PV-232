import pytest
from calculator import add, subtract, multiply, divide, classify_number


def test_add():
    assert add(2, 3) == 5


def test_subtract():
    assert subtract(5, 2) == 3


def test_multiply():
    assert multiply(3, 4) == 12


def test_divide():
    assert divide(10, 2) == 5


def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(1, 0)


@pytest.mark.parametrize("x,expected", [(5, "Positive"), (0, "Zero"), (-3, "Negative")])
def test_classify_number(x, expected):
    assert classify_number(x) == expected