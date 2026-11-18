import sqlite3

import pytest
from werkzeug.security import check_password_hash


def test_registration_persists_hash_and_rejects_duplicate(client, post, repository):
  assert (
    post(
      client, "/register", name="Анна", email="Reader@Example.test", password="BookPassword42"
    ).status_code
    == 302
  )
  user = repository.user_by_email("reader@example.test")
  assert user["password_hash"] != "BookPassword42"
  assert check_password_hash(user["password_hash"], "BookPassword42")
  response = post(
    client, "/register", name="Иван", email="reader@example.test", password="BookPassword42"
  )
  assert response.status_code == 400
  assert "уже зарегистрирован" in response.text
  assert repository.db.execute("SELECT count(*) FROM users").fetchone()[0] == 1


@pytest.mark.parametrize("field, value", [("name", "А"), ("email", "wrong"), ("password", "short")])
def test_registration_validation_at_http_boundary(client, post, field, value):
  data = {"name": "Анна", "email": "reader@example.test", "password": "BookPassword42"}
  data[field] = value
  assert post(client, "/register", **data).status_code == 400


def test_login_wrong_password_and_unknown_email(client, post, account):
  account(client)
  post(client, "/logout")
  for email in ["reader@example.test", "missing@example.test"]:
    response = post(client, "/login", email=email, password="wrong-password")
    assert response.status_code == 400
    assert "Неверный email или пароль" in response.text
  assert client.get("/cart").status_code == 302


def test_search_is_case_insensitive_and_input_is_escaped(client):
  response = client.get("/?q=ТЕСТИРОВАНИЕ")
  assert "Тестирование на практике" in response.text
  assert "Python с нуля" not in response.text
  response = client.get("/", query_string={"q": "<script>alert(1)</script>"})
  assert "Книги не найдены" in response.text
  assert "<script>" not in response.text
  assert "&lt;script&gt;" in response.text


def test_protected_pages_require_login(client):
  for url in ["/cart", "/checkout", "/orders/1"]:
    response = client.get(url)
    assert response.status_code == 302
    assert response.location.endswith("/login")
  assert client.get("/login").status_code == 200
  assert client.get("/register").status_code == 200


def test_csrf_rejects_missing_and_wrong_token(client, account):
  account(client)
  for data in [{}, {"csrf": "invalid"}, {"csrf": "неверный"}]:
    assert client.post("/cart/1/add", data=data).status_code == 400
  assert "Корзина пуста" in client.get("/cart").text


def test_cart_merges_quantities_and_removes_item(client, post, account, repository):
  account(client)
  assert post(client, "/cart/1/add", quantity="1").status_code == 302
  assert post(client, "/cart/1/add", quantity="2").status_code == 302
  items = repository.cart(1)
  assert len(items) == 1
  assert items[0].quantity == 3
  assert items[0].total == 387000
  assert "3 870,00 ₽" in client.get("/cart").text
  assert post(client, "/cart/1/remove").status_code == 302
  assert not repository.cart(1)


@pytest.mark.parametrize("product, quantity", [(999, "1"), (1, "0"), (4, "6")])
def test_cart_rejects_invalid_requests(client, post, account, repository, product, quantity):
  account(client)
  assert post(client, f"/cart/{product}/add", quantity=quantity).status_code == 400
  assert not repository.cart(1)


def test_users_cannot_read_or_delete_each_others_cart_and_order(
  app, client, post, account, repository
):
  account(client)
  post(client, "/cart/1/add")
  other = app.test_client()
  account(other, "other@example.test")
  assert "Корзина пуста" in other.get("/cart").text
  post(other, "/cart/1/remove")
  assert len(repository.cart(1)) == 1
  response = post(client, "/checkout", name="Анна", address="Москва, улица Книжная, 10")
  assert other.get(response.location).status_code == 404


def test_checkout_stores_server_price_and_empties_cart(client, post, account, repository):
  account(client)
  post(client, "/cart/1/add", quantity="2")
  assert client.get("/checkout").status_code == 200
  response = post(client, "/checkout", name="Анна", address="Москва, улица Книжная, 10", total="1")
  assert response.status_code == 302
  order = client.get(response.location)
  assert "Заказ оформлен" in order.text
  assert "2 580,00 ₽" in order.text
  assert repository.products()[0].stock == 18
  assert not repository.cart(1)
  stored = repository.db.execute("SELECT * FROM orders").fetchone()
  assert stored["total"] == 258000
  assert stored["address"] == "Москва, улица Книжная, 10"
  assert client.get("/orders/999").status_code == 404


def test_empty_checkout_and_invalid_address_are_rejected(client, post, account, repository):
  account(client)
  assert "Добавьте книги" in client.get("/checkout").text
  assert post(client, "/checkout", name="Анна", address="Москва, дом 1").status_code == 400
  post(client, "/cart/1/add")
  assert post(client, "/checkout", name="Анна", address="1234").status_code == 400
  assert len(repository.cart(1)) == 1
  assert repository.db.execute("SELECT count(*) FROM orders").fetchone()[0] == 0


def test_checkout_rechecks_changed_stock(client, post, account, repository):
  account(client)
  post(client, "/cart/4/add", quantity="5")
  with repository.db:
    repository.db.execute("UPDATE products SET stock = 4 WHERE id = 4")
  response = post(client, "/checkout", name="Анна", address="Москва, дом 1")
  assert response.status_code == 400
  assert "Остаток изменился" in response.text
  assert repository.products()[3].stock == 4
  assert repository.db.execute("SELECT count(*) FROM orders").fetchone()[0] == 0


def test_checkout_rolls_back_all_changes_on_database_error(client, post, account, repository):
  account(client)
  post(client, "/cart/1/add")
  repository.db.executescript("""
    CREATE TRIGGER reject_item BEFORE INSERT ON order_items
    BEGIN SELECT RAISE(ABORT, 'simulated storage failure'); END;
  """)
  with pytest.raises(sqlite3.IntegrityError):
    post(client, "/checkout", name="Анна", address="Москва, дом 1")
  assert repository.db.execute("SELECT count(*) FROM orders").fetchone()[0] == 0
  assert repository.products()[0].stock == 20
  assert len(repository.cart(1)) == 1


def test_logout_revokes_server_session_even_with_old_cookie(client, post, account):
  account(client)
  old_cookie = client.get_cookie("session").value
  assert post(client, "/logout").status_code == 302
  client.set_cookie("session", old_cookie)
  assert client.get("/cart").status_code == 302
  with client.session_transaction() as session:
    assert session["sid"]
