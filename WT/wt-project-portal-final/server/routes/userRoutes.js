const express = require("express");
const router = express.Router();
const auth = require("../middleware/authMiddleware");
const role = require("../middleware/roleMiddleware");
const userController = require("../controllers/userController");

router.get("/", auth, role(["teacher", "admin"]), userController.listUsers);

module.exports = router;
