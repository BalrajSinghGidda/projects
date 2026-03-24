const express = require("express");
const router = express.Router();
const authController = require("../controllers/authController");
const auth = require("../middleware/authMiddleware");

router.post("/register", authController.register);
router.post("/login", authController.login);
router.get("/logout", auth, authController.logout);
router.get("/me", auth, authController.me);

module.exports = router;
