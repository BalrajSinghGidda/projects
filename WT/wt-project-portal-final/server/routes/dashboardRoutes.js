
const express=require('express');
const router=express.Router();
const auth=require('../middleware/authMiddleware');
const role = require("../middleware/roleMiddleware");
const controller=require('../controllers/dashboardController');

router.get('/stats',auth, role(["teacher", "admin"]), controller.stats);

module.exports=router;
