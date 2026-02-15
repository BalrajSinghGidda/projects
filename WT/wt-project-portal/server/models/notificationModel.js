const db = require("../config/db");

const Notification = {
  create: (title, message, sentBy, callback) => {
    const sql = `
      INSERT INTO notifications (title, message, sent_by)
      VALUES (?, ?, ?)
    `;
    db.query(sql, [title, message, sentBy], callback);
  },

  getAll: (callback) => {
    const sql = `
      SELECT n.id, n.title, n.message, n.created_at,
             u.name AS sender
      FROM notifications n
      LEFT JOIN users u ON n.sent_by = u.id
      ORDER BY n.created_at DESC
    `;
    db.query(sql, callback);
  }
};

module.exports = Notification;

