# test_delivery.py

import pytest
from delivery import calculate_delivery_cost


def test_free_delivery_from_5000():
    # Сумма 5000 — доставка бесплатная
    assert calculate_delivery_cost(5000, 10, False) == 0.0


def test_paid_delivery_below_5000_boundary():
    # Сумма 4999.99 — доставка платная
    assert calculate_delivery_cost(4999.99, 10, False) == 500.0


def test_short_distance_zero():
    # Нулевая дистанция — тариф 200
    assert calculate_delivery_cost(1000, 0, False) == 200.0


def test_short_distance_boundary_5():
    # Ровно 5 км — тариф 200
    assert calculate_delivery_cost(1000, 5, False) == 200.0


def test_middle_distance_just_above_5():
    # 5.01 км — переход в средний тариф 500
    assert calculate_delivery_cost(1000, 5.01, False) == 500.0


def test_middle_distance_boundary_20():
    # Ровно 20 км — тариф 500
    assert calculate_delivery_cost(1000, 20, False) == 500.0


def test_long_distance_just_above_20():
    # 21 км — 500 + (21 - 20) * 30 = 530
    assert calculate_delivery_cost(1000, 21, False) == 530.0


def test_long_distance_30():
    # 30 км — 500 + 10 * 30 = 800
    assert calculate_delivery_cost(1000, 30, False) == 800.0


def test_premium_discount_middle():
    # Premium — скидка 50%: 500 * 0.5 = 250
    assert calculate_delivery_cost(1000, 10, True) == 250.0


def test_premium_discount_long():
    # Premium — скидка 50%: 800 * 0.5 = 400
    assert calculate_delivery_cost(1000, 30, True) == 400.0


def test_premium_free_delivery():
    # Premium, но сумма >= 5000 — доставка всё равно 0
    assert calculate_delivery_cost(5000, 100, True) == 0.0


def test_premium_short_distance():
    # Premium — скидка 50%: 200 * 0.5 = 100
    assert calculate_delivery_cost(1000, 5, True) == 100.0


def test_negative_order_amount():
    # Отрицательная сумма — ошибка
    with pytest.raises(ValueError):
        calculate_delivery_cost(-1, 10, False)


def test_negative_distance():
    # Отрицательное расстояние — ошибка
    with pytest.raises(ValueError):
        calculate_delivery_cost(1000, -1, False)


def test_zero_order_amount():
    # Нулевая сумма допустима, доставка платная
    assert calculate_delivery_cost(0, 10, False) == 500.0
