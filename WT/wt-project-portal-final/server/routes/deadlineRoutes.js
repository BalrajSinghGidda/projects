const express = require("express");
const router = express.Router();
const auth = require("../middleware/authMiddleware");
const deadlineController = require("../controllers/deadlineController");

router.post("/", auth, deadlineController.createDeadline);
router.get("/", auth, deadlineController.listDeadlines);

module.exports = router;
