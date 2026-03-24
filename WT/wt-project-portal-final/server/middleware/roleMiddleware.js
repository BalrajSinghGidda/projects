module.exports = function roleMiddleware(allowedRoles) {
  return function (req, res, next) {
    if (!req.session || !req.session.user) {
      return res.status(401).json({ message: "Unauthorized" });
    }

    if (!allowedRoles.includes(req.session.user.role)) {
      return res.status(403).json({ message: "Access denied" });
    }

    next();
  };
};
