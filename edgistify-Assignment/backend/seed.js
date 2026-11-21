const { db } = require("./config/db");
const ProductModel = require("./models/ProductModel");

const products = [
  {
    title: "Classic Cotton T-Shirt",
    category: "T-Shirts",
    description: "Soft everyday cotton t-shirt with a relaxed fit.",
    brand: "Urban Basics",
    price: 25,
    rating: 4.5,
    images: ["https://placehold.co/600x600?text=Cotton+T-Shirt"],
    quantity: 40,
    size: "M",
  },
  {
    title: "Slim Fit Denim Jacket",
    category: "Jackets",
    description: "Durable denim jacket with a modern slim fit.",
    brand: "North Street",
    price: 79,
    rating: 4.7,
    images: ["https://placehold.co/600x600?text=Denim+Jacket"],
    quantity: 18,
    size: "L",
  },
  {
    title: "Everyday Running Shoes",
    category: "Shoes",
    description: "Lightweight running shoes for daily training.",
    brand: "Stride",
    price: 95,
    rating: 4.4,
    images: ["https://placehold.co/600x600?text=Running+Shoes"],
    quantity: 25,
    size: "42",
  },
  {
    title: "Canvas Tote Bag",
    category: "Accessories",
    description: "Reusable canvas tote with a spacious main compartment.",
    brand: "Carry Co",
    price: 19,
    rating: 4.2,
    images: ["https://placehold.co/600x600?text=Canvas+Tote"],
    quantity: 60,
    size: "One Size",
  },
  {
    title: "Wool Blend Beanie",
    category: "Accessories",
    description: "Warm wool blend beanie for cold weather.",
    brand: "North Street",
    price: 22,
    rating: 4.6,
    images: ["https://placehold.co/600x600?text=Wool+Beanie"],
    quantity: 35,
    size: "One Size",
  },
  {
    title: "Relaxed Fit Hoodie",
    category: "Hoodies",
    description: "Cotton hoodie with a brushed inner lining.",
    brand: "Urban Basics",
    price: 55,
    rating: 4.8,
    images: ["https://placehold.co/600x600?text=Relaxed+Hoodie"],
    quantity: 30,
    size: "XL",
  },
];

if (ProductModel.findAll().length > 0) {
  console.log("Products already exist. Delete data/shop.db to reseed.");
} else {
  products.forEach((product) => ProductModel.create(product));
  console.log(`Seeded ${products.length} products.`);
}

db.close();