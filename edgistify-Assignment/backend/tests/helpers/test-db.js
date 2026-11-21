require("./test-env");

const { db } = require("../../config/db");
const ProductModel = require("../../models/ProductModel");

const PRODUCTS = [
  {
    title: "Classic Cotton T-Shirt",
    category: "T-Shirts",
    description: "A comfortable cotton t-shirt",
    brand: "Urban Basics",
    price: 25,
    rating: 4.5,
    images: ["https://example.com/tshirt.png"],
    quantity: 40,
    size: "M",
  },
  {
    title: "Slim Fit Denim Jacket",
    category: "Jackets",
    description: "A stylish denim jacket",
    brand: "North Street",
    price: 79,
    rating: 4.7,
    images: ["https://example.com/jacket.png"],
    quantity: 18,
    size: "L",
  },
];

function seedProducts() {
  if (ProductModel.findAll().length === 0) {
    PRODUCTS.forEach((product) => ProductModel.create(product));
  }
}

function resetUsers() {
  db.exec("DELETE FROM carts; DELETE FROM orders; DELETE FROM users;");
}

module.exports = { db, seedProducts, resetUsers, PRODUCTS };
