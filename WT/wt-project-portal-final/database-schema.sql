-- WT Portal Database Schema
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

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  description TEXT,
  type VARCHAR(50),
  created_by INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
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
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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
