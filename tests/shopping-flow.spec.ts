import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { ProductPage } from '../pages/ProductPage';

test.describe('User Shopping Journey', () => {
  test('Login, Search, Add to Cart, and Logout', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const productPage = new ProductPage(page);

    // 1. Login
    await loginPage.goto();
    await loginPage.login('testuser', 'password123');
    await expect(page).toHaveURL(/dashboard/);

    // 2. Search for a product
    await productPage.search('laptop');
    await expect(page.locator('.product-card')).not.toHaveCount(0);

    // 3. Add to Cart
    await productPage.addFirstProductToCart();
    await expect(page.locator('.cart-badge')).toHaveText('1');

    // 4. Logout
    await page.getByRole('button', { name: 'Logout' }).click();
    await expect(page).toHaveURL(/login/);
  });
});