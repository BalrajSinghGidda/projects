const express = require("express");
const router = express.Router();
const projectController = require("../controllers/projectController");
const auth = require("../middleware/authMiddleware");

router.post("/create", auth, projectController.createProject);
router.get("/all", auth, projectController.getAllProjects);
router.get("/mine", auth, projectController.getMyProjects);
router.get("/:id/members", auth, projectController.getProjectMembers);

module.exports = router;

