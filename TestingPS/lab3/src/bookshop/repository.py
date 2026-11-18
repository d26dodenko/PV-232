"""Хранилище магазина. Заказ, остатки и очистка корзины меняются вместе."""

import sqlite3
from pathlib import Path

from .domain import CartItem, Product, ShopError, cart_total

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
  token TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY, title TEXT NOT NULL, author TEXT NOT NULL,
  price INTEGER NOT NULL CHECK(price > 0), stock INTEGER NOT NULL CHECK(stock >= 0)
);
CREATE TABLE IF NOT EXISTS cart (
  user_id INTEGER NOT NULL REFERENCES users(id),
  product_id INTEGER NOT NULL REFERENCES products(id),
  quantity INTEGER NOT NULL CHECK(quantity BETWEEN 1 AND 10),
  PRIMARY KEY(user_id, product_id)
);
CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
  name TEXT NOT NULL, address TEXT NOT NULL, total INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS order_items (
  order_id INTEGER NOT NULL REFERENCES orders(id),
  title TEXT NOT NULL, price INTEGER NOT NULL, quantity INTEGER NOT NULL
);
"""
PRODUCTS = [
  (1, "Python с нуля", "Анна Белова", 129000, 20),
  (2, "Тестирование на практике", "Илья Соколов", 159000, 12),
  (3, "Чистая архитектура", "Мария Орлова", 189000, 8),
  (4, "Алгоритмы каждый день", "Павел Волков", 99000, 5),
]


class Repository:
  def __init__(self, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    self.db = sqlite3.connect(path, timeout=10)
    self.db.row_factory = sqlite3.Row
    self.db.execute("PRAGMA foreign_keys = ON")

  def close(self):
    self.db.close()

  def initialize(self):
    self.db.executescript(SCHEMA)
    with self.db:
      self.db.executemany("INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?, ?)", PRODUCTS)

  def create_user(self, name, email, password_hash):
    try:
      with self.db:
        return self.db.execute(
          "INSERT INTO users(name, email, password_hash) VALUES (?, ?, ?)",
          (name, email, password_hash),
        ).lastrowid
    except sqlite3.IntegrityError as error:
      raise ShopError("Этот email уже зарегистрирован.") from error

  def user_by_email(self, email):
    return self.db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

  def start_session(self, token, user_id):
    with self.db:
      self.db.execute("INSERT INTO sessions VALUES (?, ?)", (token, user_id))

  def session_user(self, token):
    return self.db.execute(
      "SELECT users.* FROM users JOIN sessions ON users.id = sessions.user_id "
      "WHERE sessions.token = ?",
      (token,),
    ).fetchone()

  def end_session(self, token):
    with self.db:
      self.db.execute("DELETE FROM sessions WHERE token = ?", (token,))

  def products(self):
    return [Product(**dict(row)) for row in self.db.execute("SELECT * FROM products ORDER BY id")]

  def cart(self, user_id):
    rows = self.db.execute(
      "SELECT products.*, cart.quantity FROM cart JOIN products "
      "ON products.id = cart.product_id WHERE cart.user_id = ? ORDER BY products.id",
      (user_id,),
    )
    return [
      CartItem(
        Product(row["id"], row["title"], row["author"], row["price"], row["stock"]), row["quantity"]
      )
      for row in rows
    ]

  def add_to_cart(self, user_id, product_id, amount):
    with self.db:
      self.db.execute("BEGIN IMMEDIATE")
      product = self.db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
      if product is None:
        raise ShopError("Книга не найдена.")
      current = self.db.execute(
        "SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id)
      ).fetchone()
      quantity = (current["quantity"] if current else 0) + amount
      if quantity > min(product["stock"], 10):
        raise ShopError("Недостаточно книг в наличии или превышен лимит 10 экземпляров.")
      self.db.execute(
        "INSERT INTO cart VALUES (?, ?, ?) ON CONFLICT(user_id, product_id) "
        "DO UPDATE SET quantity = excluded.quantity",
        (user_id, product_id, quantity),
      )

  def remove_from_cart(self, user_id, product_id):
    with self.db:
      self.db.execute(
        "DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id)
      )

  def checkout(self, user_id, name, address):
    with self.db:
      self.db.execute("BEGIN IMMEDIATE")
      items = self.cart(user_id)
      if not items:
        raise ShopError("Корзина пуста.")
      if any(item.quantity > item.product.stock for item in items):
        raise ShopError("Остаток изменился. Удалите недоступную книгу из корзины.")
      order_id = self.db.execute(
        "INSERT INTO orders(user_id, name, address, total) VALUES (?, ?, ?, ?)",
        (user_id, name, address, cart_total(items)),
      ).lastrowid
      for item in items:
        self.db.execute(
          "INSERT INTO order_items VALUES (?, ?, ?, ?)",
          (order_id, item.product.title, item.product.price, item.quantity),
        )
        self.db.execute(
          "UPDATE products SET stock = stock - ? WHERE id = ?", (item.quantity, item.product.id)
        )
      self.db.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
      return order_id

  def order(self, user_id, order_id):
    order = self.db.execute(
      "SELECT * FROM orders WHERE id = ? AND user_id = ?", (order_id, user_id)
    ).fetchone()
    items = self.db.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,)).fetchall()
    return order, items
