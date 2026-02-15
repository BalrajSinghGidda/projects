const db = require("../config/db");

const Absence = {
  create: (userId, reason, date, callback) => {
    const sql = `
      INSERT INTO absence_requests (user_id, reason, date)
      VALUES (?, ?, ?)
    `;
    db.query(sql, [userId, reason, date], callback);
  },

  getAll: (callback) => {
    const sql = `
      SELECT a.id, u.name, a.reason, a.date, a.status
      FROM absence_requests a
      JOIN users u ON a.user_id = u.id
      ORDER BY a.created_at DESC
    `;
    db.query(sql, callback);
  }
};

module.exports = Absence;

