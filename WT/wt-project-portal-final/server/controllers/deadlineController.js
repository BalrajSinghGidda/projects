const Deadline = require("../models/deadlineModel");

exports.createDeadline = (req, res) => {
  const actor = req.session.user;
  if (!actor || (actor.role !== "teacher" && actor.role !== "admin")) {
    return res.status(403).json({ message: "Access denied" });
  }

  const { title, type, dueDate, description } = req.body;
  if (!title || !type || !dueDate) {
    return res.status(400).json({ message: "title, type and dueDate are required" });
  }

  Deadline.create(title, type, dueDate, description, actor.id, (err, result) => {
    if (err) return res.status(500).json({ error: err });
    res.json({ message: "Deadline created successfully", deadlineId: result.insertId });
  });
};

exports.listDeadlines = (req, res) => {
  const actor = req.session.user;
  if (!actor) {
    return res.status(401).json({ message: "Unauthorized" });
  }

  const scope = (actor.role === "teacher" || actor.role === "admin") ? "all" : "open";
  Deadline.list(scope, (err, results) => {
    if (err) return res.status(500).json({ error: err });
    res.json(results);
  });
};
