def calculate_bike_rental(hours: float, bike_type: str, is_member: bool) -> float:
    """
    Расчёт стоимости аренды велосипеда.

    Бизнес-правила:
    1. hours должен быть > 0, иначе ValueError.
    2. bike_type должен быть одним из: 'city', 'mountain', 'electric',
       иначе ValueError.
    3. Базовые ставки за первый час:
       - city: 150 руб.
       - mountain: 250 руб.
       - electric: 400 руб.
    4. Каждый следующий час до 3 включительно — 80% от базовой ставки.
    5. Каждый час свыше 3 — 60% от базовой ставки.
    6. Для участников клуба (is_member=True) — скидка 15% на итог.
    7. Результат округляется до 2 знаков.
    """
    if hours <= 0:
        raise ValueError("hours must be > 0")

    rates = {
        "city": 150.0,
        "mountain": 250.0,
        "electric": 400.0,
    }
    if bike_type not in rates:
        raise ValueError("unknown bike_type: " + str(bike_type))

    rate = rates[bike_type]

    if hours <= 1:
        total = rate * hours
    elif hours <= 3:
        total = rate + (hours - 1) * rate * 0.8
    else:
        total = rate + 2 * rate * 0.8 + (hours - 3) * rate * 0.6

    if is_member:
        total *= 0.85

    return round(total, 2)