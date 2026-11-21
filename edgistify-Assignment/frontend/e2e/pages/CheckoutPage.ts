import { expect, Locator, Page } from "@playwright/test";
import { BasePage } from "./BasePage";

export interface ShippingAddress {
  firstName: string;
  lastName: string;
  email: string;
  address: string;
  city: string;
  pinCode: string;
}

export class CheckoutPage extends BasePage {
  readonly placeOrderButton: Locator;

  constructor(page: Page) {
    super(page);
    this.placeOrderButton = page.getByRole("button", { name: "Place Order" });
  }

  async goto(): Promise<void> {
    await this.page.goto("/checkout");
    await expect(this.page.getByRole("heading", { name: "Checkout", level: 1 })).toBeVisible();
  }

  async fillShippingAddress(data: ShippingAddress): Promise<void> {
    await this.page.locator('input[name="firstName"]').fill(data.firstName);
    await this.page.locator('input[name="lastName"]').fill(data.lastName);
    await this.page.locator('input[name="email"]').fill(data.email);
    await this.page.locator('input[name="address"]').fill(data.address);
    await this.page.locator('input[name="city"]').fill(data.city);
    await this.page.locator('input[name="pinCode"]').fill(data.pinCode);
  }

  async expectTotal(amount: number): Promise<void> {
    await expect(this.placeOrderButton).toBeVisible();
    await expect(this.page.locator("p").filter({ hasText: "Total:" })).toContainText(`$${amount}`);
  }

  async placeOrder(): Promise<void> {
    await this.placeOrderButton.click();
  }
}
