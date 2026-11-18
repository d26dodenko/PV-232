import os
import threading
import uuid
from pathlib import Path

import pytest
from werkzeug.serving import make_server

from bookshop import create_app

from .pages import AuthPage


@pytest.fixture(scope="session")
def base_url(tmp_path_factory):
  path = tmp_path_factory.mktemp("e2e") / "shop.sqlite"
  app = create_app({"DATABASE": str(path)})
  server = make_server("127.0.0.1", 0, app, threaded=True)
  thread = threading.Thread(target=server.serve_forever, daemon=True)
  thread.start()
  yield f"http://127.0.0.1:{server.server_port}"
  server.shutdown()
  thread.join(timeout=5)
  server.server_close()


@pytest.fixture
def email():
  return f"reader-{uuid.uuid4().hex}@example.test"


@pytest.fixture
def signed_in(page, base_url, email):
  auth = AuthPage(page, base_url)
  auth.register(email)
  auth.login(email)
  return auth


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
  return {**browser_context_args, "viewport": {"width": 1280, "height": 900}, "locale": "ru-RU"}


@pytest.fixture(autouse=True)
def save_test_screenshot(page, request):
  yield
  directory = Path("reports/screenshots")
  directory.mkdir(parents=True, exist_ok=True)
  page.screenshot(path=str(directory / f"{request.node.name}.png"), full_page=True)


@pytest.fixture
def expected_order_total():
  return "Итого: 1 290,01 ₽" if os.environ.get("LAB3_DEMO") == "e2e" else "Итого: 1 290,00 ₽"
