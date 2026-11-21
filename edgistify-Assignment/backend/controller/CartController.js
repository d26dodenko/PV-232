const CartModel = require("../models/CartModel");
const { toId } = require("../models/helpers");

// get a cart
const getCart = (req, res) => {
  try {
    const cartItems = CartModel.findByUserId(req.userId);
    res.json(cartItems);
  } catch (error) {
    res.status(500).json({ message: "Error", error });
  }
};

// add a cart
const addCart = (req, res) => {
  try {
    const { images, img1, title, price, quantity, size, productId } = req.body;

    if (!toId(productId) || !title || price === undefined || !size) {
      return res
        .status(400)
        .json({ message: "productId, title, price and size are required" });
    }

    const cartItem = CartModel.create({
      userId: req.userId,
      productId,
      images,
      img1,
      title,
      price,
      quantity,
      size,
    });

    res.status(201).json({ message: "Added to cart Sucsessfully", cartItem });
  } catch (error) {
    res.status(500).json({ message: "Error", error });
  }
};

// update a cart
const updateCart = (req, res) => {
  try {
    const quantity = Number(req.body.quantity);

    if (!Number.isInteger(quantity) || quantity < 1) {
      return res
        .status(400)
        .json({ message: "quantity must be a positive integer" });
    }

    const cartItem = CartModel.updateQuantity(req.params.id, quantity);

    if (!cartItem) {
      return res.status(404).json({ message: "Cart is not found" });
    }

    res.json({ message: "Cart updated sucessfully", cartItem });
  } catch (error) {
    res.status(500).json({ message: "Error ", error });
  }
};

// delete a cart
const removeCart = (req, res) => {
  try {
    const removed = CartModel.remove(req.params.id);

    if (!removed) {
      return res.status(404).json({ message: "Cart is not found" });
    }

    res.json({ message: "Product removed from cart" });
  } catch (error) {
    res.status(500).json({ message: "Error ", error });
  }
};

module.exports = { getCart, addCart, updateCart, removeCart };
