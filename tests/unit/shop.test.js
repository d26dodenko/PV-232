import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { DatabaseSync } from 'node:sqlite';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createShop, credentials, quantity, text } from '../../back/shop.js';

let shop;
const user = { fullName: 'Bogdan', email: 'student@example.com', password: 'Password123' };
beforeEach(() => { shop = createShop(); });
afterEach(() => { shop.close(); vi.restoreAllMocks(); });
function account(email = user.email) {
  shop.register({ ...user, email });
  return shop.authenticate(shop.login({ ...user, email }).token);
}
const item = { productId: '1', size: 'M', quantity: 1 };

describe('Input validation', () => {
  it.each([undefined, null, 1, '', ' ', 'a'.repeat(201)])('rejects invalid text %s', (value) => {
    expect(() => text(value, 'name')).toThrow('Invalid field');
  });
  it('trims whitespace and accepts length boundaries', () => {
    expect(text(' ab ', 'name', 2, 2)).toBe('ab');
  });
  it('normalizes email', () => {
    expect(credentials({ ...user, email: ' STUDENT@example.com ' }).email).toBe(user.email);
  });
  it.each(['abc', 'a@b', '@a.ru', 'a b@c.ru'])('rejects invalid email %s', (email) => {
    expect(() => credentials({ ...user, email })).toThrow('Invalid email');
  });
  it.each(['short', 'x'.repeat(129)])('validates password length %s', (password) => {
    expect(() => credentials({ ...user, password })).toThrow('password');
  });
  it.each([0, -1, 100, 1.5, '1', null])('rejects invalid quantity %s', (value) => {
    expect(() => quantity(value)).toThrow('Quantity');
  });
  it.each([1, 99])('accepts quantity boundary %s', (value) => expect(quantity(value)).toBe(value));
});

describe('Catalog, account and session', () => {
  it('returns the catalog and searches without case sensitivity', () => {
    expect(shop.products()).toHaveLength(4);
    expect(shop.products(' DENIM ')).toEqual([shop.getProduct('2')]);
    expect(shop.products('absent')).toEqual([]);
  });
  it('rejects an unknown product', () => expect(() => shop.getProduct('404')).toThrow('Product not found'));
  it('creates an account and issues distinct tokens', () => {
    shop.register(user);
    const first = shop.login(user);
    const second = shop.login(user);
    expect(first.userName).toBe('Bogdan');
    expect(first.token).not.toBe(second.token);
    expect(shop.authenticate(first.token)).toBe(1);
  });
  it('rejects duplicate registration', () => {
    shop.register(user);
    expect(() => shop.register({ ...user, email: 'STUDENT@example.com' })).toThrow('Email is already registered');
  });
  it('validates the name', () => expect(() => shop.register({ ...user, fullName: 'a' })).toThrow('name'));
  it('rejects an unknown account', () => expect(() => shop.login(user)).toThrow('Invalid email or password'));
  it('rejects an incorrect password', () => {
    shop.register(user);
    expect(() => shop.login({ ...user, password: 'wrongpass' })).toThrow('Invalid email or password');
  });
  it('revokes the session on sign out', () => {
    shop.register(user);
    const { token } = shop.login(user);
    expect(shop.logout(token).message).toBe('Signed out');
    expect(() => shop.authenticate(token)).toThrow('Please sign in');
  });
  it('rejects an expired session', () => {
    shop.register(user);
    const { token } = shop.login(user);
    vi.spyOn(Date, 'now').mockReturnValue(Date.now() + 86400001);
    expect(() => shop.authenticate(token)).toThrow('Please sign in');
  });
});

