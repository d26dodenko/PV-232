import secrets

import pytest

from bookshop import create_app
from bookshop.repository import Repository


@pytest.fixture
def app(tmp_path):
  return create_app(
    {
      "TESTING": True,
      "DATABASE": str(tmp_path / "shop.sqlite"),
      "SECRET_KEY": secrets.token_hex(32),
    }
  )


@pytest.fixture
def client(app):
  return app.test_client()


@pytest.fixture
def repository(app):
  repository = Repository(app.config["DATABASE"])
  yield repository
  repository.close()


@pytest.fixture
def post():
  def send(client, path, **data):
    client.get("/")
    with client.session_transaction() as session:
      data["csrf"] = session["csrf"]
    return client.post(path, data=data)

  return send


@pytest.fixture
def account(post):
  def create(client, email="reader@example.test"):
    response = post(client, "/register", name="Читатель", email=email, password="BookPassword42")
    assert response.status_code == 302
    response = post(client, "/login", email=email, password="BookPassword42")
    assert response.status_code == 302
    return email

  return create
