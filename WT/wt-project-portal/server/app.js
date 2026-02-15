const db = require("./config/db");
const path = require("path");
const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const session = require("express-session");

const app = express();
const server = http.createServer(app);
const io = new Server(server);

// 🔥 BODY PARSERS FIRST
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 🔥 SESSION BEFORE ROUTES (IMPORTANT FIX)
app.use(session({
  secret: "wt-secret",
  resave: false,
  saveUninitialized: false,
  cookie: { secure: false } // for localhost
}));

app.use(express.static(path.join(__dirname, "../public")));

// 🔥 ROUTES AFTER SESSION
const notificationController = require("./controllers/notificationController");
notificationController.setIO(io);
const notificationRoutes = require("./routes/notificationRoutes");
app.use("/api/notifications", notificationRoutes);

const authRoutes = require("./routes/authRoutes");
app.use("/api/auth", authRoutes);

const projectRoutes = require("./routes/projectRoutes");
app.use("/api/projects", projectRoutes);

const absenceRoutes = require("./routes/absenceRoutes");
app.use("/api/absence", absenceRoutes);

// test route
app.get("/", (req, res) => {
  res.send("WT Project Portal is running 🚀");
});

app.get("/test-db", (req, res) => {
  db.query("SELECT 1 + 1 AS result", (err, results) => {
    if (err) {
      return res.status(500).json({ error: err });
    }
    res.json({
      message: "Database is working 🎉",
      result: results[0].result
    });
  });
});

// socket connection
io.on("connection", (socket) => {
  console.log("User connected:", socket.id);
});

// start server
const PORT = 3000;
server.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

