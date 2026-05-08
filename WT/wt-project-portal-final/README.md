# NexusEdu

A comprehensive web-based project and viva management system designed for
educational institutions. This portal enables students, teachers, and
administrators to collaborate on project submissions, manage deadlines, handle
absence requests, and communicate through real-time notifications.

## Overview

NexusEdu is a full-stack web application that streamlines the
academic project management workflow with role-based access control, real-time
updates, and intuitive user interfaces for students, teachers, and
administrators.

### Key Features

- **🔐 Role-Based Access Control**: Three distinct user roles (Student, Teacher,
  Admin) with customized interfaces and permissions
- **📚 Project Management**: Create, submit, and manage major/minor projects
  with file uploads
- **⏰ Deadline Management**: Teachers and admins can set submission deadlines;
  students submit under active deadlines
- **👥 Team Collaboration**: Multi-member project support with real-time member
  management
- **📢 Real-time Notifications**: Socket.IO-powered instant notifications across
  all users
- **🚫 Absence Management**: Students submit absence requests; teachers/admins
  approve or reject
- **📊 Dashboard Analytics**: Role-specific dashboards with KPIs and system
  statistics
- **🌓 Dark Mode**: Persistent theme preference with light/dark mode toggle
- **📱 Responsive Design**: Mobile-first interface with MS Office-inspired flat
  design

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Node.js, Express.js
- **Database**: MySQL / MariaDB
- **Real-time Communication**: Socket.IO
- **Authentication**: Session-based (express-session)
- **File Uploads**: Multer
- **Password Security**: bcrypt

## 📁 Project Structure

```
nexusedu/
├── server/
│   ├── app.js                      # Main application entry point
│   ├── config/
│   │   ├── db.js                   # Database connection
│   │   └── session.js              # Session configuration
│   ├── middleware/
│   │   ├── authMiddleware.js       # Authentication checks
│   │   └── roleMiddleware.js       # Role-based access control
│   ├── models/
│   │   ├── absenceModel.js         # Absence request queries
│   │   ├── dashboardModel.js       # Dashboard statistics
│   │   ├── deadlineModel.js        # Submission deadlines
│   │   ├── notificationModel.js    # Notifications
│   │   ├── projectModel.js         # Project & member management
│   │   └── userModel.js            # User management
│   ├── controllers/
│   │   ├── absenceController.js    # Absence request logic
│   │   ├── authController.js       # Authentication logic
│   │   ├── dashboardController.js  # Dashboard data
│   │   ├── deadlineController.js   # Deadline management
│   │   ├── notificationController.js # Notification handling
│   │   ├── projectController.js    # Project operations
│   │   └── userController.js       # User operations
│   └── routes/
│       ├── absenceRoutes.js        # Absence API endpoints
│       ├── authRoutes.js           # Auth API endpoints
│       ├── dashboardRoutes.js      # Dashboard API
│       ├── deadlineRoutes.js       # Deadline API
│       ├── notificationRoutes.js   # Notification API
│       ├── projectRoutes.js        # Project API endpoints
│       ├── uploadRoutes.js         # File upload endpoints
│       └── userRoutes.js           # User API endpoints
├── public/
│   ├── pages/
│   │   ├── login.html              # Login page
│   │   ├── dashboard.html          # Main dashboard redirect
│   │   ├── student-dashboard.html  # Student interface
│   │   ├── teacher-dashboard.html  # Teacher interface
│   │   ├── admin-dashboard.html    # Admin interface
│   │   ├── project.html            # Project management
│   │   ├── notifications.html      # Notifications
│   │   └── absence.html            # Absence requests
│   ├── css/
│   │   └── styles.css              # Application styles
│   └── js/
│       └── main.js                 # Client-side JavaScript
├── uploads/                         # User-uploaded project files
├── database-schema.sql              # Database schema & seed data
├── .env                             # Environment configuration
├── .env.example                     # Environment template
├── package.json                     # Dependencies
├── SETUP.md                         # Detailed setup guide
├── QUICKSTART.txt                   # Quick reference guide
└── progress.md                      # Development changelog
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v14 or higher)
- **MySQL** or **MariaDB**
- **npm** (comes with Node.js)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nexusedu
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Setup MySQL database**

   Create database and user:
   ```bash
   sudo mysql
   ```

   In MySQL prompt:
   ```sql
   CREATE USER 'connectBase'@'localhost' IDENTIFIED BY 'connectBase';
   CREATE DATABASE wt_portal;
   GRANT ALL PRIVILEGES ON wt_portal.* TO 'connectBase'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

4. **Import database schema**
   ```bash
   mysql -u connectBase -pconnectBase wt_portal < database-schema.sql
   ```

5. **Configure environment variables**

   Copy `.env.example` to `.env` and update if needed:
   ```bash
   cp .env.example .env
   ```

   Default configuration:
   ```
   DB_HOST=localhost
   DB_USER=connectBase
   DB_PASS=connectBase
   DB_NAME=wt_portal
   SESSION_SECRET=wt-secret
   PORT=3000
   ```

