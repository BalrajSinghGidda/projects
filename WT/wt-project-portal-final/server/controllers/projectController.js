const Project = require("../models/projectModel");
const User = require("../models/userModel");
const Deadline = require("../models/deadlineModel");

let ioInstance = null;
exports.setIO = (io) => {
  ioInstance = io;
};

// CREATE PROJECT
exports.createProject = (req, res) => {
  const { title, description, type, members, deadlineId } = req.body;
  const actor = req.session.user;
  const userId = actor.id;

  if (actor.role !== "student") {
    return res.status(403).json({ message: "Only students can submit projects" });
  }

  if (!title || !type || !deadlineId) {
    return res.status(400).json({ message: "Title, type and deadlineId are required" });
  }

  Deadline.findById(deadlineId, (deadlineErr, deadlines) => {
    if (deadlineErr) return res.status(500).json({ error: deadlineErr });
    if (!deadlines.length) return res.status(404).json({ message: "Deadline not found" });

    const deadline = deadlines[0];
    if (deadline.status !== "open") {
      return res.status(400).json({ message: "Deadline is closed" });
    }

    const dueDate = new Date(deadline.due_date);
    const now = new Date();
    if (dueDate < now) {
      return res.status(400).json({ message: "Deadline has passed" });
    }

    Project.create(title, description, type, userId, deadlineId, (err, result) => {
      if (err) return res.status(500).json({ error: err });

      const projectId = result.insertId;

      // add creator as member automatically
      Project.addMember(projectId, userId, (memberErr) => {
        if (memberErr) console.error("Failed to add creator as member:", memberErr);
      });

      // add other members if provided
      if (members && Array.isArray(members) && members.length > 0) {
        members.forEach((m) => {
          Project.addMember(projectId, m, (memberErr) => {
            if (memberErr) console.error(`Failed to add member ${m}:`, memberErr);
          });
        });
      }

      res.json({
        message: "Project submitted successfully 🚀",
        projectId
      });
    });
  });
};

// GET ALL PROJECTS (for teacher/admin)
exports.getAllProjects = (req, res) => {
  const actor = req.session.user;
  if (!actor || (actor.role !== "teacher" && actor.role !== "admin")) {
    return res.status(403).json({ message: "Access denied" });
  }

  Project.getAll((err, results) => {
    if (err) return res.status(500).json({ error: err });
    res.json(results);
  });
};

// GET PROJECTS OF CURRENT USER
exports.getMyProjects = (req, res) => {
  const userId = req.session.user.id;

  Project.getByUser(userId, (err, results) => {
    if (err) return res.status(500).json({ error: err });
    res.json(results);
  });
};

// GET MEMBERS OF A PROJECT
exports.getProjectMembers = (req, res) => {
  const { id } = req.params;

  Project.getMembers(id, (err, results) => {
    if (err) return res.status(500).json({ error: err });
    res.json(results);
  });
};

exports.addProjectMember = (req, res) => {
  const projectId = req.params.id;
  const { userId } = req.body;
  const actor = req.session.user;

  if (!userId) {
    return res.status(400).json({ message: "userId is required" });
  }

  if (actor.role !== "teacher" && actor.role !== "admin") {
    return res.status(403).json({ message: "Access denied" });
  }

  User.findById(userId, (userErr, userRows) => {
    if (userErr) return res.status(500).json({ error: userErr });
    if (!userRows.length) return res.status(404).json({ message: "User not found" });

    Project.addMember(projectId, userId, (err) => {
      if (err) {
        if (err.code === "ER_DUP_ENTRY") {
          return res.status(400).json({ message: "User already in project" });
        }
        return res.status(500).json({ error: err });
      }

      Project.getMembers(projectId, (membersErr, members) => {
        if (membersErr) return res.status(500).json({ error: membersErr });

        if (ioInstance) {
          ioInstance.emit("project_members_updated", {
            projectId: Number(projectId),
            members
          });
        }

        res.json({ message: "Member added successfully", members });
      });
    });
  });
};

exports.removeProjectMember = (req, res) => {
  const projectId = req.params.id;
  const userId = Number(req.params.userId);
  const actor = req.session.user;

  if (actor.role !== "teacher" && actor.role !== "admin") {
    return res.status(403).json({ message: "Access denied" });
  }

  Project.getById(projectId, (projectErr, projects) => {
    if (projectErr) return res.status(500).json({ error: projectErr });
    if (!projects.length) return res.status(404).json({ message: "Project not found" });

    const project = projects[0];
    if (Number(project.created_by) === userId) {
      return res.status(400).json({ message: "Cannot remove project creator" });
    }

    Project.removeMember(projectId, userId, (err, result) => {
      if (err) return res.status(500).json({ error: err });
      if (!result.affectedRows) return res.status(404).json({ message: "Member not found in project" });

      Project.getMembers(projectId, (membersErr, members) => {
        if (membersErr) return res.status(500).json({ error: membersErr });

        if (ioInstance) {
          ioInstance.emit("project_members_updated", {
            projectId: Number(projectId),
            members
          });
        }

        res.json({ message: "Member removed successfully", members });
      });
    });
  });
};



exports.getProjectById = (req,res)=>{
  const id=req.params.id;
  Project.getById(id,(err,results)=>{
    if(err) return res.status(500).json({error:err});
    res.json(results[0]);
  });
};

exports.searchProjects = (req,res)=>{
  const {q,type}=req.query;
  Project.search(q,type,(err,results)=>{
    if(err) return res.status(500).json({error:err});
    res.json(results);
  });
};

exports.getProjectsByDeadline = (req, res) => {
  const actor = req.session.user;
  if (!actor || (actor.role !== "teacher" && actor.role !== "admin")) {
    return res.status(403).json({ message: "Access denied" });
  }

  const deadlineId = req.params.deadlineId;
  Project.getByDeadline(deadlineId, (err, results) => {
    if (err) return res.status(500).json({ error: err });
    res.json(results);
  });
};
