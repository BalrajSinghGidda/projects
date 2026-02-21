const express = require('express');
const path = require('path');
const { db, setupDatabase } = require('./database.js');
const bcrypt = require('bcrypt');
const session = require('express-session');
const SQLiteStore = require('connect-sqlite3')(session);
const multer = require('multer');

const app = express();
const port = 3000;
const upload = multer({ dest: 'uploads/' });

// Set up the database
setupDatabase();

// Middleware to parse JSON bodies
app.use(express.json());

// Session middleware
app.use(session({
    store: new SQLiteStore({ db: 'sessions.db' }),
    secret: 'a very secret key',
    resave: false,
    saveUninitialized: false,
    cookie: {
        maxAge: 1000 * 60 * 60 * 24 // 1 day
    }
}));

// Serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, '../public')));
app.use('/uploads', express.static(path.join(__dirname, '..', 'uploads')));

// Auth middleware
const isAuthenticated = (req, res, next) => {
    if (req.session.userId) {
        next();
    } else {
        if (req.originalUrl.startsWith('/api/')) {
            res.status(401).json({ error: 'Unauthorized' });
        } else {
            res.redirect('/login');
        }
    }
};

// Page routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../public', 'index.html'));
});

app.get('/admin-home', isAuthenticated, (req, res) => {
    if (req.session.role !== 'admin') return res.status(403).send('Access denied');
    res.sendFile(path.join(__dirname, '../public', 'index.html'));
});

app.get('/teacher-home', isAuthenticated, (req, res) => {
    if (req.session.role !== 'teacher') return res.status(403).send('Access denied');
    res.sendFile(path.join(__dirname, '../public', 'index.html'));
});

app.get('/student-home', isAuthenticated, (req, res) => {
    if (req.session.role !== 'student') return res.status(403).send('Access denied');
    res.sendFile(path.join(__dirname, '../public', 'index.html'));
});

app.get('/projects', isAuthenticated, (req, res) => {
    res.sendFile(path.join(__dirname, '../public', 'index.html'));
});

app.get('/announcements', isAuthenticated, (req, res) => {
    res.sendFile(path.join(__dirname, '../public', 'index.html'));
});

app.get('/submit', isAuthenticated, (req, res) => {
    res.sendFile(path.join(__dirname, '../public', 'index.html'));
});

app.get('/absence', isAuthenticated, (req, res) => {
    res.sendFile(path.join(__dirname, '../public', 'index.html'));
});

app.get('/schedule-viva', isAuthenticated, (req, res) => {
    if (req.session.role !== 'teacher' && req.session.role !== 'admin') return res.status(403).send('Access denied');
    res.sendFile(path.join(__dirname, '../public', 'index.html'));
});

app.get('/create-assignment', isAuthenticated, (req, res) => {
    if (req.session.role !== 'teacher' && req.session.role !== 'admin') return res.status(403).send('Access denied');
    res.sendFile(path.join(__dirname, '../public', 'index.html'));
});


// API Endpoints
app.post('/api/register', isAuthenticated, (req, res) => {
    const { username, password, role } = req.body;
    const { role: userRole } = req.session;

    if (userRole === 'teacher' && role === 'student') {
        // Teachers can register students
        bcrypt.hash(password, 10, (err, hash) => {
            if (err) {
                return res.status(500).json({ error: err.message });
            }
            db.run('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', [username, hash, role], function(err) {
                if (err) {
                    return res.status(400).json({ error: err.message });
                }
                res.json({ id: this.lastID });
            });
        });
    } else if (userRole === 'admin') {
        // Admins can register anyone
        bcrypt.hash(password, 10, (err, hash) => {
            if (err) {
                return res.status(500).json({ error: err.message });
            }
            db.run('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', [username, hash, role], function(err) {
                if (err) {
                    return res.status(400).json({ error: err.message });
                }
                res.json({ id: this.lastID });
            });
        });
    } else {
        res.status(403).json({ error: 'You are not authorized to register users.' });
    }
});


app.post('/api/login', (req, res) => {
    const { username, password } = req.body;
    db.get('SELECT * FROM users WHERE username = ?', [username], (err, user) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        if (!user) {
            return res.status(400).json({ error: 'User not found' });
        }
        bcrypt.compare(password, user.password, (err, result) => {
            if (result) {
                req.session.userId = user.id;
                req.session.role = user.role;
                res.json({ message: 'Logged in successfully', role: user.role });
            } else {
                res.status(401).json({ error: 'Invalid password' });
            }
        });
    });
});

