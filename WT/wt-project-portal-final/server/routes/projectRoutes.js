const express = require("express");
const router = express.Router();
const projectController = require("../controllers/projectController");
const auth = require("../middleware/authMiddleware");
const role = require("../middleware/roleMiddleware");

router.post("/create", auth, role(["student"]), projectController.createProject);
router.get("/all", auth, role(["teacher", "admin"]), projectController.getAllProjects);
router.get("/mine", auth, projectController.getMyProjects);
router.get("/:id/members", auth, projectController.getProjectMembers);
router.post("/:id/members", auth, role(["teacher", "admin"]), projectController.addProjectMember);
router.delete("/:id/members/:userId", auth, role(["teacher", "admin"]), projectController.removeProjectMember);
router.get("/deadline/:deadlineId", auth, role(["teacher", "admin"]), projectController.getProjectsByDeadline);

router.get('/search', auth, projectController.searchProjects);
router.get('/:id', auth, projectController.getProjectById);
module.exports = router;
