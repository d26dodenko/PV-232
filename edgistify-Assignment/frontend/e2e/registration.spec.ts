import { expect, test } from "@playwright/test";
import { registerViaApi, uniqueUser } from "./helpers/user";
import { LoginPage } from "./pages/LoginPage";
import { SignupPage } from "./pages/SignupPage";

test.describe("Registration", () => {
  test("registers a new user and redirects to the login page", async ({ page }) => {
    const user = uniqueUser();
    const signupPage = new SignupPage(page);

    await signupPage.goto();
    await signupPage.register(user.fullName, user.email, user.password);
    await signupPage.expectSignupSuccess();
    await expect(page).toHaveURL(/\/login$/);

    const loginPage = new LoginPage(page);
    await loginPage.login(user.email, user.password);
    await loginPage.expectLoginSuccess();
    await expect(page).toHaveURL(/\/$/);
  });

  test("shows an error when the email is already registered", async ({ page, request }) => {
    const user = uniqueUser();
    await registerViaApi(request, user);
    const signupPage = new SignupPage(page);

    await signupPage.goto();
    await signupPage.register(user.fullName, user.email, user.password);

    await signupPage.expectDuplicateEmailError();
    await expect(page).toHaveURL(/\/signup$/);
  });
});
