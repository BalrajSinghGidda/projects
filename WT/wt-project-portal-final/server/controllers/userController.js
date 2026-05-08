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

exports.updateOwnName = (req, res) => {
  const requester = req.session.user;
  if (!requester) {
    return res.status(401).json({ message: "Unauthorized" });
  }

  const name = req.body && typeof req.body.name === "string" ? req.body.name.trim() : "";
  if (!name) {
    return res.status(400).json({ message: "Name is required" });
  }

  User.updateNameById(requester.id, name, (err, result) => {
    if (err) {
      return res.status(500).json({ error: err });
    }
    if (!result.affectedRows) {
      return res.status(404).json({ message: "User not found" });
    }

    req.session.user.name = name;
    res.json({ message: "Display name updated", user: req.session.user });
  });
};

exports.changeOwnPassword = (req, res) => {
  const requester = req.session.user;
  if (!requester) {
    return res.status(401).json({ message: "Unauthorized" });
  }

  const currentPassword = req.body && req.body.currentPassword;
  const newPassword = req.body && req.body.newPassword;
  if (!currentPassword || !newPassword) {
    return res.status(400).json({ message: "Current and new password are required" });
  }

  User.findWithPasswordById(requester.id, async (findErr, users) => {
    if (findErr) {
      return res.status(500).json({ error: findErr });
    }
    if (!users.length) {
      return res.status(404).json({ message: "User not found" });
    }

    const user = users[0];
    const isValid = await bcrypt.compare(currentPassword, user.password);
    if (!isValid) {
      return res.status(401).json({ message: "Current password is incorrect" });
    }

    try {
      const hashedPassword = await bcrypt.hash(newPassword, 10);
      User.updatePasswordById(requester.id, hashedPassword, (updateErr, result) => {
        if (updateErr) {
          return res.status(500).json({ error: updateErr });
        }
        if (!result.affectedRows) {
          return res.status(404).json({ message: "User not found" });
        }

        res.json({ message: "Password updated successfully" });
      });
    } catch (err) {
      res.status(500).json({ error: err });
    }
  });
};

exports.updateUserByAdmin = async (req, res) => {
  const requester = req.session.user;
  if (!requester || requester.role !== "admin") {
    return res.status(403).json({ message: "Access denied" });
  }

  const userId = Number(req.params.id);
  if (!Number.isInteger(userId) || userId <= 0) {
    return res.status(400).json({ message: "Invalid user id" });
  }

  const name = req.body && typeof req.body.name === "string" ? req.body.name.trim() : "";
  const newPassword = req.body && req.body.newPassword;
  if (!name && !newPassword) {
    return res.status(400).json({ message: "Provide name and/or new password" });
  }

  User.findById(userId, async (findErr, users) => {
    if (findErr) {
      return res.status(500).json({ error: findErr });
    }
    if (!users.length) {
      return res.status(404).json({ message: "User not found" });
    }

    const targetUser = users[0];
    if (targetUser.role !== "student" && targetUser.role !== "teacher") {
      return res.status(403).json({ message: "Admin can only edit teacher or student users" });
    }

    const finish = () => {
      res.json({ message: "User updated successfully" });
    };

    const updatePassword = async () => {
      if (!newPassword) return finish();
      try {
        const hashedPassword = await bcrypt.hash(newPassword, 10);
        User.updatePasswordById(userId, hashedPassword, (passErr) => {
          if (passErr) {
            return res.status(500).json({ error: passErr });
          }
          finish();
        });
      } catch (err) {
        return res.status(500).json({ error: err });
      }
    };

    if (name) {
      User.updateNameById(userId, name, (nameErr) => {
        if (nameErr) {
          return res.status(500).json({ error: nameErr });
        }
        updatePassword();
      });
      return;
    }

    updatePassword();
  });
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

exports.requestStudentPasswordChange = async (req, res) => {
  const requester = req.session.user;
  if (!requester || requester.role !== "teacher") {
    return res.status(403).json({ message: "Access denied" });
  }

  const userId = Number(req.params.id);
  if (!Number.isInteger(userId) || userId <= 0) {
    return res.status(400).json({ message: "Invalid user id" });
  }
  const newPassword = req.body && req.body.newPassword;
  if (!newPassword) {
    return res.status(400).json({ message: "New password is required" });
  }

  User.findById(userId, async (findErr, users) => {
    if (findErr) {
      return res.status(500).json({ error: findErr });
    }
    if (!users.length) {
      return res.status(404).json({ message: "User not found" });
    }

    const targetUser = users[0];
    if (targetUser.role !== "student") {
      return res.status(403).json({ message: "Teacher can only request student password change" });
    }

    User.hasPendingPasswordChangeRequest(userId, async (pendingErr, pending) => {
      if (pendingErr) {
        return res.status(500).json({ error: pendingErr });
      }
      if (pending.length) {
        return res.status(400).json({ message: "A pending password-change request already exists for this user" });
      }

      try {
        const newPasswordHash = await bcrypt.hash(newPassword, 10);
        User.createPasswordChangeRequest(userId, requester.id, newPasswordHash, (createErr) => {
          if (createErr) {
            return res.status(500).json({ error: createErr });
          }
          res.status(201).json({ message: "Password change request submitted for admin approval" });
        });
      } catch (err) {
        res.status(500).json({ error: err });
      }
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

exports.listPasswordChangeRequests = (req, res) => {
  const requester = req.session.user;
  if (!requester || (requester.role !== "teacher" && requester.role !== "admin")) {
    return res.status(403).json({ message: "Access denied" });
  }

  const handler = requester.role === "admin"
    ? User.listPasswordChangeRequestsForAdmin
    : (callback) => User.listPasswordChangeRequestsForTeacher(requester.id, callback);

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

exports.reviewPasswordChangeRequest = (req, res) => {
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

  User.resolvePasswordChangeRequest(requestId, requester.id, status, (err, result) => {
    if (err) {
      if (err.code === "NOT_FOUND") {
        return res.status(404).json({ message: "Password change request not found" });
      }
      if (err.code === "ALREADY_RESOLVED") {
        return res.status(400).json({ message: "Password change request already resolved" });
      }
      if (err.code === "INVALID_TARGET_ROLE") {
        return res.status(403).json({ message: "Only student passwords can be changed via teacher request" });
      }
      if (err.code === "TARGET_NOT_FOUND") {
        return res.status(404).json({ message: "Target user not found" });
      }
      return res.status(500).json({ error: err });
    }

    if (result.action === "approved") {
      return res.json({ message: "Password change approved and applied" });
    }
    res.json({ message: "Password change request rejected" });
  });
};
