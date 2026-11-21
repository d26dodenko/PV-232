const { db } = require("../config/db");
const { toId, normalizeImages, parseJsonArray } = require("./helpers");

const mapRow = (row) => {
  if (!row) {
    return undefined;
  }

  const images = parseJsonArray(row.images);

  return {
    ...row,
    _id: String(row.id),
    images,
    img1: images[0],
  };
};

const findByUserId = (userId) => {
  const id = toId(userId);
  if (!id) {
    return [];
  }

  return db
    .prepare("SELECT * FROM carts WHERE userId = ? ORDER BY id")
    .all(id)
    .map(mapRow);
};

const findById = (id) => {
  const cartId = toId(id);
  if (!cartId) {
    return undefined;
  }

  return mapRow(db.prepare("SELECT * FROM carts WHERE id = ?").get(cartId));
};

const create = ({
  userId,
  productId,
  images,
  img1,
  title,
  price,
  quantity = 1,
  size,
}) => {
  const result = db
    .prepare(
      `INSERT INTO carts
        (userId, productId, images, title, price, quantity, size)
       VALUES (?, ?, ?, ?, ?, ?, ?)`
    )
    .run(
      toId(userId),
      toId(productId),
      JSON.stringify(normalizeImages(images, img1)),
      title,
      price,
      quantity ?? 1,
      size
    );

  return findById(result.lastInsertRowid);
};

const updateQuantity = (id, quantity) => {
  const cartId = toId(id);
  if (!cartId) {
    return undefined;
  }

  db.prepare(
    "UPDATE carts SET quantity = ?, updatedAt = datetime('now') WHERE id = ?"
  ).run(quantity, cartId);

  return findById(cartId);
};

const remove = (id) => {
  const cartId = toId(id);
  if (!cartId) {
    return false;
  }

  return db.prepare("DELETE FROM carts WHERE id = ?").run(cartId).changes > 0;
};

module.exports = { findByUserId, findById, create, updateQuantity, remove };
