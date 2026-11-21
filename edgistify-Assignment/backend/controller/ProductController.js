const ProductModel = require("../models/ProductModel");

const getProducts = (req, res) => {
  try {
    const products = ProductModel.findAll();
    res.json(products);
  } catch (error) {
    res.status(500).json({ message: "Error" });
  }
};

const getSingleProducts = (req, res) => {
  try {
    const product = ProductModel.findById(req.params.id);
    if (!product) {
      return res.status(404).json({ message: "Product not found" });
    }
    res.json(product);
  } catch (error) {
    res.status(500).json({ message: "Error" });
  }
};

module.exports = { getProducts, getSingleProducts };
