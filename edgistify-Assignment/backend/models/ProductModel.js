const { db } = require("../config/db");
const { toId, normalizeImages, parseJsonArray } = require("./helpers");

const mapRow = (row) => {
  if (!row) {
    return undefined;
  }

  return {
    ...row,
    _id: String(row.id),
    images: parseJsonArray(row.images),
    sizes: [row.size],
  };
};

const findAll = () =>
  db.prepare("SELECT * FROM products ORDER BY id").all().map(mapRow);

const findById = (id) => {
  const productId = toId(id);
  if (!productId) {
    return undefined;
  }

  return mapRow(
    db.prepare("SELECT * FROM products WHERE id = ?").get(productId)
  );
};

const create = ({
  title,
  category,
  description,
  brand,
  price,
  rating = 0,
  images,
  img1,
  quantity,
  size,
  sizes,
}) => {
  const storedSize = size || (Array.isArray(sizes) ? sizes[0] : sizes) || "M";
  const result = db
    .prepare(
      `INSERT INTO products
        (title, category, description, brand, price, rating, images, quantity, size)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
    )
    .run(
      title,
      category,
      description,
      brand,
      price,
      rating,
      JSON.stringify(normalizeImages(images, img1)),
      quantity,
      storedSize
    );

  return findById(result.lastInsertRowid);
};

module.exports = { findAll, findById, create };
