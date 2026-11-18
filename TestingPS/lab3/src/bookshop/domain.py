"""Правила ввода и расчёта стоимости, независимые от HTTP и SQLite."""

import re
from dataclasses import dataclass


class ShopError(ValueError):
  pass


def email_address(value: str) -> str:
  value = value.strip().casefold()
  if len(value) > 120 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
    raise ShopError("Укажите корректный email.")
  return value


def customer_name(value: str) -> str:
  value = value.strip()
  if not 2 <= len(value) <= 60:
    raise ShopError("Имя должно содержать от 2 до 60 символов.")
  return value


def password_value(value: str) -> str:
  if not 8 <= len(value) <= 128 or not value.strip():
    raise ShopError("Пароль должен содержать от 8 до 128 символов.")
  return value


def delivery_address(value: str) -> str:
  value = value.strip()
  if not 5 <= len(value) <= 200:
    raise ShopError("Адрес должен содержать от 5 до 200 символов.")
  return value


def quantity_value(value: str) -> int:
  if not value.isascii() or not value.isdigit() or len(value) > 2 or not 1 <= int(value) <= 10:
    raise ShopError("Количество должно быть целым числом от 1 до 10.")
  return int(value)


def money(cents: int) -> str:
  return f"{cents // 100:,}".replace(",", " ") + f",{cents % 100:02d} ₽"


@dataclass(frozen=True)
class Product:
  id: int
  title: str
  author: str
  price: int
  stock: int


@dataclass(frozen=True)
class CartItem:
  product: Product
  quantity: int

  @property
  def total(self) -> int:
    return self.product.price * self.quantity


def cart_total(items: list[CartItem]) -> int:
  return sum(item.total for item in items)
