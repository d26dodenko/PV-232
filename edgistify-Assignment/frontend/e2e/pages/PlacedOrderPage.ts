import { expect, Page } from "@playwright/test";
import { BasePage } from "./BasePage";

export class PlacedOrderPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  async expectLoaded(): Promise<void> {
    await expect(
      this.page.getByRole("heading", { name: "Order Placed Successfully!" }),
    ).toBeVisible();
  }

  async expectOrderDetails(totalPrice: number, shippingAddress: string): Promise<void> {
    await expect(this.page.getByText("Order Summary")).toBeVisible();
    await expect(this.page.locator("p").filter({ hasText: "Total Price:" })).toContainText(
      `₹${totalPrice}`,
    );
    await expect(this.page.locator("p").filter({ hasText: "Shipping Address:" })).toContainText(
      shippingAddress,
    );
    await expect(this.page.locator("p").filter({ hasText: "Payment Status:" })).toContainText(
      "Pending",
    );
    await expect(this.page.locator("p").filter({ hasText: "Order Status:" })).toContainText(
      "Pending",
    );
  }

  async expectProduct(title: string, quantity: number): Promise<void> {
    await expect(this.page.getByText(title, { exact: true })).toBeVisible();
    await expect(this.page.getByText(`Quantity: ${quantity}`)).toBeVisible();
  }
}
