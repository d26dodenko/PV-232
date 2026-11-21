const { db } = require("../config/db");

const findByEmail = (email) =>
  db.prepare("SELECT * FROM users WHERE email = ?").get(email);

const findById = (id) =>
  db
    .prepare(
      "SELECT id, fullName, email, createdAt, updatedAt FROM users WHERE id = ?"
    )
    .get(id);

const create = ({ fullName, email, password }) => {
  const result = db
    .prepare("INSERT INTO users (fullName, email, password) VALUES (?, ?, ?)")
    .run(fullName, email, password);

  return findById(result.lastInsertRowid);
};

module.exports = { findByEmail, findById, create };
