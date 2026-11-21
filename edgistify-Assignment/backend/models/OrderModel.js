const { db } = require("../config/db");
const { toId, parseJsonArray } = require("./helpers");

const mapRow = (row) => {
  if (!row) {
    return undefined;
  }

  return {
    ...row,
    _id: String(row.id),
    products: parseJsonArray(row.products),
  };
};

const findById = (id) => {
  const orderId = toId(id);
  if (!orderId) {
    return undefined;
  }

  return mapRow(
    db.prepare("SELECT * FROM orders WHERE id = ?").get(orderId)
  );
};

const create = ({
  userId,
  products,
  totalPrice,
  shippingAddress,
  paymentStatus = "Pending",
  orderStatus = "Pending",
}) => {
  const result = db
    .prepare(
      `INSERT INTO orders
        (userId, products, totalPrice, shippingAddress, paymentStatus, orderStatus)
       VALUES (?, ?, ?, ?, ?, ?)`
    )
    .run(
      toId(userId),
      JSON.stringify(products),
      totalPrice,
      shippingAddress,
      paymentStatus,
      orderStatus
    );

  return findById(result.lastInsertRowid);
};

const findByUserId = (userId) => {
  const id = toId(userId);
  if (!id) {
    return [];
  }

  return db
    .prepare("SELECT * FROM orders WHERE userId = ? ORDER BY id")
    .all(id)
    .map(mapRow);
};

module.exports = { findById, create, findByUserId };
