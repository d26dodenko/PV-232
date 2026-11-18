"""HTTP-слой магазина и управление пользовательским сеансом."""

import os
import secrets
from functools import wraps
from pathlib import Path

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for

from .domain import ShopError, cart_total, money
from .repository import Repository
from .service import ShopService


def create_app(config=None):
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_mapping(
    SECRET_KEY=os.environ.get("SHOP_SECRET") or secrets.token_hex(32),
    DATABASE=os.environ.get("SHOP_DATABASE", str(Path.cwd() / "instance" / "shop.sqlite")),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("SHOP_HTTPS") == "1",
    MAX_CONTENT_LENGTH=16 * 1024,
  )
  if config:
    app.config.update(config)
  repository = Repository(app.config["DATABASE"])
  repository.initialize()
  repository.close()
  app.jinja_env.filters["money"] = money

  def repo():
    if "repository" not in g:
      g.repository = Repository(app.config["DATABASE"])
    return g.repository

  def service():
    return ShopService(repo())

  @app.teardown_appcontext
  def close_repository(error=None):
    repository = g.pop("repository", None)
    if repository:
      repository.close()

  @app.before_request
  def load_user_and_check_csrf():
    g.user = repo().session_user(session.get("sid", ""))
    if request.method == "POST":
      expected = session.get("csrf", "")
      supplied = request.form.get("csrf", "")
      if not expected or not secrets.compare_digest(expected.encode(), supplied.encode()):
        abort(400, description="Недействительный CSRF-токен.")

  @app.context_processor
  def template_context():
    if "csrf" not in session:
      session["csrf"] = secrets.token_urlsafe(32)
    return {"csrf": session["csrf"], "user": g.user}

  def authenticated(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
      if g.user is None:
        return redirect(url_for("login"))
      return view(*args, **kwargs)

    return wrapped

  @app.get("/")
  def catalog():
    query = request.args.get("q", "")
    return render_template("catalog.html", products=service().search(query), query=query)

  @app.route("/register", methods=["GET", "POST"])
  def register():
    error = None
    if request.method == "POST":
      try:
        service().register(
          request.form.get("name", ""),
          request.form.get("email", ""),
          request.form.get("password", ""),
        )
        flash("Регистрация завершена. Войдите в аккаунт.")
        return redirect(url_for("login"))
      except ShopError as exc:
        error = str(exc)
    return render_template("auth.html", registration=True, error=error), 400 if error else 200

  @app.route("/login", methods=["GET", "POST"])
  def login():
    error = None
    if request.method == "POST":
      try:
        token = service().login(request.form.get("email", ""), request.form.get("password", ""))
        repo().end_session(session.get("sid", ""))
        session.clear()
        session["sid"] = token
        flash("Вы вошли в аккаунт.")
        return redirect(url_for("catalog"))
      except ShopError as exc:
        error = str(exc)
    return render_template("auth.html", registration=False, error=error), 400 if error else 200

  @app.post("/logout")
  @authenticated
  def logout():
    repo().end_session(session["sid"])
    session.clear()
    flash("Вы вышли из аккаунта.")
    return redirect(url_for("catalog"))

  @app.get("/cart")
  @authenticated
  def cart():
    items = repo().cart(g.user["id"])
    return render_template("cart.html", items=items, total=cart_total(items))

  @app.post("/cart/<int:product_id>/add")
  @authenticated
  def add_to_cart(product_id):
    try:
      service().add_to_cart(g.user["id"], product_id, request.form.get("quantity", "1"))
    except ShopError as exc:
      return render_template("error.html", message=str(exc)), 400
    flash("Книга добавлена в корзину.")
    return redirect(url_for("cart"))

  @app.post("/cart/<int:product_id>/remove")
  @authenticated
  def remove_from_cart(product_id):
    repo().remove_from_cart(g.user["id"], product_id)
    return redirect(url_for("cart"))

  @app.route("/checkout", methods=["GET", "POST"])
  @authenticated
  def checkout():
    error = None
    if request.method == "POST":
      try:
        order_id = service().checkout(
          g.user["id"], request.form.get("name", ""), request.form.get("address", "")
        )
        return redirect(url_for("order", order_id=order_id))
      except ShopError as exc:
        error = str(exc)
    items = repo().cart(g.user["id"])
    return render_template(
      "checkout.html", items=items, total=cart_total(items), error=error
    ), 400 if error else 200

  @app.get("/orders/<int:order_id>")
  @authenticated
  def order(order_id):
    order, items = repo().order(g.user["id"], order_id)
    if order is None:
      abort(404)
    return render_template("order.html", order=order, items=items)

  return app
