const bcrypt = require("bcrypt");
const User = require("../models/userModel");

// REGISTER
exports.register = async (req, res) => {
  const { name, email, password, role } = req.body;

  if (!name || !email || !password) {
    return res.status(400).json({ message: "Missing fields" });
  }

  if (!req.body) {
    return res.status(400).json({ message: "No data sent" });
  }


  try {
    const hashedPassword = await bcrypt.hash(password, 10);

    User.create(name, email, hashedPassword, role || "student", (err, result) => {
      if (err) {
        if (err.code === "ER_DUP_ENTRY") {
          return res.status(400).json({ message: "Email already exists" });
        }
        return res.status(500).json({ error: err });
      }

      res.json({ message: "User registered successfully 🎉" });
    });

  } catch (err) {
    res.status(500).json({ error: err });
  }
};

// LOGIN
exports.login = (req, res) => {
  const { email, password } = req.body;

  User.findByEmail(email, async (err, results) => {
    if (err) return res.status(500).json({ error: err });

    if (results.length === 0) {
      return res.status(404).json({ message: "User not found" });
    }

    const user = results[0];

    const match = await bcrypt.compare(password, user.password);

    if (!match) {
      return res.status(401).json({ message: "Invalid password" });
    }

    // save session
    req.session.user = {
      id: user.id,
      name: user.name,
      role: user.role
    };

    res.json({ message: "Login successful", user: req.session.user });
  });
};

// LOGOUT
exports.logout = (req, res) => {
  req.session.destroy(() => {
    res.json({ message: "Logged out successfully" });
  });
};

// CURRENT USER
exports.me = (req, res) => {
  if (!req.session.user) {
    return res.status(401).json({ message: "Not logged in" });
  }
  res.json(req.session.user);
};

