module.exports = function (req, res, next) {
  if (!req.session.user || !req.session) {
    return res.status(401).json({ message: "Unauthorized" });
  }
  next();
};

