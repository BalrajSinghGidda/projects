const Absence = require("../models/absenceModel");

// student submits
exports.submitAbsence = (req, res) => {
  const { reason, date } = req.body;
  const userId = req.session.user.id;

  if (!reason || !date) {
    return res.status(400).json({ message: "Missing fields" });
  }

  Absence.create(userId, reason, date, (err, result) => {
    if (err) return res.status(500).json({ error: err });

    res.json({ message: "Absence submitted 🚫" });
  });
};

// teacher views (all), student views (own)
exports.getAllAbsences = (req, res) => {
  const user = req.session.user;
  
  if (user.role === 'teacher' || user.role === 'admin') {
    Absence.getAll((err, results) => {
      if (err) return res.status(500).json({ error: err });
      res.json(results);
    });
  } else {
    Absence.getByUser(user.id, (err, results) => {
      if (err) return res.status(500).json({ error: err });
      res.json(results);
    });
  }
};

exports.updateAbsenceStatus = (req, res) => {
  const actor = req.session.user;
  if (!actor || (actor.role !== "teacher" && actor.role !== "admin")) {
    return res.status(403).json({ message: "Access denied" });
  }

  const absenceId = req.params.id;
  const { status } = req.body;
  const allowed = ["approved", "rejected"];
  if (!allowed.includes(status)) {
    return res.status(400).json({ message: "status must be approved or rejected" });
  }

  Absence.updateStatus(absenceId, status, actor.id, (err, result) => {
    if (err) return res.status(500).json({ error: err });
    if (!result.affectedRows) return res.status(404).json({ message: "Absence request not found" });

    res.json({ message: `Absence request ${status}` });
  });
};
