import pytest
from bike_rental import calculate_bike_rental


def test_zero_hours_raises_error():
    with pytest.raises(ValueError):
        calculate_bike_rental(0, "city", False)


def test_negative_hours_raises_error():
    with pytest.raises(ValueError):
        calculate_bike_rental(-1, "city", False)


def test_unknown_bike_type_raises_error():
    with pytest.raises(ValueError):
        calculate_bike_rental(1, "scooter", False)


def test_city_bike_one_hour():
    # Первый час по полной ставке
    assert calculate_bike_rental(1, "city", False) == pytest.approx(150.0)


def test_city_bike_half_hour():
    # Дробный час: 150 * 0.5
    assert calculate_bike_rental(0.5, "city", False) == pytest.approx(75.0)


def test_city_bike_two_hours():
    # 150 + 1 * 120
    assert calculate_bike_rental(2, "city", False) == pytest.approx(270.0)


def test_city_bike_three_hours():
    # 150 + 2 * 120
    assert calculate_bike_rental(3, "city", False) == pytest.approx(390.0)


def test_city_bike_four_hours():
    # 150 + 2 * 120 + 1 * 90
    assert calculate_bike_rental(4, "city", False) == pytest.approx(480.0)


def test_mountain_bike_two_hours():
    # 250 + 1 * 200
    assert calculate_bike_rental(2, "mountain", False) == pytest.approx(450.0)


def test_electric_bike_two_hours():
    # 400 + 1 * 320
    assert calculate_bike_rental(2, "electric", False) == pytest.approx(720.0)


def test_member_discount_on_city_bike():
    # 270 * 0.85
    assert calculate_bike_rental(2, "city", True) == pytest.approx(229.5)


def test_member_discount_on_long_electric_rental():
    # (400 + 2*320 + 1*240) * 0.85
    assert calculate_bike_rental(4, "electric", True) == pytest.approx(1088.0)