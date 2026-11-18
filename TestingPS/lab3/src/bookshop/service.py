"""Сценарии покупателя и проверка входных данных."""

import secrets

from werkzeug.security import check_password_hash, generate_password_hash

from .domain import (
  ShopError,
  customer_name,
  delivery_address,
  email_address,
  password_value,
  quantity_value,
)


class ShopService:
  def __init__(self, repository):
    self.repository = repository

  def register(self, name, email, password):
    return self.repository.create_user(
      customer_name(name), email_address(email), generate_password_hash(password_value(password))
    )

  def login(self, email, password):
    user = self.repository.user_by_email(email_address(email))
    if user is None or not check_password_hash(user["password_hash"], password):
      raise ShopError("Неверный email или пароль.")
    token = secrets.token_urlsafe(32)
    self.repository.start_session(token, user["id"])
    return token

  def search(self, query):
    query = query.strip().casefold()
    return [
      product
      for product in self.repository.products()
      if query in f"{product.title} {product.author}".casefold()
    ]

  def add_to_cart(self, user_id, product_id, amount):
    self.repository.add_to_cart(user_id, product_id, quantity_value(amount))

  def checkout(self, user_id, name, address):
    return self.repository.checkout(user_id, customer_name(name), delivery_address(address))
