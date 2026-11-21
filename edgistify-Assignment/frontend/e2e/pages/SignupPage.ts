import { expect, Locator, Page } from "@playwright/test";
import { BasePage } from "./BasePage";

export class SignupPage extends BasePage {
  readonly nameInput: Locator;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly loginLink: Locator;

  constructor(page: Page) {
    super(page);
    this.nameInput = page.getByPlaceholder("Name");
    this.emailInput = page.getByPlaceholder("Email");
    this.passwordInput = page.getByPlaceholder("Password");
    this.submitButton = page.getByRole("button", { name: "Sign Up" });
    this.loginLink = page.locator("p").getByText("Login", { exact: true });
  }

  async goto(): Promise<void> {
    await this.page.goto("/signup");
    await expect(this.submitButton).toBeVisible();
  }

  async register(fullName: string, email: string, password: string): Promise<void> {
    await this.nameInput.fill(fullName);
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectSignupSuccess(): Promise<void> {
    await expect(this.page.getByText("Signup successful")).toBeVisible();
  }

  async expectDuplicateEmailError(): Promise<void> {
    await expect(this.page.getByText("Email already exists")).toBeVisible();
  }
}
