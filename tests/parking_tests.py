import pytest

from parking import calculate_parking_cost


# Позитивные и граничные проверки тарифов парковки
@pytest.mark.parametrize(
    ("hours", "is_resident", "expected_cost"),
    [
        pytest.param(0, False, 0.0, id="нулевое-время"),
        pytest.param(0.25, False, 0.0, id="бесплатный-интервал-внутри"),
        pytest.param(0.49, False, 0.0, id="бесплатный-интервал-перед-границей"),
        pytest.param(0.5, False, 0.0, id="бесплатный-интервал-на-границе"),
        pytest.param(0.51, False, 150.0, id="базовый-тариф-после-границы"),
        pytest.param(1, False, 150.0, id="базовый-тариф-внутри-интервала"),
        pytest.param(2.99, False, 150.0, id="базовый-тариф-перед-границей"),
        pytest.param(3, False, 150.0, id="базовый-тариф-на-границе"),
        pytest.param(3.01, False, 150.5, id="почасовой-тариф-после-границы"),
        pytest.param(4, False, 200.0, id="почасовой-тариф-один-час-сверх"),
        pytest.param(10, False, 500.0, id="почасовой-тариф-стандартный-случай"),
        pytest.param(11.99, False, 599.5, id="почасовой-тариф-перед-максимумом"),
        pytest.param(12, False, 600.0, id="суточный-максимум-на-границе"),
        pytest.param(12.01, False, 600.0, id="суточный-максимум-после-границы"),
        pytest.param(24, False, 600.0, id="суточный-максимум-на-пределе-времени"),
        pytest.param(0.5, True, 0.0, id="резидент-бесплатный-интервал"),
        pytest.param(0.51, True, 105.0, id="резидент-скидка-на-базовый-тариф"),
        pytest.param(3, True, 105.0, id="резидент-базовый-тариф-на-границе"),
        pytest.param(4, True, 140.0, id="резидент-скидка-на-почасовой-тариф"),
        pytest.param(12, True, 420.0, id="резидент-скидка-на-суточный-максимум"),
        pytest.param(24, True, 420.0, id="резидент-максимум-на-пределе-времени"),
    ],
)
def test_calculate_parking_cost(hours, is_resident, expected_cost):
    assert calculate_parking_cost(hours, is_resident) == pytest.approx(expected_cost)


# Негативные проверки валидации входных данных
@pytest.mark.parametrize(
    ("hours", "is_resident", "expected_message"),
    [
        pytest.param(-0.01, False, "hours must be >= 0", id="отрицательное-время"),
        pytest.param(-5, True, "hours must be >= 0", id="отрицательное-время-резидент"),
        pytest.param(24.01, False, "hours must be <= 24", id="время-больше-суток"),
        pytest.param(100, True, "hours must be <= 24", id="время-больше-суток-резидент"),
    ],
)
def test_calculate_parking_cost_rejects_invalid_values(
    hours,
    is_resident,
    expected_message,
):
    with pytest.raises(ValueError, match=expected_message):
        calculate_parking_cost(hours, is_resident)