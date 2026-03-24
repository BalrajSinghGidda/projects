
const express = require("express");
const router = express.Router();
const multer = require("multer");
const path = require("path");
const authMiddleware = require("../middleware/authMiddleware");
const role = require("../middleware/roleMiddleware");
const Project = require("../models/projectModel");

// Configure Multer Storage
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, "uploads/");
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + "-" + Math.round(Math.random() * 1e9);
    cb(null, file.fieldname + "-" + uniqueSuffix + path.extname(file.originalname));
  }
});

// File Filter
const fileFilter = (req, file, cb) => {
  const allowedTypes = /jpeg|jpg|png|gif|pdf|doc|docx|zip/;
  const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
  const mimetype = allowedTypes.test(file.mimetype);

  if (mimetype && extname) {
    return cb(null, true);
  } else {
    cb(new Error("Error: File type not supported!"));
  }
};

const upload = multer({
  storage: storage,
  fileFilter: fileFilter,
  limits: { fileSize: 5 * 1024 * 1024 } // 5MB limit
});

function ensureProjectMember(req, res, next) {
  const projectId = req.params.id;
  const userId = req.session.user.id;

  Project.isMember(projectId, userId, (memberErr, rows) => {
    if (memberErr) {
      return res.status(500).json({ error: memberErr });
    }
    if (!rows.length) {
      return res.status(403).json({ message: "You are not a member of this project" });
    }
    next();
  });
}

router.post("/project/:id", authMiddleware, role(["student"]), ensureProjectMember, upload.single("file"), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ message: "No file uploaded" });
  }

  // Ideally, save file info to database here linked to req.params.id
  res.json({ message: "File uploaded successfully", file: req.file });
});

module.exports = router;
