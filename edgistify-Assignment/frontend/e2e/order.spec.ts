import { expect, test } from "@playwright/test";
import { authenticate, createAuthenticatedUser } from "./helpers/user";
import { CartPage } from "./pages/CartPage";
import { CheckoutPage, ShippingAddress } from "./pages/CheckoutPage";
import { PlacedOrderPage } from "./pages/PlacedOrderPage";
import { ProductsPage } from "./pages/ProductsPage";

const PRODUCT = { title: "Classic Cotton T-Shirt", price: 25 };
const ADDRESS: ShippingAddress = {
  firstName: "Test",
  lastName: "Customer",
  email: "customer@example.com",
  address: "12 Main Street",
  city: "Springfield",
  pinCode: "123456",
};

test.describe("Order", () => {
  test("places an order and shows the confirmation page", async ({ page, request }) => {
    const user = await createAuthenticatedUser(request);
    await authenticate(page, user);

    const productsPage = new ProductsPage(page);
    await productsPage.goto();
    await productsPage.addToCart(PRODUCT.title);

    const cartPage = new CartPage(page);
    await cartPage.goto();
    await cartPage.expectTotal(PRODUCT.price);
    await cartPage.proceedToCheckout();
    await expect(page).toHaveURL(/\/checkout$/);

    const checkoutPage = new CheckoutPage(page);
    await checkoutPage.fillShippingAddress(ADDRESS);
    await checkoutPage.expectTotal(PRODUCT.price);
    await checkoutPage.placeOrder();
    await expect(page).toHaveURL(/\/placed$/);

    const placedOrderPage = new PlacedOrderPage(page);
    await placedOrderPage.expectLoaded();
    await placedOrderPage.expectOrderDetails(
      PRODUCT.price,
      `${ADDRESS.address}, ${ADDRESS.city}, ${ADDRESS.pinCode}`,
    );
    await placedOrderPage.expectProduct(PRODUCT.title, 1);
  });

  test("does not place an order when the cart is empty", async ({ page, request }) => {
    const user = await createAuthenticatedUser(request);
    await authenticate(page, user);

    const checkoutPage = new CheckoutPage(page);
    await checkoutPage.goto();
    await checkoutPage.fillShippingAddress(ADDRESS);
    await checkoutPage.placeOrder();

    await expect(page.getByText("Your cart is empty!")).toBeVisible();
    await expect(page).toHaveURL(/\/checkout$/);
  });
});
