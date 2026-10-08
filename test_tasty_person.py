# test_tasty_person.py

import pytest

from tasty_person import calculate_tastiness


def test_good_person():
    # Хороший вариант
    assert calculate_tastiness(180, 70, 40, "Илья", "active") == pytest.approx(69.26, abs=0.01)


def test_normal_person():
    # Обычный человек, нормальный ИМТ
    assert calculate_tastiness(175, 70, 15, "Илья", "passive") == pytest.approx(62.63, abs=0.01)


def test_active_lifestyle():
    # Активный образ жизни
    assert calculate_tastiness(175, 70, 15, "Илья", "active") == pytest.approx(93.94, abs=0.01)


def test_low_bmi():
    # Низкий ИМТ
    assert calculate_tastiness(180, 55, 10, "Аня", "passive") == pytest.approx(47.92, abs=0.01)


def test_high_bmi():
    # Высокий ИМТ
    assert calculate_tastiness(160, 90, 30, "Олег", "passive") == pytest.approx(24.18, abs=0.01)


def test_minimum_height():
    # Минимальный рост на границе
    assert calculate_tastiness(50, 50, 10, "A", "passive") == pytest.approx(3.82, abs=0.01)


def test_maximum_weight():
    # Максимальный вес на границе
    assert calculate_tastiness(250, 400, 70, "Егор", "passive") == pytest.approx(4.61, abs=0.01)


def test_minimum_weight():
    # Минимальный вес на границе
    assert calculate_tastiness(175, 1, 0, "Зина", "passive") == pytest.approx(25.25, abs=0.01)


def test_maximum_fat_percent():
    # Максимальный процент жира
    assert calculate_tastiness(175, 70, 70, "Игорь", "passive") == pytest.approx(22.10, abs=0.01)


def test_zero_fat_percent_active():
    # Нулевой процент жира, идеал только мясо
    assert calculate_tastiness(175, 70, 0, "Костя", "active") == pytest.approx(100.0, abs=0.01)


def test_zero_fat_percent_passive():
    # Нормальный ИМТ, нулевой жир, пассивный
    assert calculate_tastiness(175, 70, 0, "Лена", "passive") == pytest.approx(73.68, abs=0.01)


def test_height_too_small():
    # Рост меньше 50
    with pytest.raises(ValueError):
        calculate_tastiness(49.99, 70, 10, "Лена", "passive")


def test_height_too_large():
    # Рост больше 250
    with pytest.raises(ValueError):
        calculate_tastiness(250.01, 70, 10, "Миша", "passive")


def test_weight_too_small():
    # Вес меньше 1
    with pytest.raises(ValueError):
        calculate_tastiness(175, 0.99, 10, "Нина", "passive")


def test_weight_too_large():
    # Вес больше 400
    with pytest.raises(ValueError):
        calculate_tastiness(175, 400.01, 10, "Оля", "passive")


def test_fat_percent_negative():
    # Процент жира меньше 0
    with pytest.raises(ValueError):
        calculate_tastiness(175, 70, -0.01, "Петя", "passive")


def test_fat_percent_too_large():
    # Процент жира больше 70
    with pytest.raises(ValueError):
        calculate_tastiness(175, 70, 70.01, "Рита", "passive")


def test_empty_name():
    # Пустое имя
    with pytest.raises(ValueError):
        calculate_tastiness(175, 70, 10, "", "passive")


def test_invalid_lifestyle():
    # Недопустимый образ жизни
    with pytest.raises(ValueError):
        calculate_tastiness(175, 70, 10, "Соня", "mixed")