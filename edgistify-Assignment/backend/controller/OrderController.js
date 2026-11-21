const OrderModel = require("../models/OrderModel");
const { normalizeImages } = require("../models/helpers");

const createOrder = (req, res) => {
  try {
    const { products, totalPrice, shippingAddress } = req.body;

    if (!Array.isArray(products) || products.length === 0) {
      return res.status(400).json({ message: "must contain products" });
    }

    const normalizedProducts = products.map((product) => ({
      productId: product.productId ?? product._id ?? null,
      title: product.title,
      images: normalizeImages(product.images, product.img1),
      quantity: product.quantity,
      price: product.price,
    }));

    const order = OrderModel.create({
      userId: req.userId,
      products: normalizedProducts,
      totalPrice,
      shippingAddress,
    });

    res.status(201).json({ message: "Order added successfully", order });
  } catch (error) {
    res.status(500).json({ message: "Error", error });
  }
};

// Fetch all orders
const getOrders = (req, res) => {
  try {
    const orders = OrderModel.findByUserId(req.userId);
    res.json(orders);
  } catch (error) {
    res.status(500).json({ message: "Error", error });
  }
};

module.exports = { createOrder, getOrders };
