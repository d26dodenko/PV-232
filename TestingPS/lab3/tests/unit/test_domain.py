import pytest

from bookshop.domain import (
  CartItem,
  Product,
  ShopError,
  cart_total,
  customer_name,
  delivery_address,
  email_address,
  money,
  password_value,
  quantity_value,
)


@pytest.mark.parametrize(
  "value, expected",
  [
    ("reader@example.test", "reader@example.test"),
    ("  Reader@EXAMPLE.test  ", "reader@example.test"),
  ],
)
def test_email_is_normalized(value, expected):
  assert email_address(value) == expected


@pytest.mark.parametrize(
  "value", ["", "reader", "a@b", "a b@x.test", "a@@x.test", "a" * 121 + "@x.test"]
)
def test_invalid_email_is_rejected(value):
  with pytest.raises(ShopError):
    email_address(value)


@pytest.mark.parametrize("value", ["Ан", "А" * 60])
def test_name_boundaries(value):
  assert customer_name(" " + value + " ") == value


@pytest.mark.parametrize("value", [" ", "А", "А" * 61])
def test_invalid_name(value):
  with pytest.raises(ShopError):
    customer_name(value)


@pytest.mark.parametrize("value", ["12345678", "a" * 128])
def test_password_boundaries(value):
  assert password_value(value) == value


@pytest.mark.parametrize("value", ["short", " " * 8, "a" * 129])
def test_invalid_password(value):
  with pytest.raises(ShopError):
    password_value(value)


@pytest.mark.parametrize("value", ["12345", "А" * 200])
def test_address_boundaries(value):
  assert delivery_address(" " + value + " ") == value


@pytest.mark.parametrize("value", ["", "1234", "А" * 201])
def test_invalid_address(value):
  with pytest.raises(ShopError):
    delivery_address(value)


@pytest.mark.parametrize("value, expected", [("1", 1), ("10", 10)])
def test_quantity_boundaries(value, expected):
  assert quantity_value(value) == expected


@pytest.mark.parametrize(
  "value", ["", "0", "11", "-1", "1.5", "one", "²", pytest.param("1" * 5000, id="oversized")]
)
def test_invalid_quantity(value):
  with pytest.raises(ShopError):
    quantity_value(value)


@pytest.mark.parametrize("value, expected", [(0, "0,00 ₽"), (199999, "1 999,99 ₽")])
def test_money_format(value, expected):
  assert money(value) == expected


def test_cart_uses_integer_prices_and_quantities():
  items = [
    CartItem(Product(1, "A", "Автор", 129000, 10), 2),
    CartItem(Product(2, "B", "Автор", 99099, 10), 1),
  ]
  assert cart_total(items) == 357099
  assert cart_total([]) == 0
