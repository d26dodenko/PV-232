import { Locator, Page } from "@playwright/test";

export class NavbarComponent {
  readonly logoutButton: Locator;
  readonly loginLink: Locator;
  readonly cartLink: Locator;
  readonly productsLink: Locator;

  constructor(page: Page) {
    const nav = page.locator("nav");
    this.logoutButton = nav.getByRole("button", { name: "Logout" });
    this.loginLink = nav.getByRole("link", { name: "Login" });
    this.cartLink = nav.getByRole("link", { name: "Cart" });
    this.productsLink = nav.getByRole("link", { name: "Products" });
  }

  async logout(): Promise<void> {
    await this.logoutButton.click();
  }

  async openCart(): Promise<void> {
    await this.cartLink.click();
  }

  async openProducts(): Promise<void> {
    await this.productsLink.click();
  }
}
