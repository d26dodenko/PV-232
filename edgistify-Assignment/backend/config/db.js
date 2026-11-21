const fs = require("fs");
const path = require("path");
const Database = require("better-sqlite3");

require("dotenv").config({ path: path.join(__dirname, "..", ".env") });

const dbPath =
  process.env.DB_PATH || path.join(__dirname, "..", "data", "shop.db");

if (dbPath !== ":memory:") {
  fs.mkdirSync(path.dirname(dbPath), { recursive: true });
}

const db = new Database(dbPath);

db.pragma("journal_mode = WAL");
db.pragma("foreign_keys = ON");

db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullName TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    createdAt TEXT NOT NULL DEFAULT (datetime('now')),
    updatedAt TEXT NOT NULL DEFAULT (datetime('now'))
  );

  CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    brand TEXT NOT NULL,
    price REAL NOT NULL,
    rating REAL NOT NULL DEFAULT 0,
    images TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    size TEXT NOT NULL,
    createdAt TEXT NOT NULL DEFAULT (datetime('now')),
    updatedAt TEXT NOT NULL DEFAULT (datetime('now'))
  );

  CREATE TABLE IF NOT EXISTS carts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userId INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    productId INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    images TEXT NOT NULL,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    size TEXT NOT NULL,
    createdAt TEXT NOT NULL DEFAULT (datetime('now')),
    updatedAt TEXT NOT NULL DEFAULT (datetime('now'))
  );

  CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userId INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    products TEXT NOT NULL,
    totalPrice REAL NOT NULL,
    shippingAddress TEXT NOT NULL,
    paymentStatus TEXT NOT NULL DEFAULT 'Pending'
      CHECK (paymentStatus IN ('Pending', 'Paid', 'Failed')),
    orderStatus TEXT NOT NULL DEFAULT 'Pending'
      CHECK (orderStatus IN ('Pending', 'Processing', 'Shipped', 'Delivered')),
    createdAt TEXT NOT NULL DEFAULT (datetime('now')),
    updatedAt TEXT NOT NULL DEFAULT (datetime('now'))
  );

  CREATE INDEX IF NOT EXISTS idx_carts_userId ON carts(userId);
  CREATE INDEX IF NOT EXISTS idx_orders_userId ON orders(userId);
`);

const PORT = process.env.PORT || 3000;

module.exports = { db, PORT };