app.get('/api/logout', (req, res) => {
    req.session.destroy();
    res.redirect('/login');
});

app.get('/api/me', isAuthenticated, (req, res) => {
    res.json({ userId: req.session.userId, role: req.session.role });
});

app.get('/api/stats', isAuthenticated, (req, res) => {
    if (req.session.role !== 'admin') {
        return res.status(403).json({ error: 'Unauthorized' });
    }
    db.get('SELECT COUNT(*) as userCount FROM users', (err, user) => {
        if(err) return res.status(500).json({ error: err.message });
        db.get('SELECT COUNT(*) as projectCount FROM projects', (err, project) => {
            if(err) return res.status(500).json({ error: err.message });
            res.json({ totalUsers: user.userCount, totalProjects: project.projectCount });
        });
    });
});

app.get('/api/projects', isAuthenticated, (req, res) => {
    db.all('SELECT * FROM projects', [], (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json({ projects: rows });
    });
});

app.post('/api/projects', isAuthenticated, upload.single('projectFile'), (req, res) => {
    const { title, link, assignment_id } = req.body;
    const filePath = req.file ? req.file.path : null;
    db.run(`INSERT INTO projects (title, link, file_path, assignment_id, submitted_by_user_id) VALUES (?, ?, ?, ?, ?)`, [title, link, filePath, assignment_id, req.session.userId], function(err) {
        if (err) {
            res.status(400).json({ error: err.message });
            return;
        }
        res.json({ id: this.lastID });
    });
});

app.get('/api/announcements', isAuthenticated, (req, res) => {
    db.all('SELECT * FROM announcements', [], (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json({ announcements: rows });
    });
});

app.post('/api/announcements', isAuthenticated, (req, res) => {
    if (req.session.role !== 'teacher' && req.session.role !== 'admin') {
        return res.status(403).json({ error: 'Only teachers and admins can create announcements' });
    }
    const { content } = req.body;
    db.run(`INSERT INTO announcements (content, created_by_user_id) VALUES (?, ?)`, [content, req.session.userId], function(err) {
        if (err) {
            res.status(400).json({ error: err.message });
            return;
        }
        res.json({ id: this.lastID });
    });
});

app.post('/api/absences', isAuthenticated, (req, res) => {
    const { reason, viva_id } = req.body;
    db.run(`INSERT INTO absences (reason, user_id, viva_id) VALUES (?, ?, ?)`, [reason, req.session.userId, viva_id], function(err) {
        if (err) {
            res.status(400).json({ error: err.message });
            return;
        }
        res.json({ id: this.lastID });
    });
});

app.get('/api/vivas', isAuthenticated, (req, res) => {
    db.all('SELECT * FROM vivas', [], (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json({ vivas: rows });
    });
});

app.post('/api/vivas', isAuthenticated, (req, res) => {
    if (req.session.role !== 'teacher' && req.session.role !== 'admin') {
        return res.status(403).json({ error: 'Only teachers and admins can schedule vivas' });
    }
    const { project_id, viva_date } = req.body;
    db.run(`INSERT INTO vivas (project_id, viva_date, scheduled_by_user_id) VALUES (?, ?, ?)`, [project_id, viva_date, req.session.userId], function(err) {
        if (err) {
            res.status(400).json({ error: err.message });
            return;
        }
        res.json({ id: this.lastID });
    });
});

app.get('/api/assignments', isAuthenticated, (req, res) => {
    db.all('SELECT * FROM assignments', [], (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json({ assignments: rows });
    });
});

app.post('/api/assignments', isAuthenticated, (req, res) => {
    if (req.session.role !== 'teacher' && req.session.role !== 'admin') {
        return res.status(403).json({ error: 'Only teachers and admins can create assignments' });
    }
    const { title, description } = req.body;
    db.run(`INSERT INTO assignments (title, description, created_by_user_id) VALUES (?, ?, ?)`, [title, description, req.session.userId], function(err) {
        if (err) {
            res.status(400).json({ error: err.message });
            return;
        }
        res.json({ id: this.lastID });
    });
});

app.get('/login', (req, res) => {
    res.sendFile(path.join(__dirname, '../public', 'login.html'));
});

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});
