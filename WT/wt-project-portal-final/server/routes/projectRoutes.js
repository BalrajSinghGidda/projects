const express = require("express");
const router = express.Router();
const projectController = require("../controllers/projectController");
const auth = require("../middleware/authMiddleware");

router.post("/create", auth, projectController.createProject);
router.get("/all", auth, projectController.getAllProjects);
router.get("/mine", auth, projectController.getMyProjects);
router.get("/:id/members", auth, projectController.getProjectMembers);
router.post("/:id/members", auth, projectController.addProjectMember);
router.delete("/:id/members/:userId", auth, projectController.removeProjectMember);
router.get("/deadline/:deadlineId", auth, projectController.getProjectsByDeadline);

router.get('/search', auth, projectController.searchProjects);
router.get('/:id', auth, projectController.getProjectById);
module.exports = router;
