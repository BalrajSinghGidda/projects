const User = require("../models/userModel");

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
