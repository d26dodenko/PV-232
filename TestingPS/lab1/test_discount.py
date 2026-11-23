import pytest
from discount import calc_discount


def test_price_zero():
  with pytest.raises(ValueError):
    calc_discount(0, 5)


def test_price_negative():
  with pytest.raises(ValueError):
    calc_discount(-10, 5)


def test_count_zero():
  with pytest.raises(ValueError):
    calc_discount(100, 0)


def test_count_negative():
  with pytest.raises(ValueError):
    calc_discount(100, -1)


def test_count_one_to_ten_discount():
  assert calc_discount(100, 10) == 99


def test_count_eleven_to_twenty_discount():
  assert calc_discount(100, 20) == 98


def test_count_twentyone_to_thirty_discount():
  assert calc_discount(100, 30) == 96


def test_count_thirtyone_to_fifty_discount():
  assert calc_discount(100, 50) == 94


def test_count_fiftyone_to_seventy_discount():
  assert calc_discount(100, 70) == 92


def test_count_above_seventy_discount():
  assert calc_discount(100, 71) == 91