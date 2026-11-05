# test_tf2_item.py

import pytest

from tf2_item import calculate_item_cost


def test_serial_unique_no_extras():
    assert calculate_item_cost("serial", "unique", False, 0, 0, 10, False) == pytest.approx(10.0, abs=0.01)


def test_specialized_unique_no_extras():
    assert calculate_item_cost("specialized", "unique", False, 0, 0, 10, False) == pytest.approx(15.0, abs=0.01)


def test_professional_unique_no_extras():
    assert calculate_item_cost("professional", "unique", False, 0, 0, 10, False) == pytest.approx(25.0, abs=0.01)


def test_serial_strange_no_extras():
    assert calculate_item_cost("serial", "strange", False, 0, 0, 10, False) == pytest.approx(18.0, abs=0.01)


def test_professional_strange_no_extras():
    assert calculate_item_cost("professional", "strange", False, 0, 0, 10, False) == pytest.approx(45.0, abs=0.01)


def test_with_spells():
    assert calculate_item_cost("serial", "unique", True, 0, 0, 10, False) == pytest.approx(14.0, abs=0.01)


def test_with_decorations():
    assert calculate_item_cost("serial", "unique", False, 0, 0, 10, True) == pytest.approx(12.0, abs=0.01)


def test_with_spells_and_decorations():
    assert calculate_item_cost("serial", "unique", True, 0, 0, 10, True) == pytest.approx(16.8, abs=0.01)


def test_with_strange_counters():
    assert calculate_item_cost("serial", "unique", False, 5, 100, 10, False) == pytest.approx(15.0, abs=0.01)


def test_full_set_professional_strange():
    assert calculate_item_cost("professional", "strange", True, 3, 200, 50, True) == pytest.approx(384.0, abs=0.01)


def test_minimum_values():
    assert calculate_item_cost("serial", "unique", False, 0, 0, 0.01, False) == pytest.approx(0.01, abs=0.01)


def test_maximum_values():
    assert calculate_item_cost("professional", "strange", True, 10, 1000, 10000, True) == pytest.approx(75700.0, abs=0.01)


def test_invalid_killstreak_tier():
    with pytest.raises(ValueError):
        calculate_item_cost("legendary", "unique", False, 0, 0, 10, False)


def test_invalid_quality():
    with pytest.raises(ValueError):
        calculate_item_cost("serial", "vintage", False, 0, 0, 10, False)


def test_counter_count_negative():
    with pytest.raises(ValueError):
        calculate_item_cost("serial", "unique", False, -1, 0, 10, False)


def test_counter_count_too_large():
    with pytest.raises(ValueError):
        calculate_item_cost("serial", "unique", False, 11, 0, 10, False)


def test_counter_value_negative():
    with pytest.raises(ValueError):
        calculate_item_cost("serial", "unique", False, 0, -1, 10, False)


def test_counter_value_too_large():
    with pytest.raises(ValueError):
        calculate_item_cost("serial", "unique", False, 0, 1001, 10, False)


def test_base_cost_zero():
    with pytest.raises(ValueError):
        calculate_item_cost("serial", "unique", False, 0, 0, 0, False)


def test_base_cost_too_large():
    with pytest.raises(ValueError):
        calculate_item_cost("serial", "unique", False, 0, 0, 10001, False)