import axios from "axios";

type ApiPayload = Record<string, unknown>;

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:3000/api",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export const signup = async (userData: ApiPayload) => {
    return await api.post("/users/register", userData);
  };

export const login = async (credentials: ApiPayload) => {
  return await api.post("/users/login", credentials);
};

export const getProducts = async () => {
  return await api.get("/products");
};


export const getProductById = async (id: string | number) => {
  return await api.get(`/products/${id}`);
};

export const addToCart = async (cartItems: ApiPayload) => {
  return await api.post("/cart/add", cartItems);
};

export const getCartItems = async () => {
  return await api.get("/cart");
};

export const deleteCartItem = async (itemId: string | number) => {
  return await api.delete(`/cart/remove/${itemId}`);
};



export const createOrder = async (orderData: ApiPayload) => {
  return await api.post("/orders/create", orderData);
};

export const getOrder = async () => {
  return await api.get("/orders/get");
};


export default api;