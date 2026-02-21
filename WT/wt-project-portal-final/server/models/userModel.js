const db = require("../config/db");

const User = {
  create: (name, email, hashedPassword, role, callback) => {
    const sql = "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)";
    db.query(sql, [name, email, hashedPassword, role], callback);
  },

  findByEmail: (email, callback) => {
    const sql = "SELECT * FROM users WHERE email = ?";
    db.query(sql, [email], callback);
  },

  findById: (id, callback) => {
    const sql = "SELECT id, name, email, role FROM users WHERE id = ?";
    db.query(sql, [id], callback);
  }
};

module.exports = User;

