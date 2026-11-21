import { expect, Locator, Page } from "@playwright/test";
import { BasePage } from "./BasePage";

export class ProductDetailsPage extends BasePage {
  readonly addToCartButton: Locator;
  readonly quantity: Locator;

  constructor(page: Page) {
    super(page);
    this.addToCartButton = page.getByRole("button", { name: "Add to Cart" });
    this.quantity = page.locator("span.px-4.text-teal-600.font-bold");
  }

  async expectLoaded(title: string): Promise<void> {
    await expect(this.page.getByRole("heading", { level: 1, name: title })).toBeVisible();
  }

  async selectSize(size: string): Promise<void> {
    await this.page.getByRole("button", { name: size, exact: true }).click();
  }

  async increaseQuantity(times = 1): Promise<void> {
    for (let i = 0; i < times; i += 1) {
      await this.page.getByRole("button", { name: "+", exact: true }).click();
    }
  }

  async addToCart(): Promise<void> {
    await this.addToCartButton.click();
  }

  async expectQuantity(value: number): Promise<void> {
    await expect(this.quantity).toHaveText(String(value));
  }
}
