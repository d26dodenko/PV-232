import { expect, test } from "@playwright/test";
import { createAuthenticatedUser } from "./helpers/user";
import { LoginPage } from "./pages/LoginPage";

test.describe("Login", () => {
  test("logs in through the UI and stores the session", async ({ page, request }) => {
    const user = await createAuthenticatedUser(request);

    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);

    await loginPage.expectLoginSuccess();
    await expect(page).toHaveURL(/\/$/);
    const session = await page.evaluate(() => ({
      token: localStorage.getItem("token"),
      userId: localStorage.getItem("userId"),
    }));
    expect(session.token).toBeTruthy();
    expect(session.userId).toBe(user.userId);
  });

  test("rejects an incorrect password", async ({ page, request }) => {
    const user = await createAuthenticatedUser(request);
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.login(user.email, "WrongPassword123!");

    await loginPage.expectError("Login failed");
    await expect(page).toHaveURL(/\/login$/);
    expect(await page.evaluate(() => localStorage.getItem("token"))).toBeNull();
  });

  test("redirects an anonymous user from a protected route to login", async ({ page }) => {
    await page.goto("/cart");
    await expect(page).toHaveURL(/\/login$/);
  });
});
