FREE_DELIVERY_THRESHOLD = 5000.0
SHORT_DISTANCE_LIMIT_KM = 5.0
MIDDLE_DISTANCE_LIMIT_KM = 20.0

SHORT_DISTANCE_COST = 200.0
MIDDLE_DISTANCE_COST = 500.0
LONG_DISTANCE_EXTRA_COST_PER_KM = 30.0
PREMIUM_DISCOUNT_RATE = 0.5


def calculate_delivery_cost(
    order_amount: float,
    distance_km: float,
    is_premium: bool,
) -> float:
    """
    Рассчитать стоимость доставки для заказа.

    Бизнес-правила:
    1. order_amount и distance_km не могут быть отрицательными.
    2. Для заказов от 5000.0 доставка бесплатна.
    3. Для заказов дешевле 5000.0:
       - расстояние до 5 км включительно стоит 200.0;
       - расстояние больше 5 км и до 20 км включительно стоит 500.0;
       - расстояние больше 20 км стоит 500.0 плюс 30.0 за каждый км сверх 20.
    4. Premium-пользователь получает скидку 50% на рассчитанную стоимость доставки.

    Аргументы:
        order_amount: сумма заказа.
        distance_km: расстояние доставки в километрах.
        is_premium: признак premium-статуса покупателя.

    Возвращает:
        Итоговая стоимость доставки.

    Исключения:
        ValueError: если сумма заказа или расстояние отрицательные.
    """
    if order_amount < 0:
        raise ValueError("order_amount must be >= 0")

    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    if order_amount >= FREE_DELIVERY_THRESHOLD:
        cost = 0.0
    elif distance_km <= SHORT_DISTANCE_LIMIT_KM:
        cost = SHORT_DISTANCE_COST
    elif distance_km <= MIDDLE_DISTANCE_LIMIT_KM:
        cost = MIDDLE_DISTANCE_COST
    else:
        extra_distance = distance_km - MIDDLE_DISTANCE_LIMIT_KM
        cost = MIDDLE_DISTANCE_COST + extra_distance * LONG_DISTANCE_EXTRA_COST_PER_KM

    if is_premium:
        cost *= PREMIUM_DISCOUNT_RATE

    return cost
