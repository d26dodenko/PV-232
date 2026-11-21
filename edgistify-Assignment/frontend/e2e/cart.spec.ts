import { test } from "@playwright/test";
import { authenticate, createAuthenticatedUser } from "./helpers/user";
import { CartPage } from "./pages/CartPage";
import { NavbarComponent } from "./pages/NavbarComponent";
import { ProductDetailsPage } from "./pages/ProductDetailsPage";
import { ProductsPage } from "./pages/ProductsPage";

const PRODUCT = { title: "Classic Cotton T-Shirt", price: 25 };

test.describe("Cart", () => {
  test("adds a product to the cart from the catalog", async ({ page, request }) => {
    const user = await createAuthenticatedUser(request);
    await authenticate(page, user);

    const productsPage = new ProductsPage(page);
    await productsPage.goto();
    await productsPage.addToCart(PRODUCT.title);
    await productsPage.expectAddedToCart();

    const cartPage = new CartPage(page);
    await new NavbarComponent(page).openCart();
    await cartPage.expectItem(PRODUCT.title, 1);
    await cartPage.expectTotal(PRODUCT.price);
  });

  test("removes a product from the cart", async ({ page, request }) => {
    const user = await createAuthenticatedUser(request);
    await authenticate(page, user);

    const productsPage = new ProductsPage(page);
    await productsPage.goto();
    await productsPage.addToCart(PRODUCT.title);

    const cartPage = new CartPage(page);
    await cartPage.goto();
    await cartPage.expectItem(PRODUCT.title, 1);
    await cartPage.removeItem(PRODUCT.title);

    await cartPage.expectEmpty();
  });

  test("adds a product with a chosen size and quantity from the details page", async ({ page, request }) => {
    const user = await createAuthenticatedUser(request);
    await authenticate(page, user);

    const productsPage = new ProductsPage(page);
    await productsPage.goto();
    await productsPage.openProduct(PRODUCT.title);

    const productDetailsPage = new ProductDetailsPage(page);
    await productDetailsPage.expectLoaded(PRODUCT.title);
    await productDetailsPage.selectSize("M");
    await productDetailsPage.increaseQuantity(2);
    await productDetailsPage.expectQuantity(3);
    await productDetailsPage.addToCart();

    const cartPage = new CartPage(page);
    await cartPage.goto();
    await cartPage.expectItem(PRODUCT.title, 3);
    await cartPage.expectTotal(PRODUCT.price * 3);
  });
});
