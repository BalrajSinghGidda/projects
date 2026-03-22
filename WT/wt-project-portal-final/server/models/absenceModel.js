const db = require("../config/db");

function withFallback(baseSql, fallbackSql, params, callback) {
  db.query(baseSql, params, (err, results) => {
    if (!err) return callback(null, results);
    if (err.code !== "ER_BAD_FIELD_ERROR") return callback(err);

    db.query(fallbackSql, params, callback);
  });
}

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
      SELECT a.id, u.name, a.reason, a.date, a.status,
             a.reviewed_at, reviewer.name AS reviewed_by_name
      FROM absence_requests a
      JOIN users u ON a.user_id = u.id
      LEFT JOIN users reviewer ON reviewer.id = a.reviewed_by
      ORDER BY a.created_at DESC
    `;
    const fallbackSql = `
      SELECT a.id, u.name, a.reason, a.date, a.status,
             NULL AS reviewed_at, NULL AS reviewed_by_name
      FROM absence_requests a
      JOIN users u ON a.user_id = u.id
      ORDER BY a.created_at DESC
    `;
    withFallback(sql, fallbackSql, [], callback);
  },

  getByUser: (userId, callback) => {
    const sql = `
      SELECT a.id, u.name, a.reason, a.date, a.status,
             a.reviewed_at, reviewer.name AS reviewed_by_name
      FROM absence_requests a
      JOIN users u ON a.user_id = u.id
      LEFT JOIN users reviewer ON reviewer.id = a.reviewed_by
      WHERE a.user_id = ?
      ORDER BY a.created_at DESC
    `;
    const fallbackSql = `
      SELECT a.id, u.name, a.reason, a.date, a.status,
             NULL AS reviewed_at, NULL AS reviewed_by_name
      FROM absence_requests a
      JOIN users u ON a.user_id = u.id
      WHERE a.user_id = ?
      ORDER BY a.created_at DESC
    `;
    withFallback(sql, fallbackSql, [userId], callback);
  },

  updateStatus: (id, status, reviewedBy, callback) => {
    const sql = `
      UPDATE absence_requests
      SET status = ?, reviewed_by = ?, reviewed_at = NOW()
      WHERE id = ?
    `;
    db.query(sql, [status, reviewedBy, id], (err, result) => {
      if (!err) return callback(null, result);
      if (err.code !== "ER_BAD_FIELD_ERROR") return callback(err);

      const fallbackSql = `
        UPDATE absence_requests
        SET status = ?
        WHERE id = ?
      `;
      db.query(fallbackSql, [status, id], callback);
    });
  }
};

module.exports = Absence;
