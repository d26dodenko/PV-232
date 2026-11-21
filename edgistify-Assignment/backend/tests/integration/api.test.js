require("../helpers/test-env");

const test = require("node:test");
const assert = require("node:assert/strict");
const request = require("supertest");
const app = require("../../index");
const ProductModel = require("../../models/ProductModel");
const { resetUsers, seedProducts, PRODUCTS } = require("../helpers/test-db");

seedProducts();

const PASSWORD = "Password123!";

function auth(token) {
  return { Authorization: `Bearer ${token}` };
}

async function createUser(fullName = "Test User") {
  const email = `user.${Date.now()}.${Math.random().toString(36).slice(2)}@example.com`;
  const registered = await request(app)
    .post("/api/users/register")
    .send({ fullName, email, password: PASSWORD });
  assert.equal(registered.status, 200);

  const loggedIn = await request(app)
    .post("/api/users/login")
    .send({ email, password: PASSWORD });
  assert.equal(loggedIn.status, 200);

  return {
    email,
    fullName,
    userId: loggedIn.body.userId,
    token: loggedIn.body.token,
  };
}

async function addToCart(token, overrides = {}) {
  return request(app)
    .post("/api/cart/add")
    .set(auth(token))
    .send({
      productId: "1",
      title: PRODUCTS[0].title,
      price: PRODUCTS[0].price,
      size: "M",
      img1: PRODUCTS[0].images[0],
      ...overrides,
    });
}

test.beforeEach(() => {
  resetUsers();
});

test("GET / reports that the server is running", async () => {
  const response = await request(app).get("/");
  assert.equal(response.status, 200);
  assert.deepEqual(response.body, { message: "Server is running!" });
});

test("POST /api/users/register validates input and rejects duplicates", async () => {
  const missing = await request(app).post("/api/users/register").send({ fullName: "No Email" });
  assert.equal(missing.status, 400);
  assert.equal(missing.body.message, "fullName, email and password are required");

  const user = await createUser("First User");
  const duplicate = await request(app)
    .post("/api/users/register")
    .send({ fullName: "Other User", email: user.email, password: PASSWORD });
  assert.equal(duplicate.status, 400);
  assert.equal(duplicate.body.message, "Email already exists");
});

test("POST /api/users/register returns 500 when the model throws", async () => {
  const UserModel = require("../../models/UserModel");
  const original = UserModel.findByEmail;
  UserModel.findByEmail = () => {
    throw new Error("database error");
  };

  try {
    const response = await request(app)
      .post("/api/users/register")
      .send({ fullName: "Broken", email: "broken@example.com", password: PASSWORD });
    assert.equal(response.status, 500);
    assert.equal(response.body.message, "Something went wrong, please try again");
  } finally {
    UserModel.findByEmail = original;
  }
});

test("POST /api/users/login validates input, finds users and checks passwords", async () => {
  const missing = await request(app).post("/api/users/login").send({ email: "a@b.c" });
  assert.equal(missing.status, 400);
  assert.equal(missing.body.message, "email and password are required");

  const unknown = await request(app)
    .post("/api/users/login")
    .send({ email: "nobody@example.com", password: PASSWORD });
  assert.equal(unknown.status, 404);
  assert.equal(unknown.body.message, "User not found");

  const user = await createUser("Login User");
  const wrongPassword = await request(app)
    .post("/api/users/login")
    .send({ email: user.email, password: "wrong-password" });
  assert.equal(wrongPassword.status, 401);
  assert.equal(wrongPassword.body.message, "Login failed");

  const success = await request(app)
    .post("/api/users/login")
    .send({ email: user.email, password: PASSWORD });
  assert.equal(success.status, 200);
  assert.equal(success.body.message, "Login successful");
  assert.equal(success.body.userName, user.fullName);
  assert.equal(typeof success.body.userId, "string");
  assert.ok(success.body.token);
});

test("GET /api/products returns mapped products", async () => {
  const response = await request(app).get("/api/products");
  assert.equal(response.status, 200);
  assert.equal(response.body.length, PRODUCTS.length);
  assert.equal(response.body[0]._id, "1");
  assert.deepEqual(response.body[0].images, PRODUCTS[0].images);
  assert.deepEqual(response.body[0].sizes, ["M"]);
});

test("GET /api/products/:id returns a product or 404", async () => {
  const found = await request(app).get("/api/products/1");
  assert.equal(found.status, 200);
  assert.equal(found.body.title, PRODUCTS[0].title);

  for (const id of ["999", "abc", "0"]) {
    const missing = await request(app).get(`/api/products/${id}`);
    assert.equal(missing.status, 404);
    assert.equal(missing.body.message, "Product not found");
  }
});

test("product controllers return 500 when the model throws", async () => {
  const originalFindAll = ProductModel.findAll;
  ProductModel.findAll = () => {
    throw new Error("database error");
  };
  const originalFindById = ProductModel.findById;
  ProductModel.findById = () => {
    throw new Error("database error");
  };

  try {
    const list = await request(app).get("/api/products");
    assert.equal(list.status, 500);
    assert.equal(list.body.message, "Error");

    const detail = await request(app).get("/api/products/1");
    assert.equal(detail.status, 500);
    assert.equal(detail.body.message, "Error");
  } finally {
    ProductModel.findAll = originalFindAll;
    ProductModel.findById = originalFindById;
  }
});

