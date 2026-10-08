# Лабораторная работа №1 

# <br> Составление тест-кейсов для готового кода. Качество ПО и место тестирования в жизненном цикле
## Цель работы

Сформировать системное представление о качестве ПО и роли тестирования в жизненном цикле; приобрести практические навыки проектирования тест-кейсов и написания автотестов на основе готового кода.

### 1. Анализ исходного кода

**Функция:**

```python
calculate_delivery_cost(order_amount: float, distance_km: float, is_premium: bool) -> float
```

**Входные параметры**

|Параметр | Тип | Допустимые значения | Недопустимые значения |
|---------|-----|---------------------|----------------------------|
|order_amount| float | >= 0 | < 0 |
| distance_km |	float |	>= 0 |	< 0|
|is_premium |	bool |	True, False |	не проверяется кодом |

**Выходной параметр** 
float — стоимость доставки. 

**Бизнес-правила**
1. Если order_amount < 0 → ValueError.
2. Если distance_km < 0 → ValueError.
3. Если order_amount >= 5000 → доставка бесплатна, cost = 0.0.
4. Иначе стоимость зависит от расстояния:
    - distance_km <= 5 → 200.0
    - 5 < distance_km <= 20 → 500.0
    - distance_km > 20 → 500.0 + (distance_km - 20) * 30.0
5. Если is_premium = True → скидка 50% на стоимость доставки.
6. Если доставка уже бесплатна (0.0), скидка не меняет результат.

**Граничные значения**

    - order_amount: 0, 4999.99, 5000, > 5000
    - distance_km: 0, 5, 5.01, 20, 20.01, 21, > 20
    - is_premium: False, True

### 2. Тест-кейсы
|ID	| Название |	Входные данные |	Ожидаемый результат	| Тип |
|---|----------|-------------------|------------------------|-----|
|TC-01 |	Бесплатная доставка при сумме 5000 |	order_amount=5000, distance_km=10, is_premium=False |	0.0 |	Позитивный, граничный |
|TC-02 |	Платная доставка чуть ниже 5000	 |order_amount=4999.99, distance_km=10, is_premium=False |	500.0 |	Граничный |
|TC-03 |	Нулевая дистанция |	order_amount=1000, distance_km=0, is_premium=False |	200.0 |	Граничный |
|TC-04 |	Граница короткой дистанции 5 км |	order_amount=1000, distance_km=5, is_premium=False |	200.0 |	Граничный |
|TC-05 |	Переход от короткой к средней дистанции |	order_amount=1000, distance_km=5.01, is_premium=False |	500.0 |	Граничный |
|TC-06 |	Граница средней дистанции 20 км |	order_amount=1000, distance_km=20, is_premium=False |	500.0	| Граничный |
|TC-07 | 	Переход к длинной дистанции	| order_amount=1000, distance_km=21, is_premium=False |	530.0 |	Граничный |
|TC-08 |	Длинная дистанция 30 км |	order_amount=1000, distance_km=30, is_premium=False |	800.0 |	Позитивный |
|TC-09 |	Скидка premium для средней дистанции |	order_amount=1000, distance_km=10, is_premium=True |	250.0 |	Позитивный |
|TC-10 |	Скидка premium для длинной дистанции |	order_amount=1000, distance_km=30, is_premium=True |	400.0 |	Позитивный |
|TC-11 |	Premium и бесплатная доставка |	order_amount=5000, distance_km=100, is_premium=True |	0.0	 | Позитивный, граничный |
|TC-12 |	Premium и короткая дистанция |	 order_amount=1000, distance_km=5, is_premium=True |	100.0 |	Позитивный |
|TC-13 |	Отрицательная сумма заказа |	order_amount=-1, distance_km=10, is_premium=False |	ValueError |	Негативный |
|TC-14 |	Отрицательная дистанция |	order_amount=1000, distance_km=-1, is_premium=False |	ValueError |	Негативный |
|TC-15 |	Нулевая сумма заказа |	order_amount=0, distance_km=10, is_premium=False |	500.0 |	Граничный, позитивный | 

### 3. Файл delivery.py
```python
# delivery.py

def calculate_delivery_cost(order_amount: float, distance_km: float, is_premium: bool) -> float:
    """
    Расчёт стоимости доставки.

    Бизнес-правила:
    1. Если order_amount < 0 или distance_km < 0 — ValueError.
    2. Если order_amount >= 5000 — доставка бесплатна (0).
    3. Иначе:
       - distance_km <= 5: 200
       - 5 < distance_km <= 20: 500
       - distance_km > 20: 500 + (distance_km - 20) * 30
    4. Для is_premium=True применяется скидка 50% на стоимость доставки.
    """
    if order_amount < 0:
        raise ValueError("order_amount must be >= 0")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    if order_amount >= 5000:
        cost = 0.0
    elif distance_km <= 5:
        cost = 200.0
    elif distance_km <= 20:
        cost = 500.0
    else:
        cost = 500.0 + (distance_km - 20) * 30.0

    if is_premium:
        cost *= 0.5

    return cost
```

### 4. Автотесты test_delivery.py
```python
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

```

### 5. Вывод
Какие ветви кода покрыты

Покрыты:
    - проверка order_amount < 0 → ValueError;
    - проверка distance_km < 0 → ValueError;
    - ветвь order_amount >= 5000 → бесплатная доставка;
    - ветвь distance_km <= 5 → 200.0;
    - ветвь 5 < distance_km <= 20 → 500.0;
    - ветвь distance_km > 20 → формула 500 + (distance_km - 20) * 30;
    - ветвь is_premium = True → скидка 50%;
    - ветвь is_premium = False → скидка не применяется.