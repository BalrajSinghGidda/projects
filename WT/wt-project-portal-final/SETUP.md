# 🚀 WT Project Portal - Setup Guide

## ✅ Current Configuration

**Database Connection:**
- Host: `localhost`
- User: `connectBase`
- Password: `connectBase`
- Database: `wt_portal`
- Port: `3000` (Web server)

## 📋 Prerequisites (NixOS)

You need Node.js and MySQL/MariaDB installed:

```bash
# Option 1: Temporary shell (recommended for testing)
nix-shell -p nodejs mysql80

# Option 2: Add to your configuration.nix permanently
environment.systemPackages = with pkgs; [ nodejs mysql80 ];
```

## 🔧 Setup Steps

### 1. Install Node Dependencies
Dependencies are already installed (node_modules exists), but if needed:
```bash
npm install
```

### 2. Setup MySQL Database

**Start MySQL service:**
```bash
# On NixOS, you may need to enable MySQL in configuration.nix:
services.mysql = {
  enable = true;
  package = pkgs.mysql80;
};

# Or start manually if already configured
sudo systemctl start mysql
```

**Create database user:**
```bash
# Login as root
sudo mysql

# Run these commands in MySQL prompt:
CREATE USER 'connectBase'@'localhost' IDENTIFIED BY 'connectBase';
CREATE DATABASE wt_portal;
GRANT ALL PRIVILEGES ON wt_portal.* TO 'connectBase'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**Import the database schema:**
```bash
mysql -u connectBase -pconnectBase wt_portal < database-schema.sql
```

### 3. Verify Configuration

Check that `.env` file has correct settings:
```bash
cat .env
```

Should contain:
```
DB_HOST=localhost
DB_USER=connectBase
DB_PASS=connectBase
DB_NAME=wt_portal
SESSION_SECRET=wt-secret
PORT=3000
```

### 4. Test Database Connection
```bash
npm start &
curl http://localhost:3000/test-db
```

You should see: `{"message":"Database is working 🎉","result":2}`

## 🎯 Running the Application

**Production mode:**
```bash
npm start
```

**Development mode (auto-reload):**
```bash
npm run dev
```

**Access the application:**
- Open browser: `http://localhost:3000`
- Login page: `http://localhost:3000/pages/login.html`

## 👤 Default User Accounts

Three default accounts are created in the database:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@example.com | admin123 |
| Teacher | teacher@example.com | teacher123 |
| Student | student@example.com | student123 |

## ➕ Creating New Users

**Option 1: Register via API (recommended)**
```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Name",
    "email": "your.email@example.com",
    "password": "yourpassword",
    "role": "student"
  }'
```

**Option 2: Insert directly into database**
```bash
# Generate a password hash first
node -e "require('bcrypt').hash('mypassword', 10).then(h => console.log(h))"

# Then insert into MySQL
mysql -u connectBase -pconnectBase wt_portal -e \
  "INSERT INTO users (name, email, password, role) VALUES ('Name', 'email@example.com', 'PASTE_HASH_HERE', 'student');"
```

**Option 3: Use the registration page**
- Navigate to the login page
- Look for a "Register" or "Sign Up" link (if available in the UI)

## 📁 Project Structure

```
wt-project-portal-final/
├── server/
│   ├── app.js              # Main server file
│   ├── config/             # Database & session config
│   ├── controllers/        # Business logic
│   ├── models/             # Database models
│   ├── routes/             # API routes
│   └── middleware/         # Auth middleware
├── public/
│   ├── pages/              # HTML pages
│   ├── css/                # Stylesheets
│   └── js/                 # Client-side JavaScript
├── .env                    # Environment variables
├── database-schema.sql     # Database schema
└── package.json            # Dependencies
```

## 🔍 Useful Commands

**Check if server is running:**
```bash
curl http://localhost:3000
```

**View database tables:**
```bash
mysql -u connectBase -pconnectBase wt_portal -e "SHOW TABLES;"
```

**View all users:**
```bash
mysql -u connectBase -pconnectBase wt_portal -e "SELECT id, name, email, role FROM users;"
```

**Stop the server:**
```bash
# If running in foreground: Ctrl+C
# If running in background:
pkill -f "node server/app.js"
```

## 🐛 Troubleshooting

**Problem: "Database connection failed"**
- Check if MySQL is running: `systemctl status mysql`
- Verify credentials in `.env` match your MySQL user

**Problem: "Port 3000 already in use"**
- Change PORT in `.env` file
- Or kill the process: `lsof -ti:3000 | xargs kill`

**Problem: "Cannot find module"**
- Run: `npm install`

**Problem: "Table doesn't exist"**
- Run: `mysql -u connectBase -pconnectBase wt_portal < database-schema.sql`
