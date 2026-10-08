Лабораторный отчет: Тестирование программного обеспечения и обеспечение качества

Студент: Окон Самуэль ИТА

Группа: Пв232
Дата: [08-08-26]
Дисциплина: Тестирование в программировании

Цель работы
Сформировать системное представление о качестве ПО и роли тестирования в жизненном цикле; приобрести практические навыки проектирования тест-кейсов и написания автотестов на основе готового кода.

Анализ исходного кода
Был проанализирован модуль delivery.py, который рассчитывает стоимость доставки на основе суммы заказа, расстояния и статуса премиум-пользователя.

Бизнес-правила:
1. Если order_amount < 0 или distance_km < 0 — вызывается исключение ValueError.
2. Если order_amount >= 5000 — доставка бесплатна (стоимость = 0).
3. В остальных случаях базовая стоимость доставки зависит от расстояния:
              distance_km <= 5: стоимость = 200
             5  < distance_km <= 20: стоимость = 500
            distance_km > 20: стоимость = 500 + (distance_km - 20) * 30
4.Если is_premium = True, применяется скидка 50% на итоговую стоимость доставки.

Входные и выходные параметры:
Входные: order_amount (float), distance_km (float), is_premium (bool)
Выходной: float (итоговая стоимость доставки)
Допустимые, недопустимые и граничные значения:
Допустимые: order_amount >= 0, distance_km >= 0, is_premium равен True или False.
Недопустимые: order_amount < 0, distance_km < 0.

Граничные: 0 (нулевое расстояние), 5 (граница короткой дистанции), 20 (граница средней дистанции), 5000 (порог бесплатной доставки), 4999.99 (чуть ниже порога).

Проектирование тест-кейсов
Было разработано 14 тест-кейсов, что удовлетворяет требованию (не менее 10) и охватывает позитивные, негативные, граничные сценарии, а также проверку скидки для premium-пользователей и бесплатной доставки.

(Здесь вам нужно создать таблицу в Word: Вставка -> Таблица. Сделайте 5 колонок и 15 строк. Скопируйте данные ниже в соответствующие ячейки):

Колонка 1: ID | Колонка 2: Название теста | Колонка 3: Категория | Колонка 4: Входные данные (Сумма, Расстояние, Premium) | Колонка 5: Ожидаемый результат

TC-01 | test_free_delivery_from_5000 | Позитивный, Граничный, Бесплатная доставка | 5000, 10, False | 0.0
TC-02 | test_paid_delivery_below_5000 | Позитивный, Граничный | 4999.99, 10, False | 500.0
TC-03 | test_short_distance | Позитивный, Граничный | 1000, 5, False | 200.0
TC-04 | test_middle_distance | Позитивный, Граничный | 1000, 20, False | 500.0
TC-05 | test_long_distance | Позитивный | 1000, 30, False | 800.0
TC-06 | test_premium_discount | Позитивный, Premium | 1000, 10, True | 250.0
TC-07 | test_premium_with_free_delivery | Позитивный, Premium, Бесплатная доставка | 5000, 10, True | 0.0
TC-08 | test_premium_with_long_distance | Позитивный, Premium | 1000, 30, True | 400.0
TC-09 | test_distance_just_above_5 | Граничный | 1000, 5.1, False | 500.0
TC-10 | test_distance_just_above_20 | Граничный | 1000, 20.1, False | 503.0
TC-11 | test_zero_order_amount_short_distance | Граничный | 0, 3, False | 200.0
TC-12 | test_zero_distance | Граничный | 1000, 0, False | 200.0
TC-13 | test_negative_order_amount | Негативный | -1, 10, False | ValueError
TC-14 | test_negative_distance | Негативный | 1000, -1, False | ValueError

Реализация и запуск автотестов
Автотесты были реализованы на языке Python с использованием фреймворка pytest. В файле test_delivery.py используются утверждения (assert) для проверки ожидаемых результатов и pytest.raises(ValueError) для проверки обработки исключений при недопустимых входных данных.

import pytest
from delivery import calculate_delivery_cost

--- Позитивные и граничные тесты ---
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

Исправлено с помощью pytest.approx для обработки погрешности округления
assert calculate_delivery_cost(1000, 20.1, False) == pytest.approx(503.0)

def test_zero_order_amount_short_distance():
assert calculate_delivery_cost(0, 3, False) == 200.0

def test_zero_distance():
assert calculate_delivery_cost(1000, 0, False) == 200.0

--- Негативные тесты ---
def test_negative_order_amount():
with pytest.raises(ValueError):
calculate_delivery_cost(-1, 10, False)

def test_negative_distance():
with pytest.raises(ValueError):
calculate_delivery_cost(1000, -1, False)

Запуск тестов:
Тесты были запущены с помощью команды:
pytest -v

Примечания по настройке и отладке:
Во время установки pytest возникла ошибка прокси-сервера ОС (Missing dependencies for SOCKS support). Проблема была решена запуском команды pip install pytest --proxy="".

При первом запуске 13 из 14 тестов прошли успешно. Тест test_distance_just_above_20 не прошел с ошибкой: assert 503.00000000000006 == 503.0. Это классическая проблема точности чисел с плавающей точкой в Python. Ошибка была исправлена путем оборачивания ожидаемого результата в pytest.approx(503.0). После исправления все 14 тестов успешно прошли:

======================= 14 passed in 0.05s =======================

 


Вывод
В ходе лабораторной работы были проанализированы бизнес-правила модуля delivery.py и разработано 14 автотестов на языке Python с использованием фреймворка pytest.

Тесты успешно покрыли все ветви кода: валидацию входных данных, все тарифные уровни расстояния, порог бесплатной доставки и скидку для premium-пользователей. В процессе тестирования была выявлена и исправлена ошибка точности вычислений с плавающей точкой.

Остаточные риски включают отсутствие проверок на неверные типы данных и экстремально большие значения.

Тестирование критически важно для жизненного цикла ПО, так как позволяет выявлять дефекты на ранних этапах, снижает стоимость их исправления и гарантирует надежность конечного продукта.

