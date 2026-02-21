const Notification = require("../models/notificationModel");

let ioInstance = null;
exports.setIO = (io) => {
  ioInstance = io;
};

// SEND NOTIFICATION (teacher)
exports.sendNotification = (req, res) => {
  const { title, message } = req.body;
  const user = req.session.user;

  if (!user || (user.role !== 'teacher' && user.role !== 'admin')) {
    return res.status(403).json({ message: "Access denied. Teachers only." });
  }

  const teacherId = user.id;

  if (!title || !message) {
    return res.status(400).json({ message: "Missing fields" });
  }

  Notification.create(title, message, teacherId, (err, result) => {
    if (err) return res.status(500).json({ error: err });

    const payload = {
      title,
      message,
      sent_by: teacherId, // sending ID, frontend might want name but this is what was there
      sender: user.name, // adding sender name for frontend convenience
      created_at: new Date()
    };

    // 🔥 broadcast to all connected clients
    if (ioInstance) {
      ioInstance.emit("new_notification", payload);
    }

    res.json({ message: "Notification sent 🔔" });
  });
};

// GET ALL NOTIFICATIONS
exports.getNotifications = (req, res) => {
  Notification.getAll((err, results) => {
    if (err) return res.status(500).json({ error: err });
    res.json(results);
  });
};

