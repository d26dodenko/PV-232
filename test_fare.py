# test_fare.py

import pytest
from fare import count_fare

# Позитивные и граничные тесты
def test_min_age():
    # Минимально возможный возраст 0
    assert count_fare(23.2, 0, False, False) == 0

def test_max_age():
    # Максимально возможный возраст 116
    assert count_fare(34.0, 116, False, False) == 104

def test_age_5():
    # В 5 проезд платный
    assert count_fare(23.2, 5, False, False) == 77

def test_short_distance():
    # От 0(не вкл) до 2.49км цена 25руб
    assert count_fare(2.49, 7, False, False) == 25

def test_long_distance():
    # От 2.5км цена - 25 + 2.5 за каждый км после 2.49км
    assert count_fare(2.5, 7, False, False) == 25

def test_age_below_5():
    # От 0 до 5 лет проезд бесплатный
    assert count_fare(23.2, 4, False, False) == 0

def test_age_from_5():
    # C 5 до 116 лет проезд платный
    assert count_fare(19.3, 37, False, False) == 67

def test_preferential():
    # Льготный проезд бесплатный
    assert count_fare(19.3, 26, True, False) == 0

def test_not_preferential():
    # Не льготный проезд платный
    assert count_fare(23.2, 26, False, False) == 77

def test_night_time():
    # Ночью проезд на 20% больше
    assert count_fare(17.4, 26, False, True) == 75

def test_distance_below_border():
    # От 0(не вкл) до 2.49км цена 25руб
    assert count_fare(1.4, 26, False, False) == 25

def test_distance_from_border():
    # От 2.5км цена - 25 + 2.5 за каждый км
    assert count_fare(45.7, 26, False, False) == 133

def test_preferential_night_time():
    # Льготный проезд в ночное время. Льготный проезд преобладает
    assert count_fare(23.2, 26, True, True) == 0

def test_age_from_5_night_time():
    # От 5 до 116 лет и ночное время. Возраст преобладает
    assert count_fare(23.2, 2, False, True) == 0

# Негативные тесты
def test_distance_below_or_equal_0():
    # Расстояние меньше или равное 0 — ошибка
    with pytest.raises(ValueError):
        count_fare(-2.3, 26, False, False)

def test_not_bool_preferential():
    # Льгота не булевое значение — ошибка
    with pytest.raises(ValueError):
        count_fare(10.0, 26, 3, False)

def test_not_bool_night():
    # Ночное время не булевое значение — ошибка
    with pytest.raises(ValueError):
        count_fare(10.0, 26, False, '')

def test_distance_0():
    # Расстояние меньше или равное 0 — ошибка
    with pytest.raises(ValueError):
        count_fare(0.0, 26, False, False)

def test_age_below_0():
    # Возраст меньше 0 — ошибка
    with pytest.raises(ValueError):
        count_fare(23.2, -3, False, False)

def test_age_from_116():
    # Возраст больше 116 — ошибка
    with pytest.raises(ValueError):
        count_fare(23.2, 148, False, False)