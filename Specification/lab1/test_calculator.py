import pytest
from calculator import add, subtract, multiply, divide, power, square_root

def test_add_positive():
    assert add(5, 3) == 8

def test_add_negative():
    assert add(-5, -3) == -8

def test_add_zero():
    assert add(0, 0) == 0

def test_subtract_positive():
    assert subtract(10, 5) == 5

def test_subtract_to_negative():
    assert subtract(5, 10) == -5

def test_multiply_positive():
    assert multiply(4, 5) == 20

def test_multiply_by_zero():
    assert multiply(100, 0) == 0

def test_multiply_negative():
    assert multiply(-4, 5) == -20

def test_divide_positive():
    assert divide(20, 4) == 5

def test_divide_float():
    assert divide(5, 2) == 2.5

def test_divide_by_zero():
    with pytest.raises(ValueError, match="Деление на ноль"):
        divide(10, 0)

def test_power_positive():
    assert power(3, 2) == 9

def test_power_zero():
    assert power(10, 0) == 1

def test_power_negative_exp():
    assert power(2, -2) == 0.25

def test_power_zero_negative_exp():
    with pytest.raises(ValueError, match="Ноль нельзя возводить"):
        power(0, -5)

def test_sqrt_positive():
    assert square_root(9) == 3.0

def test_sqrt_zero():
    assert square_root(0) == 0.0

def test_sqrt_negative():
    with pytest.raises(ValueError, match="Корень из отрицательного"):
        square_root(-4)