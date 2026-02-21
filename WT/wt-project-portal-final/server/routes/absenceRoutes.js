const express = require("express");
const router = express.Router();
const controller = require("../controllers/absenceController");
const auth = require("../middleware/authMiddleware");

router.post("/submit", auth, controller.submitAbsence);
router.get("/all", auth, controller.getAllAbsences);

module.exports = router;

