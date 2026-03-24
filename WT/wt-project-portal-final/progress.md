# WT Project Portal — Progress Log

Last updated: 2026-03-22 (UTC)

## Update Policy
- This file is now maintained as a running changelog.
- Every major and minor change should be appended to the "Change Log" section with:
  - timestamp (UTC),
  - change type (`major` or `minor`),
  - summary of what changed,
  - affected files.
- Newest entries should appear at the top of the log.

## Project Goal
Build a web-based class project/viva management portal with:
- Role-based access (`student`, `teacher`, `admin`)
- Major/minor project management
- Notifications and communication
- Absence reporting for viva/submission

## Finalized Stack
- Frontend: HTML, CSS, Vanilla JS
- Backend: Node.js + Express
- Realtime: Socket.IO
- Auth: Session-based (`express-session`)
- Database: MySQL/MariaDB

## Current Codebase Status
Implemented modules:
- Auth: register/login/logout/me
- Projects: student-only submission, list all, list mine, get project by id, search, deadline-scoped listing
- Project members: add/list/remove APIs with Socket.IO realtime update event
- Notifications: create + fetch + realtime broadcast
- Absence: submit + teacher/admin approve/reject + role-based listing
- Deadlines: teacher/admin can create deadlines; students submit under open deadlines
- Dashboard: system stats (projects/users/roles/pending absences/open deadlines)
- Uploads: project file upload endpoint (Multer)
- Users API: teacher/admin user listing for maintenance/member assignment
- Role-aware frontend behavior: page access redirect + feature visibility rules
- UI system: MS Office 2013/2016-inspired flat design with role-based theming
- RBAC hardening: route-level role middleware + project ownership checks for reads/uploads
- Role hierarchy UX: student (minimal), teacher (operational KPIs), admin (governance KPIs)
- QoL UX: dark mode toggle, persistent theme preference, and mobile-first responsive behavior

Frontend pages present:
- `public/pages/login.html`
- `public/pages/dashboard.html`
- `public/pages/student-dashboard.html`
- `public/pages/teacher-dashboard.html`
- `public/pages/admin-dashboard.html`
- `public/pages/project.html`
- `public/pages/notifications.html`
- `public/pages/absence.html`

## Setup/Support Files Added
- `database-schema.sql`  
  Creates required tables and includes seed users.
- `SETUP.md`  
  Full setup guide (NixOS + DB + run instructions).
- `QUICKSTART.txt`  
  Fast startup/reference guide.

## Important Note on Default Credentials
Default users are defined in `database-schema.sql` **only after importing schema**:
- `admin@example.com / admin123`
- `teacher@example.com / teacher123`
- `student@example.com / student123`

If schema is not imported yet, these users do not exist in DB.

## How to Continue on Any Machine
1. Clone/copy project.
2. Install Node + MySQL/MariaDB.
3. Create `.env` from `.env.example` (or use current values).
4. Run DB setup:
   - create DB/user
   - import `database-schema.sql`
5. Install deps: `npm install`
6. Run app: `npm start`
7. Open: `http://localhost:3000`

## Pending Work (Next Execution Steps)
1. Add explicit HOD role or configurable authority scope for teacher/HOD split.
2. Add deadline close/reopen controls and archival behavior.
3. Add safer FK/index migration handling for legacy local databases.
4. Add advanced filters/search UX polish and feedback states.
5. Add API-level tests or smoke script for role flows.

## Handoff Notes for Other Agents
- Use this file as project state snapshot.
- Check `SETUP.md` for environment/bootstrap.
- Check `database-schema.sql` for canonical DB structure.
- Start implementation from “Pending Work” list above.

