const express = require("express");
const router = express.Router();
const auth = require("../middleware/authMiddleware");
const role = require("../middleware/roleMiddleware");
const userController = require("../controllers/userController");

router.get("/", auth, role(["teacher", "admin"]), userController.listUsers);
router.post("/", auth, role(["teacher", "admin"]), userController.createUser);
router.get("/removal-requests", auth, role(["teacher", "admin"]), userController.listRemovalRequests);
router.post("/:id/removal-requests", auth, role(["teacher", "admin"]), userController.requestUserRemoval);
router.patch("/removal-requests/:id", auth, role(["admin"]), userController.reviewRemovalRequest);

module.exports = router;
