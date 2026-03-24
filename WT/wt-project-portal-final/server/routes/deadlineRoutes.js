const express = require("express");
const router = express.Router();
const auth = require("../middleware/authMiddleware");
const role = require("../middleware/roleMiddleware");
const deadlineController = require("../controllers/deadlineController");

router.post("/", auth, role(["teacher", "admin"]), deadlineController.createDeadline);
router.get("/", auth, role(["student", "teacher", "admin"]), deadlineController.listDeadlines);

module.exports = router;
