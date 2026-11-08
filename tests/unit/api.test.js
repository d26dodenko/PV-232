import { afterEach, expect, it, vi } from 'vitest';
import { api } from '../../front/src/api.js';

afterEach(() => vi.unstubAllGlobals());
it('sends GET without a body or token', async () => {
  const fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => [] });
  vi.stubGlobal('fetch', fetch);
  expect(await api('/products')).toEqual([]);
  expect(fetch).toHaveBeenCalledWith('/api/products', { headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' }, body: undefined });
});
it('sends the token and JSON body', async () => {
  localStorage.setItem('token', 'session');
  const fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ id: 1 }) });
  vi.stubGlobal('fetch', fetch);
  expect(await api('/cart/add', { method: 'POST', body: { quantity: 1 } })).toEqual({ id: 1 });
  expect(fetch.mock.calls[0][1]).toMatchObject({ method: 'POST', headers: { Authorization: 'Bearer session' }, body: '{"quantity":1}' });
});
it('propagates the API error message', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, json: async () => ({ message: 'Please sign in' }) }));
  await expect(api('/cart')).rejects.toThrow('Please sign in');
});
it('propagates network errors to the caller', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
  await expect(api('/products')).rejects.toThrow('offline');
});
