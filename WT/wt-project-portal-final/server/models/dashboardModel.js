
const db=require('../config/db');
exports.getStats=(callback)=>{
 db.query(`
   SELECT
     (SELECT COUNT(*) FROM projects) as total_projects,
     (SELECT COUNT(*) FROM users) as total_users,
     (SELECT COUNT(*) FROM users WHERE role='student') as total_students,
     (SELECT COUNT(*) FROM users WHERE role='teacher') as total_teachers,
     (SELECT COUNT(*) FROM users WHERE role='admin') as total_admins,
     (SELECT COUNT(*) FROM projects WHERE type='major') as major_count,
     (SELECT COUNT(*) FROM projects WHERE type='minor') as minor_count,
     (SELECT COUNT(*) FROM absence_requests WHERE status='pending') as pending_absences,
     (SELECT COUNT(*) FROM submission_deadlines WHERE status='open') as open_deadlines
 `,callback);
};
