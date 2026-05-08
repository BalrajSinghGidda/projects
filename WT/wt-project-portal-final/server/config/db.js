const mysql = require("mysql2");
require("dotenv").config();

const db = mysql.createConnection({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASS,
  database: process.env.DB_NAME
});

db.connect((err) => {
  if (err) {
    console.error("❌ Database connection failed:", err);
    return;
  }
  console.log("✅ Connected to MySQL database");
  runMigrations();
});

function runMigrations() {
  const migrations = [
    `
      CREATE TABLE IF NOT EXISTS submission_deadlines (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(200) NOT NULL,
        type ENUM('major', 'minor') NOT NULL,
        due_date DATETIME NOT NULL,
        description TEXT,
        status ENUM('open', 'closed') DEFAULT 'open',
        created_by INT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `,
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS deadline_id INT NULL",
    "ALTER TABLE absence_requests ADD COLUMN IF NOT EXISTS reviewed_by INT NULL",
    "ALTER TABLE absence_requests ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP NULL",
    `
      CREATE TABLE IF NOT EXISTS user_removal_requests (
        id INT AUTO_INCREMENT PRIMARY KEY,
        target_user_id INT NOT NULL,
        requested_by INT NOT NULL,
        reason TEXT,
        status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
        reviewed_by INT NULL,
        reviewed_at TIMESTAMP NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (target_user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (requested_by) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
      )
    `
  ];

  let index = 0;
  const executeNext = () => {
    if (index >= migrations.length) {
      console.log("✅ Database migrations applied");
      return;
    }

    db.query(migrations[index], (migrationErr) => {
      if (migrationErr) {
        console.error("❌ Migration failed:", migrationErr);
        return;
      }

      index += 1;
      executeNext();
    });
  };

  executeNext();
}

module.exports = db;
