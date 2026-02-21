const Project = require("../models/projectModel");

// CREATE PROJECT
exports.createProject = (req, res) => {
  const { title, description, type, members } = req.body;
  const userId = req.session.user.id;

  if (!title || !type) {
    return res.status(400).json({ message: "Title and type required" });
  }

  Project.create(title, description, type, userId, (err, result) => {
    if (err) return res.status(500).json({ error: err });

    const projectId = result.insertId;

    // add creator as member automatically
    Project.addMember(projectId, userId, (err) => {
        if (err) console.error("Failed to add creator as member:", err);
    });

    // add other members if provided
    if (members && Array.isArray(members) && members.length > 0) {
      members.forEach((m) => {
        Project.addMember(projectId, m, (err) => {
            if (err) console.error(`Failed to add member ${m}:`, err);
        });
      });
    }

    res.json({
      message: "Project created successfully 🚀",
      projectId
    });
  });
};

// GET ALL PROJECTS (for teacher/admin)
exports.getAllProjects = (req, res) => {
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
