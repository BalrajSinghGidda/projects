const express = require("express");
const router = express.Router();
const controller = require("../controllers/absenceController");
const auth = require("../middleware/authMiddleware");
const role = require("../middleware/roleMiddleware");

router.post("/submit", auth, role(["student"]), controller.submitAbsence);
router.get("/all", auth, role(["student", "teacher", "admin"]), controller.getAllAbsences);
router.patch("/:id/status", auth, role(["teacher", "admin"]), controller.updateAbsenceStatus);

module.exports = router;
