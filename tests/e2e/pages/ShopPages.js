export class AuthPage {
  constructor(page) { this.page = page; }
  async register(user) {
    await this.page.goto('/signup');
    await this.page.getByLabel('Full name').fill(user.fullName);
    await this.fill(user);
    await this.page.getByRole('button', { name: 'Create account' }).click();
    await this.page.waitForURL('**/login');
  }
  async fill(user) {
    await this.page.getByLabel('Email').fill(user.email);
    await this.page.getByLabel('Password').fill(user.password);
  }
  async login(user) {
    await this.page.goto('/login');
    await this.fill(user);
    await this.page.getByRole('button', { name: 'Sign in', exact: true }).click();
  }
  async logout() {
    await this.page.getByRole('button', { name: 'Sign out', exact: true }).click();
    await this.page.waitForURL('**/login');
  }
}

export class CatalogPage {
  constructor(page) { this.page = page; }
  async open() { await this.page.goto('/'); }
  async search(query) { await this.page.getByLabel('Search products').fill(query); }
  product(title) { return this.page.getByRole('article').filter({ has: this.page.getByRole('heading', { name: title, exact: true }) }); }
  async add(title, size = 'M') {
    const card = this.product(title);
    await card.getByLabel(`Size ${title}`).selectOption(size);
    await card.getByRole('button', { name: 'Add to cart' }).click();
  }
}

export class CartPage {
  constructor(page) { this.page = page; }
  async open() { await this.page.getByRole('navigation').getByRole('link', { name: 'Cart', exact: true }).click(); }
  async remove(title) { await this.page.getByRole('button', { name: `Remove ${title}` }).click(); }
  async checkout() { await this.page.getByRole('link', { name: 'Proceed to checkout' }).click(); }
}

export class CheckoutPage {
  constructor(page) { this.page = page; }
  async place(address) {
    await this.page.getByLabel('Shipping address').fill(address);
    await this.page.getByRole('button', { name: 'Place order' }).click();
  }
}
