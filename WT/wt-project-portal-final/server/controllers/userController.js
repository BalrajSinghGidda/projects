const User = require("../models/userModel");
const bcrypt = require("bcrypt");

exports.listUsers = (req, res) => {
  const requester = req.session.user;
  if (!requester || (requester.role !== "teacher" && requester.role !== "admin")) {
    return res.status(403).json({ message: "Access denied" });
  }

  const role = requester.role === "teacher" ? "student" : (req.query.role || null);

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

exports.deleteUserByAdmin = (req, res) => {
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
      return res.status(403).json({ message: "Only teacher and student users can be removed" });
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

exports.requestUserRemoval = (req, res) => {
  const requester = req.session.user;
  if (!requester || (requester.role !== "teacher" && requester.role !== "admin")) {
    return res.status(403).json({ message: "Access denied" });
  }

  const userId = Number(req.params.id);
  if (!Number.isInteger(userId) || userId <= 0) {
    return res.status(400).json({ message: "Invalid user id" });
  }

  if (requester.id === userId) {
    return res.status(400).json({ message: "You cannot request removal of your own account" });
  }

  const reason = req.body && typeof req.body.reason === "string" ? req.body.reason.trim() : null;

  User.findById(userId, (findErr, users) => {
    if (findErr) {
      return res.status(500).json({ error: findErr });
    }

    if (!users.length) {
      return res.status(404).json({ message: "User not found" });
    }

    const targetUser = users[0];
    if (requester.role === "teacher" && targetUser.role !== "student") {
      return res.status(403).json({ message: "Teacher can only request student removal" });
    }
    if (targetUser.role !== "student" && targetUser.role !== "teacher") {
      return res.status(403).json({ message: "Only teacher and student users can be removed" });
    }

    User.hasPendingRemovalRequest(userId, (pendingErr, pending) => {
      if (pendingErr) {
        return res.status(500).json({ error: pendingErr });
      }

      if (pending.length) {
        return res.status(400).json({ message: "A pending removal request already exists for this user" });
      }

      User.createRemovalRequest(userId, requester.id, reason, (createErr) => {
        if (createErr) {
          return res.status(500).json({ error: createErr });
        }

        res.status(201).json({ message: "Removal request submitted for admin approval" });
      });
    });
  });
};

exports.listRemovalRequests = (req, res) => {
  const requester = req.session.user;
  if (!requester || (requester.role !== "teacher" && requester.role !== "admin")) {
    return res.status(403).json({ message: "Access denied" });
  }

  const handler = requester.role === "admin"
    ? User.listRemovalRequestsForAdmin
    : (callback) => User.listRemovalRequestsForTeacher(requester.id, callback);

  handler((err, results) => {
    if (err) {
      return res.status(500).json({ error: err });
    }
    res.json(results);
  });
};

exports.reviewRemovalRequest = (req, res) => {
  const requester = req.session.user;
  if (!requester || requester.role !== "admin") {
    return res.status(403).json({ message: "Access denied" });
  }

  const requestId = Number(req.params.id);
  const status = req.body && req.body.status;
  if (!Number.isInteger(requestId) || requestId <= 0) {
    return res.status(400).json({ message: "Invalid request id" });
  }
  if (status !== "approved" && status !== "rejected") {
    return res.status(400).json({ message: "Invalid status" });
  }

  User.resolveRemovalRequest(requestId, requester.id, status, (err, result) => {
    if (err) {
      if (err.code === "NOT_FOUND") {
        return res.status(404).json({ message: "Removal request not found" });
      }
      if (err.code === "ALREADY_RESOLVED") {
        return res.status(400).json({ message: "Removal request already resolved" });
      }
      if (err.code === "INVALID_TARGET_ROLE") {
        return res.status(403).json({ message: "Only teacher and student users can be removed" });
      }
      if (err.code === "TARGET_NOT_FOUND") {
        return res.status(404).json({ message: "Target user not found" });
      }
      if (err.code === "ER_ROW_IS_REFERENCED_2") {
        return res.status(400).json({ message: "User cannot be deleted due to existing references" });
      }
      return res.status(500).json({ error: err });
    }

    if (result.action === "approved") {
      return res.json({ message: "Removal approved and user deleted" });
    }
    res.json({ message: "Removal request rejected" });
  });
};
