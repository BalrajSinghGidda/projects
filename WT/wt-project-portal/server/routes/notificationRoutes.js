const express = require("express");
const router = express.Router();
const controller = require("../controllers/notificationController");
const auth = require("../middleware/authMiddleware");

// teacher/admin only (you can later restrict by role)
router.post("/send", auth, controller.sendNotification);

router.get("/all", auth, controller.getNotifications);

module.exports = router;

