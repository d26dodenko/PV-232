import pytest

from delivery import calculate_delivery_cost


# Позитивные и граничные проверки основных тарифов доставки.
@pytest.mark.parametrize(
    ("order_amount", "distance_km", "is_premium", "expected_cost"),
    [
        pytest.param(0, 0, False, 200.0, id="нулевой-заказ-и-нулевое-расстояние"),
        pytest.param(1, 0, False, 200.0, id="нулевое-расстояние-с-платным-заказом"),
        pytest.param(1000, 1, False, 200.0, id="короткая-доставка-внутри-интервала"),
        pytest.param(1000, 4.99, False, 200.0, id="короткая-доставка-перед-границей"),
        pytest.param(1000, 5, False, 200.0, id="короткая-доставка-на-границе"),
        pytest.param(1000, 5.01, False, 500.0, id="средняя-доставка-после-границы"),
        pytest.param(1000, 10, False, 500.0, id="средняя-доставка-внутри-интервала"),
        pytest.param(1000, 19.99, False, 500.0, id="средняя-доставка-перед-границей"),
        pytest.param(1000, 20, False, 500.0, id="средняя-доставка-на-границе"),
        pytest.param(1000, 20.01, False, 500.3, id="дальняя-доставка-после-границы"),
        pytest.param(1000, 21, False, 530.0, id="дальняя-доставка-за-один-км-сверх"),
        pytest.param(1000, 30, False, 800.0, id="дальняя-доставка-стандартный-случай"),
        pytest.param(1000, 100, False, 2900.0, id="дальняя-доставка-большое-расстояние"),
        pytest.param(4999.99, 10, False, 500.0, id="платная-доставка-перед-порогом"),
        pytest.param(5000, 0, False, 0.0, id="бесплатная-доставка-на-пороге-ноль-км"),
        pytest.param(5000, 10, False, 0.0, id="бесплатная-доставка-на-пороге"),
        pytest.param(5000.01, 100, False, 0.0, id="бесплатная-доставка-выше-порога"),
        pytest.param(8000, 50, False, 0.0, id="бесплатная-доставка-дальний-адрес"),
        pytest.param(1000, 5, True, 100.0, id="премиум-скидка-на-короткую-доставку"),
        pytest.param(1000, 10, True, 250.0, id="премиум-скидка-на-среднюю-доставку"),
        pytest.param(1000, 20.01, True, 250.15, id="премиум-скидка-на-дробную-дальнюю-доставку"),
        pytest.param(1000, 30, True, 400.0, id="премиум-скидка-на-дальнюю-доставку"),
        pytest.param(5000, 30, True, 0.0, id="премиум-бесплатная-доставка-остается-бесплатной"),
    ],
)
def test_calculate_delivery_cost(
    order_amount,
    distance_km,
    is_premium,
    expected_cost,
):
    assert (
        calculate_delivery_cost(order_amount, distance_km, is_premium)
        == pytest.approx(expected_cost)
    )


# Негативные проверки валидации входных данных.
@pytest.mark.parametrize(
    ("order_amount", "distance_km", "is_premium", "expected_message"),
    [
        pytest.param(-0.01, 10, False, "order_amount must be >= 0", id="отрицательная-сумма"),
        pytest.param(-100, 10, True, "order_amount must be >= 0", id="отрицательная-сумма-premium"),
        pytest.param(1000, -0.01, False, "distance_km must be >= 0", id="отрицательное-расстояние"),
        pytest.param(1000, -100, True, "distance_km must be >= 0", id="отрицательное-расстояние-premium"),
    ],
)
def test_calculate_delivery_cost_rejects_negative_values(
    order_amount,
    distance_km,
    is_premium,
    expected_message,
):
    with pytest.raises(ValueError, match=expected_message):
        calculate_delivery_cost(order_amount, distance_km, is_premium)
