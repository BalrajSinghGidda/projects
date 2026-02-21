
const dashboard=require('../models/dashboardModel');
exports.stats=(req,res)=>{
 dashboard.getStats((err,results)=>{
  if(err) return res.status(500).json({error:err});
  res.json(results[0]);
 });
};
