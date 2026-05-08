const User = require("../models/userModel");
const bcrypt = require("bcrypt");

exports.listUsers = (req, res) => {
  const requester = req.session.user;
  if (!requester || (requester.role !== "teacher" && requester.role !== "admin")) {
    return res.status(403).json({ message: "Access denied" });
  }

  const role = req.query.role || null;

  User.list(role, (err, results) => {
    if (err) {
      return res.status(500).json({ error: err });
    }
    res.json(results);
  });
};

exports.createUser = async (req, res) => {
  const requester = req.session.user;
  const { name, email, password, role } = req.body;

  if (!name || !email || !password) {
    return res.status(400).json({ message: "Missing fields" });
  }

  const isAdmin = requester.role === "admin";
  const allowedRoles = isAdmin ? ["student", "teacher"] : ["student"];
  const finalRole = role || "student";

  if (!allowedRoles.includes(finalRole)) {
    const message = isAdmin
      ? "Admin can only create student or teacher users"
      : "Teacher can only create student users";
    return res.status(403).json({ message });
  }

  try {
    const hashedPassword = await bcrypt.hash(password, 10);

    User.create(name, email, hashedPassword, finalRole, (err, result) => {
      if (err) {
        if (err.code === "ER_DUP_ENTRY") {
          return res.status(400).json({ message: "Email already exists" });
        }
        return res.status(500).json({ error: err });
      }

      res.status(201).json({
        message: "User created successfully",
        user: {
          id: result.insertId,
          name,
          email,
          role: finalRole
        }
      });
    });
  } catch (err) {
    res.status(500).json({ error: err });
  }
};

exports.deleteUser = (req, res) => {
  const requester = req.session.user;
  if (!requester || requester.role !== "admin") {
    return res.status(403).json({ message: "Access denied" });
  }

  const userId = Number(req.params.id);
  if (!Number.isInteger(userId) || userId <= 0) {
    return res.status(400).json({ message: "Invalid user id" });
  }

  if (requester.id === userId) {
    return res.status(400).json({ message: "You cannot delete your own account" });
  }

  User.findById(userId, (findErr, users) => {
    if (findErr) {
      return res.status(500).json({ error: findErr });
    }

    if (!users.length) {
      return res.status(404).json({ message: "User not found" });
    }

    const targetUser = users[0];
    if (targetUser.role !== "student" && targetUser.role !== "teacher") {
      return res.status(403).json({ message: "Only teacher and student users can be deleted" });
    }

    User.deleteById(userId, (deleteErr, result) => {
      if (deleteErr) {
        if (deleteErr.code === "ER_ROW_IS_REFERENCED_2") {
          return res.status(400).json({ message: "User cannot be deleted due to existing references" });
        }
        return res.status(500).json({ error: deleteErr });
      }

      if (!result.affectedRows) {
        return res.status(404).json({ message: "User not found" });
      }

      res.json({ message: "User deleted successfully" });
    });
  });
};
