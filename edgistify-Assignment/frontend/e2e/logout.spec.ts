import { expect, test } from "@playwright/test";
import { createAuthenticatedUser } from "./helpers/user";
import { LoginPage } from "./pages/LoginPage";
import { NavbarComponent } from "./pages/NavbarComponent";

test.describe("Logout", () => {
  test("clears the token and redirects to login", async ({ page, request }) => {
    const user = await createAuthenticatedUser(request);

    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await expect(page).toHaveURL(/\/$/);

    const navbar = new NavbarComponent(page);
    await navbar.logout();

    await expect(page).toHaveURL(/\/login$/);
    expect(await page.evaluate(() => localStorage.getItem("token"))).toBeNull();
    await expect(navbar.loginLink).toBeVisible();
    await expect(navbar.logoutButton).toHaveCount(0);

    await page.goto("/cart");
    await expect(page).toHaveURL(/\/login$/);
  });
});
