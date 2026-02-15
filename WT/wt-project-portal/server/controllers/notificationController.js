const Notification = require("../models/notificationModel");

let ioInstance = null;
exports.setIO = (io) => {
  ioInstance = io;
};

// SEND NOTIFICATION (teacher)
exports.sendNotification = (req, res) => {
  const { title, message } = req.body;
  const teacherId = req.session.user.id;

  if (!title || !message) {
    return res.status(400).json({ message: "Missing fields" });
  }

  Notification.create(title, message, teacherId, (err, result) => {
    if (err) return res.status(500).json({ error: err });

    const payload = {
      title,
      message,
      sent_by: teacherId
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

