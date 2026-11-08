import { beforeEach, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import App, { Auth, Cart, Checkout, Orders, Products } from '../../front/src/App.jsx';
import { api } from '../../front/src/api.js';

vi.mock('../../front/src/api.js', () => ({ api: vi.fn() }));
const product = { _id: '1', title: 'Cotton T-shirt', price: 1200, sizes: ['S', 'M'], brand: 'Clothify', color: '#ccc' };
const jacket = { ...product, _id: '2', title: 'Denim Jacket' };
const item = { ...product, productId: '1', size: 'M', quantity: 2 };
const notify = vi.fn();
beforeEach(() => { api.mockReset(); notify.mockReset(); });
function mount(element, path = '/') { return render(<MemoryRouter initialEntries={[path]}>{element}</MemoryRouter>); }
async function fillAuth(register = false) {
  const user = userEvent.setup();
  if (register) await user.type(screen.getByLabelText('Full name'), 'Bogdan');
  await user.type(screen.getByLabelText('Email'), 'student@example.com');
  await user.type(screen.getByLabelText('Password'), 'Password123');
  await user.click(screen.getByRole('button', { name: register ? 'Create account' : 'Sign in' }));
}

it('renders the catalog, filters products and shows an empty result', async () => {
  api.mockResolvedValue([product, jacket]);
  mount(<Products notify={notify} />);
  expect(await screen.findByText('Cotton T-shirt')).toBeVisible();
  const user = userEvent.setup();
  await user.type(screen.getByLabelText('Search products'), ' DENIM ');
  expect(screen.queryByText('Cotton T-shirt')).not.toBeInTheDocument();
  expect(screen.getByText('Denim Jacket')).toBeVisible();
  await user.type(screen.getByLabelText('Search products'), '404');
  expect(screen.getByText('No products found')).toBeVisible();
});
it('adds selected and default sizes', async () => {
  localStorage.setItem('token', 'session');
  api.mockResolvedValueOnce([product]).mockResolvedValue([]);
  mount(<Products notify={notify} />);
  const user = userEvent.setup();
  await user.click(await screen.findByRole('button', { name: 'Add to cart' }));
  expect(api).toHaveBeenLastCalledWith('/cart/add', { method: 'POST', body: { productId: '1', quantity: 1, size: 'S' } });
  await user.selectOptions(screen.getByLabelText('Size Cotton T-shirt'), 'M');
  await user.click(screen.getByRole('button', { name: 'Add to cart' }));
  expect(api.mock.calls.at(-1)[1].body.size).toBe('M');
  expect(notify).toHaveBeenCalledWith('Product added to cart');
});
it('redirects guests to sign in when adding an item', async () => {
  api.mockResolvedValue([product]);
  mount(<App />);
  await userEvent.click(await screen.findByRole('button', { name: 'Add to cart' }));
  expect(screen.getByRole('heading', { name: 'Sign in' })).toBeVisible();
});
it('displays catalog and add item errors', async () => {
  api.mockRejectedValueOnce(new Error('Catalog unavailable'));
  const first = mount(<Products notify={notify} />);
  await waitFor(() => expect(notify).toHaveBeenCalledWith('Catalog unavailable'));
  first.unmount();
  localStorage.setItem('token', 'session');
  api.mockResolvedValueOnce([product]).mockRejectedValueOnce(new Error('Failed to add product'));
  mount(<Products notify={notify} />);
  await userEvent.click(await screen.findByRole('button', { name: 'Add to cart' }));
  expect(notify).toHaveBeenCalledWith('Failed to add product');
});
it('submits registration and redirects to sign in', async () => {
  api.mockResolvedValue({ message: 'Registration complete' });
  mount(<App />, '/signup');
  await fillAuth(true);
  expect(api).toHaveBeenCalledWith('/users/register', { method: 'POST', body: { fullName: 'Bogdan', email: 'student@example.com', password: 'Password123' } });
  expect(screen.getByRole('heading', { name: 'Sign in' })).toBeVisible();
  expect(screen.getByRole('alert')).toHaveTextContent('Registration complete');
});
it('stores the session after sign in', async () => {
  api.mockResolvedValueOnce({ token: 'session', userName: 'Bogdan' }).mockResolvedValue([product]);
  mount(<App />, '/login');
  await fillAuth();
  expect(localStorage.getItem('token')).toBe('session');
  expect(screen.getByText('Bogdan')).toBeVisible();
  expect(await screen.findByText('Cotton T-shirt')).toBeVisible();
});
it('displays sign in errors and enables the submit button', async () => {
  api.mockRejectedValue(new Error('Incorrect password'));
  mount(<Auth notify={notify} onLogin={vi.fn()} />);
  await fillAuth();
  expect(notify).toHaveBeenCalledWith('Incorrect password');
  expect(screen.getByRole('button', { name: 'Sign in' })).toBeEnabled();
});
it('renders the cart total and removes an item', async () => {
  api.mockResolvedValueOnce([item]).mockResolvedValueOnce([]);
  mount(<Cart notify={notify} />);
  expect(await screen.findByText('Total: 2400 ₽')).toBeVisible();
  expect(screen.getByText('Size: M · Quantity: 2')).toBeVisible();
  await userEvent.click(screen.getByRole('button', { name: 'Remove Cotton T-shirt' }));
  expect(api).toHaveBeenLastCalledWith('/cart/1/M', { method: 'DELETE' });
  expect(screen.getByText('Your cart is empty')).toBeVisible();
});
it('displays cart loading and removal errors', async () => {
  api.mockRejectedValueOnce(new Error('Cart unavailable'));
  const first = mount(<Cart notify={notify} />);
  await waitFor(() => expect(notify).toHaveBeenCalledWith('Cart unavailable'));
  first.unmount();
  api.mockResolvedValueOnce([item]).mockRejectedValueOnce(new Error('Failed to remove item'));
  mount(<Cart notify={notify} />);
  await userEvent.click(await screen.findByRole('button', { name: 'Remove Cotton T-shirt' }));
  expect(notify).toHaveBeenCalledWith('Failed to remove item');
});
it('submits the address and displays order history', async () => {
  localStorage.setItem('token', 'session');
  api.mockResolvedValueOnce({ id: 1 }).mockResolvedValueOnce([{ id: 1, products: [item], totalPrice: 2400, shippingAddress: '10 Lesnaya Street, Moscow' }]);
  mount(<App />, '/checkout');
  const user = userEvent.setup();
  await user.type(screen.getByLabelText('Shipping address'), '10 Lesnaya Street, Moscow');
  await user.click(screen.getByRole('button', { name: 'Place order' }));
  expect(api).toHaveBeenCalledWith('/orders/create', { method: 'POST', body: { shippingAddress: '10 Lesnaya Street, Moscow' } });
  expect(await screen.findByText('Order #1')).toBeVisible();
  expect(screen.getByText('Cotton T-shirt (M) × 2')).toBeVisible();
});
it('displays checkout errors and enables the submit button', async () => {
  api.mockRejectedValue(new Error('Your cart is empty'));
  mount(<Checkout notify={notify} />);
  await userEvent.type(screen.getByLabelText('Shipping address'), '10 Lesnaya Street, Moscow');
  await userEvent.click(screen.getByRole('button', { name: 'Place order' }));
  expect(notify).toHaveBeenCalledWith('Your cart is empty');
  expect(screen.getByRole('button')).toBeEnabled();
});
it('displays empty order history and loading errors', async () => {
  api.mockResolvedValueOnce([]);
  const first = mount(<Orders notify={notify} />);
  expect(await screen.findByText('No orders yet')).toBeVisible();
  first.unmount();
  api.mockRejectedValueOnce(new Error('Order history unavailable'));
  mount(<Orders notify={notify} />);
  await waitFor(() => expect(notify).toHaveBeenCalledWith('Order history unavailable'));
});
it('protects cart, checkout and order history from guests', async () => {
  for (const path of ['/cart', '/checkout', '/placed']) {
    const view = mount(<App />, path);
    expect(await screen.findByRole('heading', { name: 'Sign in' })).toBeVisible();
    view.unmount();
  }
});
it('signs out, clears the session and protects the cart', async () => {
  localStorage.setItem('token', 'session');
  localStorage.setItem('userName', 'Bogdan');
  api.mockResolvedValue([]);
  mount(<App />);
  await userEvent.click(screen.getByRole('button', { name: 'Sign out' }));
  expect(api).toHaveBeenCalledWith('/users/logout', { method: 'POST' });
  expect(localStorage.getItem('token')).toBeNull();
  expect(screen.getByRole('heading', { name: 'Sign in' })).toBeVisible();
});
it('preserves the session when sign out fails', async () => {
  localStorage.setItem('token', 'session');
  localStorage.setItem('userName', 'Bogdan');
  api.mockResolvedValueOnce([]).mockRejectedValueOnce(new Error('Network unavailable'));
  mount(<App />);
  await userEvent.click(screen.getByRole('button', { name: 'Sign out' }));
  expect(screen.getByRole('alert')).toHaveTextContent('Network unavailable');
  expect(localStorage.getItem('token')).toBe('session');
});
it('renders the page not found screen', () => {
  mount(<App />, '/missing');
  expect(screen.getByRole('heading', { name: 'Page not found' })).toBeVisible();
});
