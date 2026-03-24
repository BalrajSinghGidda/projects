
const dashboard=require('../models/dashboardModel');
exports.stats=(req,res)=>{
 if(!req.session || !req.session.user || (req.session.user.role!=="teacher" && req.session.user.role!=="admin")){
  return res.status(403).json({message:"Access denied"});
 }
 dashboard.getStats((err,results)=>{
  if(err) return res.status(500).json({error:err});
  res.json(results[0]);
 });
};
