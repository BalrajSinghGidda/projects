const db = require("../config/db");

const Deadline = {
  create: (title, type, dueDate, description, createdBy, callback) => {
    const sql = `
      INSERT INTO submission_deadlines (title, type, due_date, description, created_by, status)
      VALUES (?, ?, ?, ?, ?, 'open')
    `;
    db.query(sql, [title, type, dueDate, description || null, createdBy], callback);
  },

  findById: (id, callback) => {
    const sql = "SELECT * FROM submission_deadlines WHERE id = ?";
    db.query(sql, [id], callback);
  },

  list: (scope, callback) => {
    let sql = `
      SELECT d.id, d.title, d.type, d.due_date, d.description, d.status, d.created_at,
             u.name AS created_by_name
      FROM submission_deadlines d
      LEFT JOIN users u ON u.id = d.created_by
    `;
    const params = [];

    if (scope !== "all") {
      sql += " WHERE d.status = 'open' AND d.due_date >= CURDATE()";
    }

    sql += " ORDER BY d.due_date ASC";
    db.query(sql, params, callback);
  }
};

module.exports = Deadline;
