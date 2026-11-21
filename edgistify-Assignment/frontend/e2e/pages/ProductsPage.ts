import { expect, Locator, Page } from "@playwright/test";
import { BasePage } from "./BasePage";

export class ProductsPage extends BasePage {
  readonly heading: Locator;

  constructor(page: Page) {
    super(page);
    this.heading = page.getByRole("heading", { name: "Products", level: 1 });
  }

  async goto(): Promise<void> {
    await this.page.goto("/products");
    await this.expectLoaded();
  }

  async expectLoaded(): Promise<void> {
    await expect(this.heading).toBeVisible();
    await expect(this.page.locator("div.group").first()).toBeVisible();
  }

  productCard(title: string): Locator {
    return this.page
      .locator("div.group")
      .filter({ has: this.page.getByRole("heading", { name: title, exact: true }) });
  }

  async selectSize(title: string, size: string): Promise<void> {
    await this.productCard(title).locator("select").selectOption(size);
  }

  async addToCart(title: string): Promise<void> {
    await this.productCard(title).getByRole("button", { name: "Add Cart" }).click();
  }

  async openProduct(title: string): Promise<void> {
    await this.productCard(title).getByRole("link").click();
  }

  async expectAddedToCart(): Promise<void> {
    await expect(this.page.getByText("Added to cart Sucsessfully")).toBeVisible();
  }
}
