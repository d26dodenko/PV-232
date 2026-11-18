from playwright.sync_api import expect

from .pages import AuthPage, CartPage, CatalogPage, CheckoutPage


def test_registration(page, base_url, email):
  AuthPage(page, base_url).register(email)
  expect(page.get_by_role("heading", name="Вход", exact=True)).to_be_visible()
  expect(page.get_by_role("status")).to_have_text("Регистрация завершена. Войдите в аккаунт.")
  AuthPage(page, base_url).register(email)
  expect(page.get_by_role("alert")).to_have_text("Этот email уже зарегистрирован.")


def test_login(page, base_url, email):
  auth = AuthPage(page, base_url)
  auth.register(email)
  auth.login(email, "wrong-password")
  expect(page.get_by_role("alert")).to_have_text("Неверный email или пароль.")
  auth.login(email)
  expect(page.get_by_role("button", name="Выйти", exact=True)).to_be_visible()
  page.reload()
  expect(page.get_by_role("button", name="Выйти", exact=True)).to_be_visible()


def test_search(page, base_url):
  catalog = CatalogPage(page, base_url)
  catalog.open()
  catalog.search("тестирование")
  expect(page.get_by_role("article")).to_have_count(1)
  expect(page.get_by_role("heading", name="Тестирование на практике", exact=True)).to_be_visible()
  catalog.search("несуществующаякнига")
  expect(page.get_by_role("status")).to_have_text("Книги не найдены.")


def test_cart(page, base_url, signed_in):
  catalog = CatalogPage(page, base_url)
  catalog.open()
  catalog.add("Python с нуля")
  catalog.open()
  catalog.add("Python с нуля")
  expect(page.get_by_test_id("cart-total")).to_have_text("Итого: 2 580,00 ₽")
  CartPage(page, base_url).remove("Python с нуля")
  expect(page.get_by_role("status")).to_have_text("Корзина пуста.")


def test_checkout(page, base_url, signed_in, expected_order_total):
  catalog = CatalogPage(page, base_url)
  catalog.open()
  catalog.add("Python с нуля")
  CartPage(page, base_url).checkout()
  CheckoutPage(page).submit("Анна Белова", "Москва, улица Книжная, дом 10")
  expect(page.get_by_role("heading", name="Заказ оформлен", exact=True)).to_be_visible()
  expect(page.get_by_test_id("order-total")).to_have_text(expected_order_total)
  expect(page.get_by_text("Адрес: Москва, улица Книжная, дом 10", exact=True)).to_be_visible()
  CartPage(page, base_url).open()
  expect(page.get_by_role("status")).to_have_text("Корзина пуста.")


def test_logout(page, base_url, signed_in):
  old_cookies = page.context.cookies()
  signed_in.logout()
  expect(page.get_by_role("status")).to_have_text("Вы вышли из аккаунта.")
  page.context.add_cookies(old_cookies)
  CartPage(page, base_url).open()
  expect(page.get_by_role("heading", name="Вход", exact=True)).to_be_visible()
