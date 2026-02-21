
const db=require('../config/db');
exports.getStats=(callback)=>{
 db.query('SELECT COUNT(*) as total, SUM(type="major") as major_count, SUM(type="minor") as minor_count FROM projects',callback);
};
