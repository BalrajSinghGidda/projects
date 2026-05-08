const express = require("express");
const router = express.Router();
const auth = require("../middleware/authMiddleware");
const role = require("../middleware/roleMiddleware");
const userController = require("../controllers/userController");

router.get("/", auth, role(["teacher", "admin"]), userController.listUsers);
router.post("/", auth, role(["teacher", "admin"]), userController.createUser);
router.delete("/:id", auth, role(["admin"]), userController.deleteUser);

module.exports = router;
