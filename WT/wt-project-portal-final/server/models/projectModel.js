const db = require("../config/db");

const Project = {

  create: (title, description, type, createdBy, deadlineId, callback) => {
    const sql = `
      INSERT INTO projects (title, description, type, created_by, deadline_id)
      VALUES (?, ?, ?, ?, ?)
    `;
    db.query(sql, [title, description, type, createdBy, deadlineId], callback);
  },

  addMember: (projectId, userId, callback) => {
    const sql = `
      INSERT INTO project_members (project_id, user_id)
      VALUES (?, ?)
    `;
    db.query(sql, [projectId, userId], callback);
  },

  removeMember: (projectId, userId, callback) => {
    const sql = `
      DELETE FROM project_members
      WHERE project_id = ? AND user_id = ?
    `;
    db.query(sql, [projectId, userId], callback);
  },

  getAll: (callback) => {
    const sql = `
      SELECT p.id, p.title, p.type, p.created_at, p.deadline_id,
             u.name AS creator, d.title AS deadline_title, d.due_date
      FROM projects p
      LEFT JOIN users u ON p.created_by = u.id
      LEFT JOIN submission_deadlines d ON d.id = p.deadline_id
      ORDER BY p.created_at DESC
    `;
    db.query(sql, callback);
  },

  getByUser: (userId, callback) => {
    const sql = `
      SELECT p.id, p.title, p.type, p.created_at, p.deadline_id, d.title AS deadline_title, d.due_date
      FROM projects p
      JOIN project_members pm ON pm.project_id = p.id
      LEFT JOIN submission_deadlines d ON d.id = p.deadline_id
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

  isMember: (projectId, userId, callback) => {
    const sql = `
      SELECT 1
      FROM project_members
      WHERE project_id = ? AND user_id = ?
      LIMIT 1
    `;
    db.query(sql, [projectId, userId], callback);
  },

  search: (query, type, callback) => {
    let sql = `
      SELECT p.*, d.title AS deadline_title, d.due_date
      FROM projects p
      LEFT JOIN submission_deadlines d ON d.id = p.deadline_id
      WHERE 1=1
    `;
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
  },

  getByDeadline: (deadlineId, callback) => {
    const sql = `
      SELECT p.id, p.title, p.type, p.created_at, p.deadline_id,
             u.name AS creator
      FROM projects p
      LEFT JOIN users u ON p.created_by = u.id
      WHERE p.deadline_id = ?
      ORDER BY p.created_at DESC
    `;
    db.query(sql, [deadlineId], callback);
  }

};

module.exports = Project;
