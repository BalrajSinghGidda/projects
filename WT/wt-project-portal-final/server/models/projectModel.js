const db = require("../config/db");

const Project = {

  create: (title, description, type, createdBy, callback) => {
    const sql = `
      INSERT INTO projects (title, description, type, created_by)
      VALUES (?, ?, ?, ?)
    `;
    db.query(sql, [title, description, type, createdBy], callback);
  },

  addMember: (projectId, userId, callback) => {
    const sql = `
      INSERT INTO project_members (project_id, user_id)
      VALUES (?, ?)
    `;
    db.query(sql, [projectId, userId], callback);
  },

  getAll: (callback) => {
    const sql = `
      SELECT p.id, p.title, p.type, p.created_at,
             u.name AS creator
      FROM projects p
      LEFT JOIN users u ON p.created_by = u.id
      ORDER BY p.created_at DESC
    `;
    db.query(sql, callback);
  },

  getByUser: (userId, callback) => {
    const sql = `
      SELECT p.id, p.title, p.type, p.created_at
      FROM projects p
      JOIN project_members pm ON pm.project_id = p.id
      WHERE pm.user_id = ?
      ORDER BY p.created_at DESC
    `;
    db.query(sql, [userId], callback);
  },

  getMembers: (projectId, callback) => {
    const sql = `
      SELECT u.id, u.name, u.email
      FROM project_members pm
      JOIN users u ON pm.user_id = u.id
      WHERE pm.project_id = ?
    `;
    db.query(sql, [projectId], callback);
  },

  getById: (id, callback) => {
    const sql = `
      SELECT p.*, u.name AS creator
      FROM projects p
      LEFT JOIN users u ON p.created_by = u.id
      WHERE p.id = ?
    `;
    db.query(sql, [id], callback);
  },

  search: (query, type, callback) => {
    let sql = "SELECT * FROM projects WHERE 1=1";
    let params = [];

    if (query) {
      sql += " AND title LIKE ?";
      params.push("%" + query + "%");
    }

    if (type) {
      sql += " AND type = ?";
      params.push(type);
    }

    db.query(sql, params, callback);
  }

};

module.exports = Project;

