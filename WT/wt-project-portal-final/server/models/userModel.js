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
  },

  findWithPasswordById: (id, callback) => {
    const sql = "SELECT id, name, email, password, role FROM users WHERE id = ?";
    db.query(sql, [id], callback);
  },

  list: (role, callback) => {
    let sql = "SELECT id, name, email, role FROM users";
    const params = [];

    if (role) {
      sql += " WHERE role = ?";
      params.push(role);
    }

    sql += " ORDER BY name ASC";
    db.query(sql, params, callback);
  },

  deleteById: (id, callback) => {
    const sql = "DELETE FROM users WHERE id = ?";
    db.query(sql, [id], callback);
  },

  updateNameById: (id, name, callback) => {
    const sql = "UPDATE users SET name = ? WHERE id = ?";
    db.query(sql, [name, id], callback);
  },

  updatePasswordById: (id, hashedPassword, callback) => {
    const sql = "UPDATE users SET password = ? WHERE id = ?";
    db.query(sql, [hashedPassword, id], callback);
  },

  hasPendingRemovalRequest: (targetUserId, callback) => {
    const sql = `
      SELECT id
      FROM user_removal_requests
      WHERE target_user_id = ? AND status = 'pending'
      LIMIT 1
    `;
    db.query(sql, [targetUserId], callback);
  },

  createRemovalRequest: (targetUserId, requestedBy, reason, callback) => {
    const sql = `
      INSERT INTO user_removal_requests (target_user_id, requested_by, reason)
      VALUES (?, ?, ?)
    `;
    db.query(sql, [targetUserId, requestedBy, reason || null], callback);
  },

  hasPendingPasswordChangeRequest: (targetUserId, callback) => {
    const sql = `
      SELECT id
      FROM user_password_change_requests
      WHERE target_user_id = ? AND status = 'pending'
      LIMIT 1
    `;
    db.query(sql, [targetUserId], callback);
  },

  createPasswordChangeRequest: (targetUserId, requestedBy, newPasswordHash, callback) => {
    const sql = `
      INSERT INTO user_password_change_requests (target_user_id, requested_by, new_password_hash)
      VALUES (?, ?, ?)
    `;
    db.query(sql, [targetUserId, requestedBy, newPasswordHash], callback);
  },

  listPasswordChangeRequestsForAdmin: (callback) => {
    const sql = `
      SELECT
        upcr.id,
        upcr.target_user_id,
        upcr.requested_by,
        upcr.status,
        upcr.created_at,
        upcr.reviewed_at,
        target.name AS target_name,
        target.email AS target_email,
        target.role AS target_role,
        requester.name AS requester_name,
        reviewer.name AS reviewer_name
      FROM user_password_change_requests upcr
      JOIN users requester ON requester.id = upcr.requested_by
      LEFT JOIN users target ON target.id = upcr.target_user_id
      LEFT JOIN users reviewer ON reviewer.id = upcr.reviewed_by
      ORDER BY
        CASE upcr.status WHEN 'pending' THEN 0 ELSE 1 END,
        upcr.created_at DESC
    `;
    db.query(sql, callback);
  },

  listPasswordChangeRequestsForTeacher: (teacherId, callback) => {
    const sql = `
      SELECT
        upcr.id,
        upcr.target_user_id,
        upcr.status,
        upcr.created_at,
        upcr.reviewed_at,
        target.name AS target_name,
        target.email AS target_email,
        reviewer.name AS reviewer_name
      FROM user_password_change_requests upcr
      LEFT JOIN users target ON target.id = upcr.target_user_id
      LEFT JOIN users reviewer ON reviewer.id = upcr.reviewed_by
      WHERE upcr.requested_by = ?
      ORDER BY upcr.created_at DESC
    `;
    db.query(sql, [teacherId], callback);
  },

  listRemovalRequestsForAdmin: (callback) => {
    const sql = `
      SELECT
        urr.id,
        urr.target_user_id,
        urr.requested_by,
        urr.reason,
        urr.status,
        urr.created_at,
        urr.reviewed_at,
        target.name AS target_name,
        target.email AS target_email,
        target.role AS target_role,
        requester.name AS requester_name,
        reviewer.name AS reviewer_name
      FROM user_removal_requests urr
      JOIN users requester ON requester.id = urr.requested_by
      LEFT JOIN users target ON target.id = urr.target_user_id
      LEFT JOIN users reviewer ON reviewer.id = urr.reviewed_by
      ORDER BY
        CASE urr.status WHEN 'pending' THEN 0 ELSE 1 END,
        urr.created_at DESC
    `;
    db.query(sql, callback);
  },

  listRemovalRequestsForTeacher: (teacherId, callback) => {
    const sql = `
      SELECT
        urr.id,
        urr.target_user_id,
        urr.reason,
        urr.status,
        urr.created_at,
        urr.reviewed_at,
        target.name AS target_name,
        target.email AS target_email,
        reviewer.name AS reviewer_name
      FROM user_removal_requests urr
      LEFT JOIN users target ON target.id = urr.target_user_id
      LEFT JOIN users reviewer ON reviewer.id = urr.reviewed_by
      WHERE urr.requested_by = ?
      ORDER BY urr.created_at DESC
    `;
    db.query(sql, [teacherId], callback);
  },

  resolveRemovalRequest: (requestId, reviewerId, action, callback) => {
    db.beginTransaction((beginErr) => {
      if (beginErr) return callback(beginErr);

      const selectSql = `
        SELECT urr.id, urr.target_user_id, urr.status, u.role AS target_role
        FROM user_removal_requests urr
        JOIN users u ON u.id = urr.target_user_id
        WHERE urr.id = ? FOR UPDATE
      `;

      db.query(selectSql, [requestId], (selectErr, rows) => {
        if (selectErr) {
          return db.rollback(() => callback(selectErr));
        }

        if (!rows.length) {
          return db.rollback(() => callback({ code: "NOT_FOUND" }));
        }

        const request = rows[0];
        if (request.status !== "pending") {
          return db.rollback(() => callback({ code: "ALREADY_RESOLVED" }));
        }

        const updateSql = `
          UPDATE user_removal_requests
          SET status = ?, reviewed_by = ?, reviewed_at = NOW()
          WHERE id = ?
        `;

        db.query(updateSql, [action, reviewerId, requestId], (updateErr) => {
          if (updateErr) {
            return db.rollback(() => callback(updateErr));
          }

          if (action === "rejected") {
            return db.commit((commitErr) => {
              if (commitErr) {
                return db.rollback(() => callback(commitErr));
              }
              callback(null, { action: "rejected" });
            });
          }

          if (request.target_role !== "student" && request.target_role !== "teacher") {
            return db.rollback(() => callback({ code: "INVALID_TARGET_ROLE" }));
          }

          db.query("DELETE FROM users WHERE id = ?", [request.target_user_id], (deleteErr, deleteResult) => {
            if (deleteErr) {
              return db.rollback(() => callback(deleteErr));
            }

            if (!deleteResult.affectedRows) {
              return db.rollback(() => callback({ code: "TARGET_NOT_FOUND" }));
            }

            db.commit((commitErr) => {
              if (commitErr) {
                return db.rollback(() => callback(commitErr));
              }
              callback(null, { action: "approved", deletedUserId: request.target_user_id });
            });
          });
        });
      });
    });
  },

  resolvePasswordChangeRequest: (requestId, reviewerId, action, callback) => {
    db.beginTransaction((beginErr) => {
      if (beginErr) return callback(beginErr);

      const selectSql = `
        SELECT upcr.id, upcr.target_user_id, upcr.new_password_hash, upcr.status, u.role AS target_role
        FROM user_password_change_requests upcr
        JOIN users u ON u.id = upcr.target_user_id
        WHERE upcr.id = ? FOR UPDATE
      `;

      db.query(selectSql, [requestId], (selectErr, rows) => {
        if (selectErr) {
          return db.rollback(() => callback(selectErr));
        }

        if (!rows.length) {
          return db.rollback(() => callback({ code: "NOT_FOUND" }));
        }

        const request = rows[0];
        if (request.status !== "pending") {
          return db.rollback(() => callback({ code: "ALREADY_RESOLVED" }));
        }

        const updateRequestSql = `
          UPDATE user_password_change_requests
          SET status = ?, reviewed_by = ?, reviewed_at = NOW()
          WHERE id = ?
        `;

        db.query(updateRequestSql, [action, reviewerId, requestId], (updateErr) => {
          if (updateErr) {
            return db.rollback(() => callback(updateErr));
          }

          if (action === "rejected") {
            return db.commit((commitErr) => {
              if (commitErr) {
                return db.rollback(() => callback(commitErr));
              }
              callback(null, { action: "rejected" });
            });
          }

          if (request.target_role !== "student") {
            return db.rollback(() => callback({ code: "INVALID_TARGET_ROLE" }));
          }

          const updateUserSql = "UPDATE users SET password = ? WHERE id = ?";
          db.query(updateUserSql, [request.new_password_hash, request.target_user_id], (userUpdateErr, userResult) => {
            if (userUpdateErr) {
              return db.rollback(() => callback(userUpdateErr));
            }

            if (!userResult.affectedRows) {
              return db.rollback(() => callback({ code: "TARGET_NOT_FOUND" }));
            }

            db.commit((commitErr) => {
              if (commitErr) {
                return db.rollback(() => callback(commitErr));
              }
              callback(null, { action: "approved", targetUserId: request.target_user_id });
            });
          });
        });
      });
    });
  }
};

module.exports = User;
