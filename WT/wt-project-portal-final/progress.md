# WT Project Portal — Progress Log

Last updated: 2026-03-22

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
- Projects: create, list all, list mine, get project by id, search
- Project members: backend table + model support present
- Notifications: create + fetch + realtime broadcast
- Absence: submit + role-based listing (all for teacher/admin, own for student)
- Dashboard: basic stats (total/major/minor projects)
- Uploads: project file upload endpoint (Multer)

Frontend pages present:
- `public/pages/login.html`
- `public/pages/dashboard.html`
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
1. Step-2: Project member add/remove UI + API wiring with live update.
2. Tight RBAC for each role per route/page action.
3. Teacher/HOD dual visibility flow for new projects.
4. Absence review workflow (`pending/approved/rejected`) UI + endpoints.
5. Polishing: validation, filters, and demo-ready walkthrough.

## Handoff Notes for Other Agents
- Use this file as project state snapshot.
- Check `SETUP.md` for environment/bootstrap.
- Check `database-schema.sql` for canonical DB structure.
- Start implementation from “Pending Work” list above.

## Change Log
- 2026-03-22T19:11:03Z | minor | Enabled persistent auto-update policy for this progress tracker. | files: `progress.md`
- 2026-03-22T19:08:27Z | major | Created project progress tracker for cross-machine and cross-agent handoff. | files: `progress.md`
- 2026-03-22T18:19:54Z | major | Added DB schema with core tables and seeded default users. | files: `database-schema.sql`
- 2026-03-22T18:19:54Z | major | Added full setup documentation for NixOS/MySQL + app run flow. | files: `SETUP.md`
- 2026-03-22T18:19:54Z | minor | Added quickstart cheat sheet and ensured `uploads/` directory exists. | files: `QUICKSTART.txt`, `uploads/`
