import { afterEach, beforeEach, expect, it } from 'vitest';
import request from 'supertest';
import { createApp } from '../../back/app.js';
import { createShop } from '../../back/shop.js';

let shop;
let app;
const user = { fullName: 'Bogdan', email: 'student@example.com', password: 'Password123' };
beforeEach(() => { shop = createShop(); app = createApp(shop); });
afterEach(() => shop.close());
async function login(email = user.email) {
  await request(app).post('/api/users/register').send({ ...user, email }).expect(201);
  const result = await request(app).post('/api/users/login').send({ ...user, email }).expect(200);
  return `Bearer ${result.body.token}`;
}
const item = { productId: '1', size: 'M', quantity: 2 };

it('returns API health and security headers', async () => {
  const result = await request(app).get('/api/health').expect(200);
  expect(result.body).toEqual({ status: 'ok' });
  expect(result.headers['x-content-type-options']).toBe('nosniff');
  expect(result.headers['x-powered-by']).toBeUndefined();
});
it('returns the catalog, searches and opens a product', async () => {
  const catalog = await request(app).get('/api/products').expect(200);
  expect(catalog.body).toHaveLength(4);
  const found = await request(app).get('/api/products').query({ q: 'DENIM' }).expect(200);
  expect(found.body.map((p) => p._id)).toEqual(['2']);
  const detail = await request(app).get('/api/products/2').expect(200);
  expect(detail.body.title).toBe('Denim Jacket');
  await request(app).get('/api/products/missing').expect(404);
});
it('registers users and rejects duplicates and invalid input', async () => {
  await request(app).post('/api/users/register').send(user).expect(201);
  await request(app).post('/api/users/register').send(user).expect(409);
  await request(app).post('/api/users/register').send({}).expect(400);
  await request(app).post('/api/users/login').send({ ...user, password: 'incorrect' }).expect(401);
});
it.each(['/api/cart', '/api/orders/get'])('protects %s against missing and invalid tokens', async (path) => {
  await request(app).get(path).expect(401);
  await request(app).get(path).set('Authorization', 'Bearer invalid').expect(401);
});
it('creates an order over HTTP, ignores client prices and clears the cart', async () => {
  const token = await login();
  const cart = await request(app).post('/api/cart/add').set('Authorization', token).send({ ...item, price: 1, userId: 999 }).expect(201);
  expect(cart.body[0]).toMatchObject({ price: 1200, quantity: 2 });
  const before = await request(app).get('/api/cart').set('Authorization', token).expect(200);
  expect(before.body).toHaveLength(1);
  const order = await request(app).post('/api/orders/create').set('Authorization', token).send({ shippingAddress: '10 Lesnaya Street, Moscow', totalPrice: 1 }).expect(201);
  expect(order.body.totalPrice).toBe(2400);
  const after = await request(app).get('/api/cart').set('Authorization', token).expect(200);
  expect(after.body).toEqual([]);
  const history = await request(app).get('/api/orders/get').set('Authorization', token).expect(200);
  expect(history.body).toEqual([order.body]);
});
it('isolates users when reading and removing items', async () => {
  const first = await login();
  const second = await login('second@example.com');
  await request(app).post('/api/cart/add').set('Authorization', first).send(item).expect(201);
  await request(app).delete('/api/cart/1/M').set('Authorization', second).expect(404);
  const other = await request(app).get('/api/cart').set('Authorization', second).expect(200);
  expect(other.body).toEqual([]);
  const removed = await request(app).delete('/api/cart/1/M').set('Authorization', first).expect(200);
  expect(removed.body).toEqual([]);
});
it('rejects empty orders, invalid sizes and quantities', async () => {
  const token = await login();
  for (const body of [{ ...item, size: 'XXS' }, { ...item, quantity: -1 }]) {
    await request(app).post('/api/cart/add').set('Authorization', token).send(body).expect(400);
  }
  await request(app).post('/api/orders/create').set('Authorization', token).send({ shippingAddress: '10 Lesnaya Street, Moscow' }).expect(400);
});
it('revokes the token on sign out', async () => {
  const token = await login();
  await request(app).post('/api/users/logout').set('Authorization', token).expect(200);
  await request(app).get('/api/cart').set('Authorization', token).expect(401);
});
it('handles malformed JSON', async () => {
  await request(app).post('/api/users/login').set('Content-Type', 'application/json').send('{').expect(400);
});
it('returns 404 for an unknown route when authenticated', async () => {
  const token = await login();
  await request(app).get('/api/missing').set('Authorization', token).expect(404);
});
it('hides internal database error details', async () => {
  const failed = createApp({ products() { throw new Error('secret database path'); } });
  const result = await request(failed).get('/api/products').expect(500);
  expect(result.body).toEqual({ message: 'Internal server error' });
});
