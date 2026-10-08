FREE_LIMIT_HOURS = 0.5
BASE_LIMIT_HOURS = 3.0
MAX_HOURS = 24.0

BASE_COST = 150.0
EXTRA_COST_PER_HOUR = 50.0
DAILY_MAX_COST = 600.0
RESIDENT_DISCOUNT_RATE = 0.3


def calculate_parking_cost(
    hours: float,
    is_resident: bool,
) -> float:
    """
    Рассчитать стоимость парковки.

    Бизнес-правила:
    1. hours не может быть отрицательным и не может превышать 24.
    2. Парковка до 0.5 часа включительно бесплатна.
    3. Для парковки дольше 0.5 часа:
       - до 3 часов включительно стоит 150.0;
       - больше 3 часов стоит 150.0 плюс 50.0 за каждый час сверх 3.
    4. Стоимость до скидки не может превышать 600.0 (суточный максимум).
    5. Резидент получает скидку 30% на рассчитанную стоимость.

    Аргументы:
        hours: время парковки в часах.
        is_resident: признак резидента.

    Возвращает:
        Итоговая стоимость парковки.

    Исключения:
        ValueError: если время отрицательное или больше 24 часов.
    """
    if hours < 0:
        raise ValueError("hours must be >= 0")

    if hours > MAX_HOURS:
        raise ValueError("hours must be <= 24")

    if hours <= FREE_LIMIT_HOURS:
        cost = 0.0
    elif hours <= BASE_LIMIT_HOURS:
        cost = BASE_COST
    else:
        extra_hours = hours - BASE_LIMIT_HOURS
        cost = BASE_COST + extra_hours * EXTRA_COST_PER_HOUR

    cost = min(cost, DAILY_MAX_COST)

    if is_resident:
        cost *= 1 - RESIDENT_DISCOUNT_RATE

    return cost