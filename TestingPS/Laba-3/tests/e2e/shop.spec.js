import { randomUUID } from 'node:crypto';
import { test, expect } from '@playwright/test';
import { AuthPage, CatalogPage, CartPage, CheckoutPage } from './pages/ShopPages.js';

let user;
let auth;
let catalog;
let cart;
test.beforeEach(async ({ page }) => {
  user = { fullName: 'Bogdan', email: `${randomUUID()}@example.com`, password: 'Password123' };
  auth = new AuthPage(page);
  catalog = new CatalogPage(page);
  cart = new CartPage(page);
});
async function signedIn(page) {
  await auth.register(user);
  await auth.login(user);
  await expect(page.getByRole('button', { name: 'Sign out' })).toBeVisible();
}

test('registers a new user', async ({ page }) => {
  await auth.register(user);
  await expect(page.getByRole('heading', { name: 'Sign in', exact: true })).toBeVisible();
  await expect(page.getByRole('alert')).toHaveText('Registration complete');
});
test('signs in and preserves the session after reload', async ({ page }) => {
  await signedIn(page);
  await page.reload();
  await expect(page.getByRole('navigation')).toContainText(user.fullName);
  await cart.open();
  await expect(page.getByText('Your cart is empty')).toBeVisible();
});
test('searches products and displays an empty result', async ({ page }) => {
  await catalog.open();
  await expect(page.getByRole('article')).toHaveCount(4);
  await catalog.search(' DENIM ');
  await expect(page.getByRole('article')).toHaveCount(1);
  await expect(catalog.product('Denim Jacket')).toBeVisible();
  await catalog.search('nonexistent product');
  await expect(page.getByText('No products found')).toBeVisible();
});
test('adds the selected size and removes the item from the cart', async ({ page }) => {
  await signedIn(page);
  await catalog.add('Cotton T-shirt', 'L');
  await expect(page.getByRole('alert')).toHaveText('Product added to cart');
  await cart.open();
  await expect(page.getByText('Size: L · Quantity: 1')).toBeVisible();
  await expect(page.getByText('Total: 1200 ₽')).toBeVisible();
  await cart.remove('Cotton T-shirt');
  await expect(page.getByText('Your cart is empty')).toBeVisible();
});
test('places an order, displays history and clears the cart', async ({ page }) => {
  await signedIn(page);
  await catalog.add('Denim Jacket', 'XL');
  await expect(page.getByRole('alert')).toHaveText('Product added to cart');
  await cart.open();
  await cart.checkout();
  await new CheckoutPage(page).place('10 Lesnaya Street, Moscow');
  await expect(page.getByRole('heading', { name: 'My orders' })).toBeVisible();
  await expect(page.getByText('Denim Jacket (XL) × 1')).toBeVisible();
  await expect(page.getByText('Total: 4500 ₽')).toBeVisible();
  await page.reload();
  await expect(page.getByText('10 Lesnaya Street, Moscow')).toBeVisible();
  await cart.open();
  await expect(page.getByText('Your cart is empty')).toBeVisible();
});
test('sign out revokes the token and protects private pages', async ({ page, request }) => {
  await signedIn(page);
  const token = await page.evaluate(() => localStorage.getItem('token'));
  await auth.logout();
  await expect(page.getByRole('button', { name: 'Sign out' })).toHaveCount(0);
  await page.goto('/checkout');
  await expect(page).toHaveURL(/\/login$/);
  const response = await request.get('/api/cart', { headers: { Authorization: `Bearer ${token}` } });
  expect(response.status()).toBe(401);
});
test('rejects an incorrect password', async ({ page }) => {
  await auth.register(user);
  await auth.login({ ...user, password: 'WrongPassword' });
  await expect(page.getByRole('alert')).toHaveText('Invalid email or password');
  await expect(page.getByRole('heading', { name: 'Sign in', exact: true })).toBeVisible();
});
test('displays an error for duplicate registration', async ({ page }) => {
  await auth.register(user);
  await page.goto('/signup');
  await page.getByLabel('Full name').fill(user.fullName);
  await auth.fill(user);
  await page.getByRole('button', { name: 'Create account' }).click();
  await expect(page.getByRole('alert')).toHaveText('Email is already registered');
});
