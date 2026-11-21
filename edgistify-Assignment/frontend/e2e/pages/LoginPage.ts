import { expect, Locator, Page } from "@playwright/test";
import { BasePage } from "./BasePage";

export class LoginPage extends BasePage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly signUpLink: Locator;

  constructor(page: Page) {
    super(page);
    this.emailInput = page.locator("form input[type=email]");
    this.passwordInput = page.locator("form input[type=password]");
    this.submitButton = page.getByRole("button", { name: "Login" });
    this.signUpLink = page.locator("p").getByText("Sign Up", { exact: true });
  }

  async goto(): Promise<void> {
    await this.page.goto("/login");
    await expect(this.submitButton).toBeVisible();
  }

  async login(email: string, password: string): Promise<void> {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectLoginSuccess(): Promise<void> {
    await expect(this.page.getByText("Login successful")).toBeVisible();
  }

  async expectError(message: string): Promise<void> {
    await expect(this.page.getByText(message)).toBeVisible();
  }
}
