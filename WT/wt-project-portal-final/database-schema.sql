-- NexusEdu Database Schema
-- Run this to create all required tables

CREATE DATABASE IF NOT EXISTS wt_portal;
USE wt_portal;

-- Users table
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  role ENUM('student', 'teacher', 'admin') DEFAULT 'student',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User removal requests (teacher submits, admin approves/rejects)
CREATE TABLE IF NOT EXISTS user_removal_requests (
  id INT AUTO_INCREMENT PRIMARY KEY,
  target_user_id INT NOT NULL,
  requested_by INT NOT NULL,
  reason TEXT,
  status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
  reviewed_by INT NULL,
  reviewed_at TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (target_user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (requested_by) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Teacher requested student password changes (admin approval required)
CREATE TABLE IF NOT EXISTS user_password_change_requests (
  id INT AUTO_INCREMENT PRIMARY KEY,
  target_user_id INT NOT NULL,
  requested_by INT NOT NULL,
  new_password_hash VARCHAR(255) NOT NULL,
  status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
  reviewed_by INT NULL,
  reviewed_at TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (target_user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (requested_by) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Submission deadlines table (teacher/admin managed)
CREATE TABLE IF NOT EXISTS submission_deadlines (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  type ENUM('major', 'minor') NOT NULL,
  due_date DATETIME NOT NULL,
  description TEXT,
  status ENUM('open', 'closed') DEFAULT 'open',
  created_by INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT
);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  description TEXT,
  type VARCHAR(50),
  created_by INT,
  deadline_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (deadline_id) REFERENCES submission_deadlines(id) ON DELETE SET NULL
);

-- Project members junction table
CREATE TABLE IF NOT EXISTS project_members (
  id INT AUTO_INCREMENT PRIMARY KEY,
  project_id INT NOT NULL,
  user_id INT NOT NULL,
  joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE KEY unique_member (project_id, user_id)
);

-- Absence requests table
CREATE TABLE IF NOT EXISTS absence_requests (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  reason TEXT NOT NULL,
  date DATE NOT NULL,
  status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
  reviewed_by INT NULL,
  reviewed_at TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  message TEXT,
  sent_by INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (sent_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Insert default users with hashed passwords
-- Admin User
-- Email: admin@example.com | Password: admin123
INSERT INTO users (name, email, password, role) VALUES
('Admin User', 'admin@example.com', '$2b$10$cHU2OL7sTlpwLsaebnzC8.vPCYpze15827OwN2VKHR0C6BTl5MC26', 'admin')
ON DUPLICATE KEY UPDATE email=email;

-- Student User
-- Email: student@example.com | Password: student123
INSERT INTO users (name, email, password, role) VALUES
('Student User', 'student@example.com', '$2b$10$trMUxuGtjAAl15gbsnQgcuwzv06sDHWuf0yadXr5FZ.d0j1bUQhsK', 'student')
ON DUPLICATE KEY UPDATE email=email;

-- Teacher User
-- Email: teacher@example.com | Password: teacher123
INSERT INTO users (name, email, password, role) VALUES
('Teacher User', 'teacher@example.com', '$2b$10$ocReu6zAJmmbQlmGMpOR0.Vly6vsI0uMsj83TAivjRQPIwgNmERNG', 'teacher')
ON DUPLICATE KEY UPDATE email=email;