6. **Start the application**
   ```bash
   npm start
   ```

   Or for development with auto-reload:
   ```bash
   npm run dev
   ```

7. **Access the portal**

   Open your browser and navigate to: `http://localhost:3000`

## 👤 Default User Accounts

The database schema includes three pre-configured test accounts:

| Role    | Email               | Password   |
| ------- | ------------------- | ---------- |
| Admin   | admin@example.com   | admin123   |
| Teacher | teacher@example.com | teacher123 |
| Student | student@example.com | student123 |

⚠️ **Security Note**: Change these passwords in production environments!

## 📖 User Roles & Permissions

### Student Role

- Submit projects under active deadlines
- Upload project files
- View own projects and deadlines
- Submit absence requests
- View notifications
- Manage personal profile

### Teacher Role

- Create and manage submission deadlines
- Review and approve/reject absence requests
- View all projects and student submissions
- Add/remove members from projects
- Send notifications to students
- Access operational KPI dashboard

### Admin Role

- Full system administration access
- User management (view all users)
- Create and manage submission deadlines
- Review absence requests
- Project oversight and member management
- System-wide notifications
- Access governance KPI dashboard

## 🔌 API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### Projects

- `GET /api/projects` - List all projects
- `GET /api/projects/my` - Get user's projects
- `GET /api/projects/:id` - Get project details
- `POST /api/projects` - Create new project (student)
- `GET /api/projects/search?q=query` - Search projects
- `GET /api/projects/deadline/:deadlineId` - Projects by deadline
- `POST /api/projects/:id/members` - Add project member (teacher/admin)
- `GET /api/projects/:id/members` - List project members
- `DELETE /api/projects/:id/members/:userId` - Remove member (teacher/admin)

### Deadlines

- `GET /api/deadlines` - List all deadlines
- `POST /api/deadlines` - Create deadline (teacher/admin)

### Absence Requests

- `GET /api/absence` - List absence requests (role-filtered)
- `POST /api/absence` - Submit absence request (student)
- `PATCH /api/absence/:id/approve` - Approve request (teacher/admin)
- `PATCH /api/absence/:id/reject` - Reject request (teacher/admin)

### Notifications

- `GET /api/notifications` - Get all notifications
- `POST /api/notifications` - Create notification (teacher/admin)

### Dashboard

- `GET /api/dashboard/stats` - Get system statistics

### Users

- `GET /api/users` - List all users (teacher/admin)

### Uploads

- `POST /api/upload/project/:projectId` - Upload project file

## 🌐 WebSocket Events

The application uses Socket.IO for real-time updates:

- `notification` - New notification broadcast
- `project-member-added` - Member added to project
- `project-member-removed` - Member removed from project

## 🎨 UI Features

- **MS Office-Inspired Design**: Clean, professional flat interface
- **Role-Based Theming**: Visual distinction between student, teacher, and admin
  interfaces
- **Dark Mode**: Toggle between light and dark themes with persistent preference
- **Responsive Layout**: Mobile-first design that adapts to all screen sizes
- **Real-time Updates**: Instant notifications and project updates via WebSocket

## 🧪 Testing

Test database connection:

```bash
curl http://localhost:3000/test-db
```

Expected response:

```json
{ "message": "Database is working 🎉", "result": 2 }
```

## 🔧 Development

### Adding New Users Programmatically

**Via API:**

```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "role": "student"
  }'
```

**Via Database:**

```bash
# Generate password hash
node -e "require('bcrypt').hash('mypassword', 10).then(h => console.log(h))"

# Insert user
mysql -u connectBase -pconnectBase wt_portal \
  -e "INSERT INTO users (name, email, password, role) VALUES ('Name', 'email@example.com', 'HASH_HERE', 'student');"
```

## 📊 Database Schema

The application uses the following main tables:

- `users` - User accounts with role-based access
- `projects` - Project submissions
- `project_members` - Project team members (junction table)
- `submission_deadlines` - Project submission deadlines
- `absence_requests` - Student absence requests
- `notifications` - System notifications

See `database-schema.sql` for complete schema definition.

## 🐛 Troubleshooting

**Database connection failed:**

- Ensure MySQL is running: `systemctl status mysql`
- Verify credentials in `.env` match your MySQL configuration
- Check that database `wt_portal` exists

**Port 3000 already in use:**

- Change `PORT` in `.env` file
- Or stop the process: `lsof -ti:3000 | xargs kill`

**Module not found errors:**

- Run `npm install` to install dependencies

**Tables don't exist:**

- Import schema:
  `mysql -u connectBase -pconnectBase wt_portal < database-schema.sql`

## 📝 License

ISC

## 🤝 Contributing

This is an educational project. Feel free to fork and modify for your own use.

## 📮 Support

For detailed setup instructions, see `SETUP.md`. For quick reference, see
`QUICKSTART.txt`. For development history, see `progress.md`.

---

**Note**: This project was developed as part of a Web Technology (WT) course
project.