## Change Log
- 2026-03-22T21:57:20Z | major | Added global dark mode toggle for all users with persisted preference (`localStorage`) and automatic theme application. | files: `public/js/main.js`, `public/css/styles.css`
- 2026-03-22T21:57:20Z | major | Added responsive/mobile optimization: viewport meta tags on all pages, improved nav/button/list behavior across breakpoints, and small-screen layout fixes. | files: `public/css/styles.css`, `public/pages/*.html`
- 2026-03-22T21:38:07Z | major | Hardened RBAC across routes with reusable role middleware; blocked unauthorized role actions and added project-level access checks for project reads/uploads. | files: `server/middleware/roleMiddleware.js`, `server/routes/authRoutes.js`, `server/routes/projectRoutes.js`, `server/routes/absenceRoutes.js`, `server/routes/notificationRoutes.js`, `server/routes/dashboardRoutes.js`, `server/routes/userRoutes.js`, `server/routes/deadlineRoutes.js`, `server/routes/uploadRoutes.js`, `server/controllers/projectController.js`, `server/controllers/authController.js`
- 2026-03-22T21:38:07Z | major | Refined role hierarchy in dashboards with clear functional tiers (student < teacher < admin) and KPI cards for teacher/admin. | files: `public/pages/student-dashboard.html`, `public/pages/teacher-dashboard.html`, `public/pages/admin-dashboard.html`, `public/js/main.js`
- 2026-03-22T21:38:07Z | minor | Removed extra explanatory text from operational pages for cleaner task-first UX. | files: `public/pages/project.html`, `public/pages/notifications.html`, `public/pages/absence.html`
- 2026-03-22T21:03:35Z | major | Fixed absence visibility issues on legacy DBs by adding runtime schema migrations/fallback queries; student requests now appear for teacher/admin and student sees updated decision status. | files: `server/config/db.js`, `server/models/absenceModel.js`, `public/js/main.js`
- 2026-03-22T21:03:35Z | minor | Hid student project submission panel for teacher/admin and added explicit policy messaging. | files: `public/pages/project.html`, `public/js/main.js`
- 2026-03-22T21:03:35Z | minor | Fixed admin "Absence Queue" action to render absence list in dashboard output panel. | files: `public/js/main.js`
- 2026-03-22T20:36:06Z | major | Added submission-deadline workflow: teacher/admin create deadlines, students submit projects under deadlines, and project lists can be filtered by deadline for member management. | files: `server/models/deadlineModel.js`, `server/controllers/deadlineController.js`, `server/routes/deadlineRoutes.js`, `server/models/projectModel.js`, `server/controllers/projectController.js`, `server/routes/projectRoutes.js`, `server/app.js`, `public/pages/project.html`, `public/js/main.js`
- 2026-03-22T20:36:06Z | major | Added absence review actions for teacher/admin (approve/reject) and surfaced reviewer metadata in UI/API. | files: `server/models/absenceModel.js`, `server/controllers/absenceController.js`, `server/routes/absenceRoutes.js`, `public/pages/absence.html`, `public/js/main.js`
- 2026-03-22T20:36:06Z | minor | Refined admin portal actions for governance (deadlines + absence queue + expanded stats). | files: `public/pages/admin-dashboard.html`, `server/models/dashboardModel.js`, `public/js/main.js`
- 2026-03-22T20:36:06Z | minor | Updated DB schema for submission deadlines and absence reviewer tracking. | files: `database-schema.sql`
- 2026-03-22T19:59:15Z | major | Redesigned UI/UX to Office-style flat interface with role-specific visual themes (student/teacher/admin). | files: `public/css/styles.css`, `public/pages/student-dashboard.html`, `public/pages/teacher-dashboard.html`, `public/pages/admin-dashboard.html`, `public/js/main.js`
- 2026-03-22T19:59:15Z | minor | Refactored shared pages (project/notifications/absence/login) into panel-based flat layout for consistency. | files: `public/pages/project.html`, `public/pages/notifications.html`, `public/pages/absence.html`, `public/pages/login.html`
- 2026-03-22T19:40:09Z | major | Completed Step-2: added project member add/remove APIs, realtime member updates, and member-management UI for teacher/admin. | files: `server/models/projectModel.js`, `server/controllers/projectController.js`, `server/routes/projectRoutes.js`, `public/pages/project.html`, `public/js/main.js`
- 2026-03-22T19:40:09Z | major | Added separate role interfaces and role-based dashboard routing (`student`, `teacher`, `admin`). | files: `public/pages/student-dashboard.html`, `public/pages/teacher-dashboard.html`, `public/pages/admin-dashboard.html`, `public/pages/dashboard.html`, `public/js/main.js`
- 2026-03-22T19:40:09Z | minor | Added user listing API for admin/teacher maintenance operations. | files: `server/models/userModel.js`, `server/controllers/userController.js`, `server/routes/userRoutes.js`, `server/app.js`
- 2026-03-22T19:40:09Z | minor | Updated styling for role dashboards and member management controls. | files: `public/css/styles.css`, `public/pages/notifications.html`, `public/pages/absence.html`
- 2026-03-22T19:11:03Z | minor | Enabled persistent auto-update policy for this progress tracker. | files: `progress.md`
- 2026-03-22T19:08:27Z | major | Created project progress tracker for cross-machine and cross-agent handoff. | files: `progress.md`
- 2026-03-22T18:19:54Z | major | Added DB schema with core tables and seeded default users. | files: `database-schema.sql`
- 2026-03-22T18:19:54Z | major | Added full setup documentation for NixOS/MySQL + app run flow. | files: `SETUP.md`
- 2026-03-22T18:19:54Z | minor | Added quickstart cheat sheet and ensured `uploads/` directory exists. | files: `QUICKSTART.txt`, `uploads/`
