import { Page, Locator } from '@playwright/test';

export class ProductPage {
  readonly page: Page;
  readonly searchInput: Locator;
  readonly firstProductAddToCartBtn: Locator;

  constructor(page: Page) {
    this.page = page;
    this.searchInput = page.getByPlaceholder('Search products...');
    this.firstProductAddToCartBtn = page.locator('.product-card').first().getByRole('button', { name: 'Add to Cart' });
  }

  async search(query: string) {
    await this.searchInput.fill(query);
    await this.searchInput.press('Enter');
    await this.page.waitForLoadState('networkidle');
  }

  async addFirstProductToCart() {
    await this.firstProductAddToCartBtn.click();
  }
}