describe('Cart and orders', () => {
  it('merges matching items and keeps sizes separate', () => {
    const id = account();
    shop.add(id, item);
    shop.add(id, { ...item, quantity: 2 });
    shop.add(id, { ...item, size: 'L' });
    expect(shop.cart(id).map((row) => row.quantity)).toEqual([1, 3]);
  });
  it('ignores client supplied prices and user IDs', () => {
    const id = account();
    expect(shop.add(id, { ...item, price: 1, userId: 999 })[0].price).toBe(1200);
  });
  it('rejects an unknown product or size', () => {
    const id = account();
    expect(() => shop.add(id, { ...item, productId: '404' })).toThrow('Product not found');
    expect(() => shop.add(id, { ...item, size: 'XXS' })).toThrow('Select a size');
  });
  it('enforces the total quantity limit', () => {
    const id = account();
    shop.add(id, { ...item, quantity: 99 });
    expect(() => shop.add(id, item)).toThrow('Quantity');
    expect(shop.cart(id)[0].quantity).toBe(99);
  });
  it('removes only items owned by the user', () => {
    const id = account();
    const other = account('other@example.com');
    shop.add(id, item);
    expect(() => shop.remove(other, '1', 'M')).toThrow('Cart item not found');
    expect(shop.cart(id)).toHaveLength(1);
    expect(shop.remove(id, '1', 'M')).toEqual([]);
  });
  it('isolates carts and order history', () => {
    const id = account();
    const other = account('other@example.com');
    shop.add(id, item);
    shop.checkout(id, { shippingAddress: '10 Lesnaya Street, Moscow' });
    expect(shop.orders(other)).toEqual([]);
    expect(shop.cart(other)).toEqual([]);
  });
  it('calculates the total, saves the address and clears the cart', () => {
    const id = account();
    shop.add(id, { ...item, quantity: 2 });
    shop.add(id, { productId: '2', size: 'XL', quantity: 1 });
    const order = shop.checkout(id, { shippingAddress: ' 10 Lesnaya Street, Moscow ', totalPrice: 1 });
    expect(order).toMatchObject({ id: 1, totalPrice: 6900, shippingAddress: '10 Lesnaya Street, Moscow' });
    expect(shop.orders(id)[0]).toEqual(order);
    expect(shop.cart(id)).toEqual([]);
  });
  it('rejects an empty order', () => {
    expect(() => shop.checkout(account(), { shippingAddress: '10 Lesnaya Street, Moscow' })).toThrow('Your cart is empty');
  });
  it('rejects a short address and preserves the cart', () => {
    const id = account();
    shop.add(id, item);
    expect(() => shop.checkout(id, { shippingAddress: 'Moscow' })).toThrow('address');
    expect(shop.cart(id)).toHaveLength(1);
  });
  it('preserves data after reopening the database', () => {
    const dir = mkdtempSync(join(tmpdir(), 'clothify-'));
    const filename = join(dir, 'shop.sqlite');
    const first = createShop(filename);
    first.register(user);
    const token = first.login(user).token;
    first.add(first.authenticate(token), item);
    first.close();
    const second = createShop(filename);
    try {
      expect(second.cart(second.authenticate(token))).toHaveLength(1);
      const db = new DatabaseSync(filename);
      const saved = db.prepare('SELECT hash, salt FROM users').get();
      db.close();
      expect(saved.hash).not.toContain(user.password);
      expect(saved.salt).toHaveLength(32);
    } finally {
      second.close();
      rmSync(dir, { recursive: true });
    }
  });
  it('rolls back the transaction when a write fails', () => {
    const dir = mkdtempSync(join(tmpdir(), 'clothify-rollback-'));
    const filename = join(dir, 'shop.sqlite');
    const broken = createShop(filename);
    broken.register(user);
    const id = broken.authenticate(broken.login(user).token);
    broken.add(id, item);
    const db = new DatabaseSync(filename);
    db.exec("CREATE TRIGGER fail_order BEFORE INSERT ON orders BEGIN SELECT RAISE(ABORT, 'disk failure'); END;");
    db.close();
    try {
      expect(() => broken.checkout(id, { shippingAddress: '10 Lesnaya Street, Moscow' })).toThrow('disk failure');
      expect(broken.cart(id)).toHaveLength(1);
      expect(broken.orders(id)).toEqual([]);
    } finally {
      broken.close();
      rmSync(dir, { recursive: true });
    }
  });
});
