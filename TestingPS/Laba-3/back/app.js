import express from 'express';
import { ShopError } from './shop.js';

export function createApp(shop) {
  const app = express();
  app.disable('x-powered-by');
  app.use(express.json({ limit: '16kb' }));
  app.use((req, res, next) => {
    res.set('X-Content-Type-Options', 'nosniff');
    next();
  });
  app.get('/api/health', (req, res) => res.json({ status: 'ok' }));
  app.get('/api/products', (req, res) => res.json(shop.products(req.query.q)));
  app.get('/api/products/:id', (req, res) => res.json(shop.getProduct(req.params.id)));
  app.post('/api/users/register', (req, res) => res.status(201).json(shop.register(req.body)));
  app.post('/api/users/login', (req, res) => res.json(shop.login(req.body)));
  app.use('/api', (req, res, next) => {
    req.token = req.get('authorization')?.replace(/^Bearer /, '') ?? '';
    req.userId = shop.authenticate(req.token);
    next();
  });
  app.post('/api/users/logout', (req, res) => res.json(shop.logout(req.token)));
  app.get('/api/cart', (req, res) => res.json(shop.cart(req.userId)));
  app.post('/api/cart/add', (req, res) => res.status(201).json(shop.add(req.userId, req.body)));
  app.delete('/api/cart/:id/:size', (req, res) => res.json(shop.remove(req.userId, req.params.id, req.params.size)));
  app.post('/api/orders/create', (req, res) => res.status(201).json(shop.checkout(req.userId, req.body)));
  app.get('/api/orders/get', (req, res) => res.json(shop.orders(req.userId)));
  app.use((req, res) => res.status(404).json({ message: 'Route not found' }));
  app.use((error, req, res, next) => {
    if (res.headersSent) return next(error);
    const status = error instanceof ShopError ? error.status : error.status === 400 ? 400 : 500;
    res.status(status).json({ message: status === 500 ? 'Internal server error' : error.message });
  });
  return app;
}
