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

// teacher views
exports.getAllAbsences = (req, res) => {
  Absence.getAll((err, results) => {
    if (err) return res.status(500).json({ error: err });
    res.json(results);
  });
};

