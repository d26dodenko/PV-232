# test_delivery.py

import pytest
from delivery import calculate_delivery_cost


# --- Positive and boundary tests ---

def test_free_delivery_from_5000():
    assert calculate_delivery_cost(5000, 10, False) == 0.0


def test_paid_delivery_below_5000():
    assert calculate_delivery_cost(4999.99, 10, False) == 500.0


def test_short_distance():
    assert calculate_delivery_cost(1000, 5, False) == 200.0


def test_middle_distance():
    assert calculate_delivery_cost(1000, 20, False) == 500.0


def test_long_distance():
    assert calculate_delivery_cost(1000, 30, False) == 800.0


def test_premium_discount():
    assert calculate_delivery_cost(1000, 10, True) == 250.0


def test_premium_with_free_delivery():
    assert calculate_delivery_cost(5000, 10, True) == 0.0


def test_premium_with_long_distance():
    assert calculate_delivery_cost(1000, 30, True) == 400.0


def test_distance_just_above_5():
    assert calculate_delivery_cost(1000, 5.1, False) == 500.0


def test_distance_just_above_20():
    assert calculate_delivery_cost(1000, 20.1, False) == pytest.approx(503.0)


def test_zero_order_amount_short_distance():
    assert calculate_delivery_cost(0, 3, False) == 200.0


def test_zero_distance():
    assert calculate_delivery_cost(1000, 0, False) == 200.0


# --- Negative tests ---

def test_negative_order_amount():
    with pytest.raises(ValueError):
        calculate_delivery_cost(-1, 10, False)


def test_negative_distance():
    with pytest.raises(ValueError):
        calculate_delivery_cost(1000, -1, False)