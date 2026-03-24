const express = require("express");
const router = express.Router();
const controller = require("../controllers/notificationController");
const auth = require("../middleware/authMiddleware");
const role = require("../middleware/roleMiddleware");

router.post("/send", auth, role(["teacher", "admin"]), controller.sendNotification);

router.get("/all", auth, role(["student", "teacher", "admin"]), controller.getNotifications);

module.exports = router;
