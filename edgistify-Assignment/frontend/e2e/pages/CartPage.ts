import { expect, Locator, Page } from "@playwright/test";
import { BasePage } from "./BasePage";

export class CartPage extends BasePage {
  readonly checkoutButton: Locator;

  constructor(page: Page) {
    super(page);
    this.checkoutButton = page.getByRole("button", { name: /Proceed to Checkout/ });
  }

  async goto(): Promise<void> {
    await this.page.goto("/cart");
    await expect(this.page.getByRole("heading", { name: "Your Cart" })).toBeVisible();
  }

  itemCard(title: string): Locator {
    return this.page
      .getByRole("heading", { name: title, exact: true })
      .locator("xpath=ancestor::div[contains(@class, 'rounded-lg')][1]");
  }

  async expectItem(title: string, quantity: number): Promise<void> {
    const card = this.itemCard(title);
    await expect(card).toBeVisible();
    await expect(card).toContainText(`Qty: ${quantity}`);
  }

  async expectTotal(amount: number): Promise<void> {
    await expect(this.page.locator("p").filter({ hasText: "Total:" })).toContainText(`$ ${amount}`);
  }

  async expectEmpty(): Promise<void> {
    await expect(this.page.getByText("Your cart is empty")).toBeVisible();
  }

  async removeItem(title: string): Promise<void> {
    await this.itemCard(title).getByRole("button").click();
  }

  async proceedToCheckout(): Promise<void> {
    await this.checkoutButton.click();
  }
}
