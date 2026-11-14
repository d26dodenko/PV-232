import { useEffect, useState } from 'react';
import { Link, Route, Routes, useNavigate } from 'react-router-dom';
import { api } from './api.js';
import ProtectedRoute from './routes/ProtectedRoute.jsx';

export function Products({ notify }) {
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState('');
  const [sizes, setSizes] = useState({});
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  useEffect(() => {
    api('/products').then(setProducts).catch((error) => notify(error.message)).finally(() => setLoading(false));
  }, [notify]);
  async function add(product) {
    if (!localStorage.getItem('token')) return navigate('/login');
    try {
      await api('/cart/add', { method: 'POST', body: { productId: product._id, quantity: 1, size: sizes[product._id] || product.sizes[0] } });
      notify('Product added to cart');
    } catch (error) {
      notify(error.message);
    }
  }
  const visible = products.filter((product) => product.title.toLowerCase().includes(search.trim().toLowerCase()));
  return <>
    <div className="intro"><p className="eyebrow">CLOTHIFY / COLLECTION 2026</p><h1>Everyday clothing</h1><p>Simple essentials. Easy choices.</p></div>
    <label className="search">Search products<input type="search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="For example, Denim" /></label>
    {loading ? <p role="status">Loading products…</p> : visible.length === 0 && <p>No products found</p>}
    <div className="products">{visible.map((product) => <article key={product._id}>
      <div className="product-art" style={{ background: product.color }} aria-hidden="true">{product.title.includes('Jacket') ? '♜' : '♧'}</div>
      <div className="product-body"><small>{product.brand}</small><h2>{product.title}</h2><p>{product.price} ₽</p>
        <label>Size {product.title}<select value={sizes[product._id] || product.sizes[0]} onChange={(event) => setSizes({ ...sizes, [product._id]: event.target.value })}>{product.sizes.map((size) => <option key={size}>{size}</option>)}</select></label>
        <button onClick={() => add(product)}>Add to cart</button></div>
    </article>)}</div>
  </>;
}

export function Auth({ register = false, onLogin, notify }) {
  const navigate = useNavigate();
  const [busy, setBusy] = useState(false);
  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    const body = Object.fromEntries(new FormData(event.currentTarget));
    try {
      const data = await api(`/users/${register ? 'register' : 'login'}`, { method: 'POST', body });
      if (register) {
        notify(data.message);
        navigate('/login');
      } else {
        localStorage.setItem('token', data.token);
        localStorage.setItem('userName', data.userName);
        onLogin(data.userName);
        notify('You have signed in');
        navigate('/');
      }
    } catch (error) {
      notify(error.message);
    } finally {
      setBusy(false);
    }
  }
  return <section className="panel"><h1>{register ? 'Sign up' : 'Sign in'}</h1><form onSubmit={submit}>
    {register && <label>Full name<input name="fullName" required minLength={2} maxLength={80} autoComplete="name" /></label>}
    <label>Email<input name="email" type="email" required autoComplete="email" /></label>
    <label>Password<input name="password" type="password" required minLength={8} maxLength={128} autoComplete={register ? 'new-password' : 'current-password'} /></label>
    <button disabled={busy}>{register ? 'Create account' : 'Sign in'}</button>
  </form><Link to={register ? '/login' : '/signup'}>{register ? 'Already have an account' : 'Create account'}</Link></section>;
}

export function Cart({ notify }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api('/cart').then(setItems).catch((error) => notify(error.message)).finally(() => setLoading(false));
  }, [notify]);
  async function remove(item) {
    try {
      setItems(await api(`/cart/${item.productId}/${item.size}`, { method: 'DELETE' }));
    } catch (error) {
      notify(error.message);
    }
  }
  return <><h1>Cart</h1>{loading ? <p>Loading…</p> : items.length === 0 ? <p>Your cart is empty</p> : <>
    {items.map((item) => <article className="cart-row" key={`${item.productId}-${item.size}`}><div><h2>{item.title}</h2><p>Size: {item.size} · Quantity: {item.quantity}</p><p>{item.price * item.quantity} ₽</p></div><button onClick={() => remove(item)}>Remove {item.title}</button></article>)}
    <p>Total: {items.reduce((sum, item) => sum + item.price * item.quantity, 0)} ₽</p><Link className="button" to="/checkout">Proceed to checkout</Link>
  </>}</>;
}

export function Checkout({ notify }) {
  const navigate = useNavigate();
  const [busy, setBusy] = useState(false);
  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    try {
      await api('/orders/create', { method: 'POST', body: Object.fromEntries(new FormData(event.currentTarget)) });
      notify('Order placed');
      navigate('/placed');
    } catch (error) {
      notify(error.message);
    } finally {
      setBusy(false);
    }
  }
  return <section className="panel"><h1>Checkout</h1><p>Cash on delivery</p><form onSubmit={submit}><label>Shipping address<input name="shippingAddress" required minLength={10} maxLength={300} autoComplete="street-address" /></label><button disabled={busy}>Place order</button></form></section>;
}

export function Orders({ notify }) {
  const [orders, setOrders] = useState([]);
  useEffect(() => { api('/orders/get').then(setOrders).catch((error) => notify(error.message)); }, [notify]);
  return <><h1>My orders</h1>{orders.length === 0 && <p>No orders yet</p>}{orders.map((order) => <article className="cart-row" key={order.id}><div><h2>Order #{order.id}</h2><p>{order.products.map((item) => `${item.title} (${item.size}) × ${item.quantity}`).join(', ')}</p><p>{order.shippingAddress}</p><strong>Total: {order.totalPrice} ₽</strong></div></article>)}</>;
}

export default function App() {
  const [name, setName] = useState(localStorage.getItem('userName') ?? '');
  const [message, notify] = useState('');
  const navigate = useNavigate();
  async function logout() {
    try {
      await api('/users/logout', { method: 'POST' });
      localStorage.removeItem('token');
      localStorage.removeItem('userName');
      setName('');
      notify('You have signed out');
      navigate('/login');
    } catch (error) {
      notify(error.message);
    }
  }
  return <><header><Link className="brand" to="/">clothify<span> / everyday wear</span></Link><nav aria-label="Main navigation"><Link to="/">Catalog</Link><Link to="/cart">Cart</Link>{name ? <><Link to="/placed">My orders</Link><span>{name}</span><button onClick={logout}>Sign out</button></> : <><Link to="/login">Sign in</Link><Link to="/signup">Sign up</Link></>}</nav></header>
    <main>{message && <div className="notice" role="alert">{message}</div>}<Routes>
      <Route path="/" element={<Products notify={notify} />} />
      <Route path="/signup" element={<Auth key="signup" register onLogin={setName} notify={notify} />} />
      <Route path="/login" element={<Auth key="login" onLogin={setName} notify={notify} />} />
      <Route element={<ProtectedRoute />} >
        <Route path="/cart" element={<Cart notify={notify} />} />
        <Route path="/checkout" element={<Checkout notify={notify} />} />
        <Route path="/placed" element={<Orders notify={notify} />} />
      </Route>
      <Route path="*" element={<h1>Page not found</h1>} />
    </Routes></main><footer>Clothify · Demo store · Cash on delivery</footer></>;
}
