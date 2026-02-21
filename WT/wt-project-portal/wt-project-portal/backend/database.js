const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');

const db = new sqlite3.Database('./database.db', (err) => {
    if (err) {
        console.error(err.message);
    }
    console.log('Connected to the database.');
});

const setupDatabase = () => {
    db.serialize(() => {
        // Create users table
        db.run(`CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT CHECK(role IN ('student', 'teacher', 'admin'))
        )`);

        // Create projects table
        db.run(`CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT,
            file_path TEXT,
            assignment_id INTEGER,
            submitted_by_user_id INTEGER,
            FOREIGN KEY (assignment_id) REFERENCES assignments (id),
            FOREIGN KEY (submitted_by_user_id) REFERENCES users (id)
        )`);

        // Create announcements table
        db.run(`CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            created_by_user_id INTEGER,
            FOREIGN KEY (created_by_user_id) REFERENCES users (id)
        )`);

        // Create absences table
        db.run(`CREATE TABLE IF NOT EXISTS absences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reason TEXT,
            user_id INTEGER,
            viva_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (viva_id) REFERENCES vivas (id)
        )`);

        // Create vivas table
        db.run(`CREATE TABLE IF NOT EXISTS vivas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            viva_date TEXT,
            scheduled_by_user_id INTEGER,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (scheduled_by_user_id) REFERENCES users (id)
        )`);

        // Create assignments table
        db.run(`CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            created_by_user_id INTEGER,
            FOREIGN KEY (created_by_user_id) REFERENCES users (id)
        )`);

        // Insert a default admin user if one doesn't exist
        db.get('SELECT * FROM users WHERE username = ?', ['admin'], (err, user) => {
            if (err) {
                return console.log(err.message);
            }
            if (!user) {
                bcrypt.hash('admin', 10, (err, hash) => {
                    if (err) {
                        return console.log(err.message);
                    }
                    db.run('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', ['admin', hash, 'admin']);
                });
            }
        });
    });
};

module.exports = {
    db,
    setupDatabase
};
