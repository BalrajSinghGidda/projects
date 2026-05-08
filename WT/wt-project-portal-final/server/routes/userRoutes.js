const express = require("express");
const router = express.Router();
const auth = require("../middleware/authMiddleware");
const role = require("../middleware/roleMiddleware");
const userController = require("../controllers/userController");

router.get("/", auth, role(["teacher", "admin"]), userController.listUsers);
router.post("/", auth, role(["teacher", "admin"]), userController.createUser);

router.patch("/me/name", auth, userController.updateOwnName);
router.patch("/me/password", auth, userController.changeOwnPassword);

router.get("/removal-requests", auth, role(["teacher", "admin"]), userController.listRemovalRequests);
router.post("/:id/removal-requests", auth, role(["teacher", "admin"]), userController.requestUserRemoval);
router.patch("/removal-requests/:id", auth, role(["admin"]), userController.reviewRemovalRequest);

router.get("/password-change-requests", auth, role(["teacher", "admin"]), userController.listPasswordChangeRequests);
router.post("/:id/password-change-requests", auth, role(["teacher"]), userController.requestStudentPasswordChange);
router.patch("/password-change-requests/:id", auth, role(["admin"]), userController.reviewPasswordChangeRequest);

router.patch("/:id", auth, role(["admin"]), userController.updateUserByAdmin);
router.delete("/:id", auth, role(["admin"]), userController.deleteUserByAdmin);

module.exports = router;
