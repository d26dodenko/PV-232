"""Page Objects содержат действия и локаторы. Ожидания результатов — в тестах."""


class AuthPage:
  def __init__(self, page, base_url):
    self.page = page
    self.base_url = base_url

  def register(self, email, password="BookPassword42", name="Читатель"):
    self.page.goto(self.base_url + "/register")
    self.page.get_by_label("Имя", exact=True).fill(name)
    self.page.get_by_label("Email", exact=True).fill(email)
    self.page.get_by_label("Пароль", exact=True).fill(password)
    self.page.get_by_role("button", name="Зарегистрироваться", exact=True).click()

  def login(self, email, password="BookPassword42"):
    self.page.goto(self.base_url + "/login")
    self.page.get_by_label("Email", exact=True).fill(email)
    self.page.get_by_label("Пароль", exact=True).fill(password)
    self.page.get_by_role("button", name="Войти", exact=True).click()

  def logout(self):
    self.page.get_by_role("button", name="Выйти", exact=True).click()


class CatalogPage:
  def __init__(self, page, base_url):
    self.page = page
    self.base_url = base_url

  def open(self):
    self.page.goto(self.base_url + "/")

  def search(self, query):
    self.page.get_by_label("Поиск по названию или автору").fill(query)
    self.page.get_by_role("button", name="Найти", exact=True).click()

  def add(self, title):
    self.page.get_by_role("article", name=title, exact=True).get_by_role(
      "button", name="В корзину"
    ).click()


class CartPage:
  def __init__(self, page, base_url):
    self.page = page
    self.base_url = base_url

  def open(self):
    self.page.goto(self.base_url + "/cart")

  def remove(self, title):
    self.page.get_by_role("button", name="Удалить " + title, exact=True).click()

  def checkout(self):
    self.page.get_by_role("link", name="Оформить заказ", exact=True).click()


class CheckoutPage:
  def __init__(self, page):
    self.page = page

  def submit(self, name, address):
    self.page.get_by_label("Получатель", exact=True).fill(name)
    self.page.get_by_label("Адрес доставки", exact=True).fill(address)
    self.page.get_by_role("button", name="Подтвердить заказ", exact=True).click()
