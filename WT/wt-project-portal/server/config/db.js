const mysql = require("mysql2");

const db = mysql.createConnection({
  host: "localhost",
  user: "connectBase",
  password: "connectBase",   // <-- put your MySQL password here
  database: "wt_portal"
});

db.connect((err) => {
  if (err) {
    console.error("❌ Database connection failed:", err);
    return;
  }
  console.log("✅ Connected to MySQL database");
});

module.exports = db;