test("cart routes require a valid JWT", async () => {
  const anonymous = await request(app).get("/api/cart");
  assert.equal(anonymous.status, 401);
  assert.equal(anonymous.body.message, "Unauthorized");

  const invalid = await request(app).get("/api/cart").set(auth("not-a-token"));
  assert.equal(invalid.status, 401);
  assert.equal(invalid.body.message, "Invalid token");
});

test("POST /api/cart/add validates the payload and the product reference", async () => {
  const user = await createUser("Cart Validator");

  const missing = await request(app)
    .post("/api/cart/add")
    .set(auth(user.token))
    .send({ title: "No product id", price: 10, size: "M" });
  assert.equal(missing.status, 400);
  assert.equal(missing.body.message, "productId, title, price and size are required");

  const badReference = await addToCart(user.token, { productId: "999999" });
  assert.equal(badReference.status, 500);
});

test("cart items belong to the authenticated user, not to the request body", async () => {
  const owner = await createUser("Cart Owner");
  const other = await createUser("Other User");

  const added = await addToCart(owner.token, { userId: other.userId });
  assert.equal(added.status, 201);
  assert.equal(added.body.message, "Added to cart Sucsessfully");
  assert.equal(added.body.cartItem.userId, Number(owner.userId));

  const ownerCart = await request(app).get("/api/cart").set(auth(owner.token));
  assert.equal(ownerCart.body.length, 1);
  assert.equal(ownerCart.body[0].img1, PRODUCTS[0].images[0]);

  const otherCart = await request(app).get("/api/cart").set(auth(other.token));
  assert.equal(otherCart.body.length, 0);
});

test("cart quantity can be updated and items can be removed", async () => {
  const user = await createUser("Cart Editor");
  const added = await addToCart(user.token);
  const cartId = added.body.cartItem._id;

  const invalid = await request(app)
    .put(`/api/cart/update/${cartId}`)
    .set(auth(user.token))
    .send({ quantity: 0 });
  assert.equal(invalid.status, 400);
  assert.equal(invalid.body.message, "quantity must be a positive integer");

  const updated = await request(app)
    .put(`/api/cart/update/${cartId}`)
    .set(auth(user.token))
    .send({ quantity: "3" });
  assert.equal(updated.status, 200);
  assert.equal(updated.body.cartItem.quantity, 3);

  const notFoundUpdate = await request(app)
    .put("/api/cart/update/999999")
    .set(auth(user.token))
    .send({ quantity: 2 });
  assert.equal(notFoundUpdate.status, 404);
  assert.equal(notFoundUpdate.body.message, "Cart is not found");

  const removed = await request(app)
    .delete(`/api/cart/remove/${cartId}`)
    .set(auth(user.token));
  assert.equal(removed.status, 200);
  assert.equal(removed.body.message, "Product removed from cart");

  const notFoundRemove = await request(app)
    .delete("/api/cart/remove/999999")
    .set(auth(user.token));
  assert.equal(notFoundRemove.status, 404);

  const cart = await request(app).get("/api/cart").set(auth(user.token));
  assert.equal(cart.body.length, 0);
});

test("orders require authentication and at least one product", async () => {
  const anonymous = await request(app).post("/api/orders/create").send({ products: [] });
  assert.equal(anonymous.status, 401);

  const user = await createUser("Order Validator");
  const missingProducts = await request(app)
    .post("/api/orders/create")
    .set(auth(user.token))
    .send({ products: [] });
  assert.equal(missingProducts.status, 400);
  assert.equal(missingProducts.body.message, "must contain products");

  const missingTotal = await request(app)
    .post("/api/orders/create")
    .set(auth(user.token))
    .send({ products: [{ title: "No total" }] });
  assert.equal(missingTotal.status, 500);
});

test("orders are created for the JWT user and returned as parsed JSON", async () => {
  const user = await createUser("Order Creator");
  const created = await request(app)
    .post("/api/orders/create")
    .set(auth(user.token))
    .send({
      userId: "999999",
      totalPrice: 25,
      shippingAddress: "12 Main Street, Springfield, 123456",
      products: [
        {
          productId: "1",
          title: PRODUCTS[0].title,
          img1: PRODUCTS[0].images[0],
          quantity: 1,
          price: 25,
        },
      ],
    });

  assert.equal(created.status, 201);
  assert.equal(created.body.message, "Order added successfully");
  assert.equal(created.body.order.userId, Number(user.userId));
  assert.equal(created.body.order.paymentStatus, "Pending");
  assert.equal(created.body.order.orderStatus, "Pending");
  assert.deepEqual(created.body.order.products[0].images, PRODUCTS[0].images);

  const orders = await request(app).get("/api/orders/get").set(auth(user.token));
  assert.equal(orders.status, 200);
  assert.equal(orders.body.length, 1);
  assert.equal(orders.body[0]._id, String(created.body.order.id));
  assert.equal(orders.body[0].totalPrice, 25);
});
