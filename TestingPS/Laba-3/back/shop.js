import { randomBytes, scryptSync, timingSafeEqual } from 'node:crypto';
import { DatabaseSync } from 'node:sqlite';

export class ShopError extends Error {
  constructor(message, status = 400) {
    super(message);
    this.status = status;
  }
}

export function text(value, name, min = 1, max = 200) {
  if (typeof value !== 'string' || value.trim().length < min || value.trim().length > max) {
    throw new ShopError(`Invalid field: ${name}`);
  }
  return value.trim();
}

export function credentials(data) {
  const email = text(data.email, 'email').toLowerCase();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) throw new ShopError('Invalid email');
  const password = text(data.password, 'password', 8, 128);
  return { email, password };
}

export function quantity(value) {
  if (!Number.isInteger(value) || value < 1 || value > 99) throw new ShopError('Quantity must be between 1 and 99');
  return value;
}

export const products = [
  { _id: '1', title: 'Cotton T-shirt', price: 1200, sizes: ['S', 'M', 'L'], brand: 'Clothify', color: '#e1c9b4' },
  { _id: '2', title: 'Denim Jacket', price: 4500, sizes: ['M', 'L', 'XL'], brand: 'Clothify', color: '#aac2ce' },
  { _id: '3', title: 'Classic Hoodie', price: 2800, sizes: ['S', 'M', 'L'], brand: 'Clothify', color: '#b8c5ad' },
  { _id: '4', title: 'Linen Shirt', price: 2400, sizes: ['S', 'M', 'XL'], brand: 'Clothify', color: '#e7deca' },
];

export function createShop(filename = ':memory:') {
  const db = new DatabaseSync(filename);
  db.exec(`
    PRAGMA foreign_keys = ON;
    CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, fullName TEXT NOT NULL, email TEXT UNIQUE NOT NULL, salt TEXT NOT NULL, hash TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, userId INTEGER NOT NULL REFERENCES users(id), expires INTEGER NOT NULL);
    CREATE TABLE IF NOT EXISTS cart (userId INTEGER NOT NULL REFERENCES users(id), productId TEXT NOT NULL, size TEXT NOT NULL, quantity INTEGER NOT NULL, PRIMARY KEY(userId, productId, size));
    CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, userId INTEGER NOT NULL REFERENCES users(id), products TEXT NOT NULL, totalPrice INTEGER NOT NULL, shippingAddress TEXT NOT NULL);
  `);
  const run = (sql, ...params) => db.prepare(sql).run(...params);
  const one = (sql, ...params) => db.prepare(sql).get(...params);
  const all = (sql, ...params) => db.prepare(sql).all(...params);
  const getProduct = (id) => {
    const product = products.find((item) => item._id === id);
    if (!product) throw new ShopError('Product not found', 404);
    return product;
  };
  const cart = (userId) => all('SELECT productId, size, quantity FROM cart WHERE userId = ? ORDER BY productId, size', userId)
    .map((item) => ({ ...getProduct(item.productId), ...item }));
  return {
    close: () => db.close(),
    products: (search = '') => products.filter((item) => item.title.toLowerCase().includes(text(search || ' ', 'search', 0).toLowerCase())),
    getProduct,
    register(data) {
      const { email, password } = credentials(data);
      const fullName = text(data.fullName, 'name', 2, 80);
      if (one('SELECT id FROM users WHERE email = ?', email)) throw new ShopError('Email is already registered', 409);
      const salt = randomBytes(16).toString('hex');
      const hash = scryptSync(password, salt, 64).toString('hex');
      run('INSERT INTO users (fullName, email, salt, hash) VALUES (?, ?, ?, ?)', fullName, email, salt, hash);
      return { message: 'Registration complete' };
    },
    login(data) {
      const { email, password } = credentials(data);
      const user = one('SELECT * FROM users WHERE email = ?', email);
      if (!user || !timingSafeEqual(scryptSync(password, user.salt, 64), Buffer.from(user.hash, 'hex'))) {
        throw new ShopError('Invalid email or password', 401);
      }
      const token = randomBytes(32).toString('hex');
      run('INSERT INTO sessions VALUES (?, ?, ?)', token, user.id, Date.now() + 86400000);
      return { token, userName: user.fullName };
    },
    authenticate(token) {
      const session = one('SELECT userId, expires FROM sessions WHERE token = ?', token);
      if (!session || session.expires <= Date.now()) throw new ShopError('Please sign in', 401);
      return session.userId;
    },
    logout(token) {
      run('DELETE FROM sessions WHERE token = ?', token);
      return { message: 'Signed out' };
    },
    cart,
    add(userId, data) {
      const product = getProduct(data.productId);
      if (!product.sizes.includes(data.size)) throw new ShopError('Select a size');
      const count = quantity(data.quantity);
      const previous = one('SELECT quantity FROM cart WHERE userId = ? AND productId = ? AND size = ?', userId, product._id, data.size);
      const total = quantity((previous?.quantity ?? 0) + count);
      run('INSERT INTO cart VALUES (?, ?, ?, ?) ON CONFLICT(userId, productId, size) DO UPDATE SET quantity = excluded.quantity', userId, product._id, data.size, total);
      return cart(userId);
    },
    remove(userId, productId, size) {
      const result = run('DELETE FROM cart WHERE userId = ? AND productId = ? AND size = ?', userId, productId, size);
      if (!result.changes) throw new ShopError('Cart item not found', 404);
      return cart(userId);
    },
    checkout(userId, data) {
      const shippingAddress = text(data.shippingAddress, 'address', 10, 300);
      const items = cart(userId);
      if (!items.length) throw new ShopError('Your cart is empty');
      const totalPrice = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
      db.exec('BEGIN');
      try {
        const result = run('INSERT INTO orders (userId, products, totalPrice, shippingAddress) VALUES (?, ?, ?, ?)', userId, JSON.stringify(items), totalPrice, shippingAddress);
        run('DELETE FROM cart WHERE userId = ?', userId);
        db.exec('COMMIT');
        return { id: Number(result.lastInsertRowid), products: items, totalPrice, shippingAddress };
      } catch (error) {
        db.exec('ROLLBACK');
        throw error;
      }
    },
    orders: (userId) => all('SELECT id, products, totalPrice, shippingAddress FROM orders WHERE userId = ? ORDER BY id DESC', userId)
      .map((order) => ({ ...order, products: JSON.parse(order.products) })),
  };
}
