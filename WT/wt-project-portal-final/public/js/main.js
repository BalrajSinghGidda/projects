const API = "/api";
const ROLE_DASHBOARD = {
  student: "/pages/student-dashboard.html",
  teacher: "/pages/teacher-dashboard.html",
  admin: "/pages/admin-dashboard.html"
};
const THEME_STORAGE_KEY = "wt-portal-theme";

let currentProjectId = null;
let currentUser = null;
let socket = null;

function resolveTheme() {
  const saved = localStorage.getItem(THEME_STORAGE_KEY);
  if (saved === "dark" || saved === "light") {
    return saved;
  }
  return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function applyTheme(theme) {
  const isDark = theme === "dark";
  document.body.classList.toggle("theme-dark", isDark);
  document.querySelectorAll(".theme-toggle-btn").forEach((btn) => {
    btn.innerText = isDark ? "Light mode" : "Dark mode";
  });
}

function toggleTheme() {
  const nextTheme = document.body.classList.contains("theme-dark") ? "light" : "dark";
  localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
  applyTheme(nextTheme);
}

function ensureThemeToggle() {
  if (document.querySelector(".theme-toggle-btn")) {
    return;
  }

  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "secondary theme-toggle-btn";
  btn.addEventListener("click", toggleTheme);

  const nav = document.querySelector("nav");
  if (nav) {
    nav.appendChild(btn);
  } else {
    btn.classList.add("floating-theme-toggle");
    document.body.appendChild(btn);
  }
}

function dashboardPathByRole(role) {
  return ROLE_DASHBOARD[role] || ROLE_DASHBOARD.student;
}

function isTeacherOrAdmin() {
  return !!currentUser && (currentUser.role === "teacher" || currentUser.role === "admin");
}

function patchDashboardNavLinks() {
  if (!currentUser) return;
  const links = document.querySelectorAll('nav a[href="/pages/dashboard.html"]');
  links.forEach((link) => {
    link.setAttribute("href", dashboardPathByRole(currentUser.role));
  });
}

function applyRoleTheme() {
  if (!currentUser) return;

  document.body.classList.remove("role-student", "role-teacher", "role-admin");
  document.body.classList.add(`role-${currentUser.role}`);

  const nav = document.querySelector("nav");
  if (!nav) return;

  if (!nav.querySelector(".role-badge")) {
    const badge = document.createElement("span");
    badge.className = "role-badge";
    badge.textContent = `${String(currentUser.role || "student").toUpperCase()} PORTAL`;
    nav.insertBefore(badge, nav.querySelector("button"));
  }
}

function setActiveNavLink(page) {
  const links = document.querySelectorAll("nav a");
  links.forEach((link) => link.classList.remove("active"));
  links.forEach((link) => {
    if (link.getAttribute("href") && link.getAttribute("href").includes(page)) {
      link.classList.add("active");
    }
  });
}

function applyRolePageRules(page) {
  if (page === "project.html") {
    const memberSection = document.getElementById("member-management-section");
    const deadlineManagement = document.getElementById("deadline-management-section");
    const submitPanel = document.getElementById("project-submit-section");
    const policyMsg = document.getElementById("project-policy-msg");
    if (!isTeacherOrAdmin()) {
      if (memberSection) memberSection.style.display = "none";
      if (deadlineManagement) deadlineManagement.style.display = "none";
      if (policyMsg) policyMsg.innerText = "Student submission portal: select an active deadline and submit.";
    } else if (currentUser.role === "teacher" || currentUser.role === "admin") {
      if (submitPanel) {
        submitPanel.style.display = "none";
      }
      const msg = document.getElementById("msg");
      if (msg) {
        msg.innerText = "Teachers/Admin cannot submit projects. Students submit under deadlines.";
      }
      if (policyMsg) {
        policyMsg.innerText = "Submission is student-only. Use deadline + member management sections below.";
      }
    }
  }

  if (page === "notifications.html" && !isTeacherOrAdmin()) {
    const form = document.getElementById("notification-form");
    if (form) {
      form.style.display = "none";
    }
  }

  if (page === "absence.html") {
    const review = document.getElementById("absence-review-section");
    const submit = document.getElementById("absence-submit-section");
    if (review && !isTeacherOrAdmin()) {
      review.style.display = "none";
    }
    if (submit && isTeacherOrAdmin()) {
      submit.style.display = "none";
    }
  }
}

function initSocket() {
  if (typeof io === "undefined" || socket) {
    return;
  }

  socket = io();
  socket.on("new_notification", (data) => {
    const onNotificationsPage = window.location.pathname.includes("notifications.html");
    if (!onNotificationsPage) {
      alert(`🔔 ${data.title}\n${data.message}`);
    } else {
      loadNotifications();
    }
  });

  socket.on("project_members_updated", (payload) => {
    const projectInput = document.getElementById("member-project-id");
    const projectId = projectInput ? Number(projectInput.value) : null;
    if (window.location.pathname.includes("project.html") && projectId && projectId === Number(payload.projectId)) {
      renderProjectMembers(payload.members, projectId);
      const msg = document.getElementById("member-msg");
      if (msg) msg.innerText = "Members updated in realtime.";
    }
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  const path = window.location.pathname;
  const page = path.split("/").pop();
  const initialTheme = resolveTheme();

  applyTheme(initialTheme);
  ensureThemeToggle();
  applyTheme(initialTheme);

  if (page !== "login.html") {
    try {
      const meRes = await fetch(`${API}/auth/me`, { credentials: "include" });
      if (meRes.status === 401) {
        window.location.href = "/pages/login.html";
        return;
      }

      currentUser = await meRes.json();
      const roleDashboardPath = dashboardPathByRole(currentUser.role);

      if (page === "dashboard.html") {
        window.location.href = roleDashboardPath;
        return;
      }

      const rolePages = ["student-dashboard.html", "teacher-dashboard.html", "admin-dashboard.html"];
      if (rolePages.includes(page) && path !== roleDashboardPath) {
        window.location.href = roleDashboardPath;
        return;
      }

      patchDashboardNavLinks();
      applyRoleTheme();
      setActiveNavLink(page);
      applyRolePageRules(page);
    } catch (error) {
      console.error("Auth check failed:", error);
    }
  }

  initSocket();

  if (page === "notifications.html") loadNotifications();
  if (page === "absence.html") loadAbsences();
  if (page === "teacher-dashboard.html" || page === "admin-dashboard.html") {
    loadDashboardStats();
  }
  if (page === "project.html") {
    loadDeadlines();
    if (isTeacherOrAdmin()) {
      loadAllUsersForMemberSelect();
      loadDeadlinesForMemberFilters();
    }
  }
});

// 🔐 LOGIN
async function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  try {
    const res = await fetch(`${API}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();
    if (document.getElementById("msg")) {
      document.getElementById("msg").innerText = data.message;
    }

    if (res.ok) {
      window.location = dashboardPathByRole(data.user.role);
    }
  } catch (error) {
    console.error("Login error:", error);
  }
}

// 🚪 LOGOUT
async function logout() {
  await fetch(`${API}/auth/logout`, { credentials: "include" });
  window.location.href = "/pages/login.html";
}

// 📁 CREATE PROJECT
async function createProject() {
  const title = document.getElementById("title").value;
  const description = document.getElementById("description").value;
  const type = document.getElementById("type").value;
  const deadlineId = Number(document.getElementById("deadline-select").value);

  if (currentUser && currentUser.role !== "student") {
    const msg = document.getElementById("msg");
    if (msg) msg.innerText = "Only students can submit projects.";
    return;
  }

  try {
    const res = await fetch(`${API}/projects/create`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ title, description, type, deadlineId, members: [] })
    });

    const data = await res.json();
    if (document.getElementById("msg")) {
      document.getElementById("msg").innerText = data.message;
    }

    if (res.ok && data.projectId) {
      currentProjectId = data.projectId;
      const uploadSection = document.getElementById("upload-section");
      if (uploadSection) {
        uploadSection.style.display = "block";
      }
      document.getElementById("msg").innerText += ` Project ID: ${data.projectId}.`;
    }
  } catch (err) {
    console.error(err);
    if (document.getElementById("msg")) {
      document.getElementById("msg").innerText = "Error creating project.";
    }
  }
}

async function createDeadline() {
  if (!isTeacherOrAdmin()) return;

  const title = document.getElementById("deadline-title").value;
  const type = document.getElementById("deadline-type").value;
  const dueDate = document.getElementById("deadline-date").value;
  const description = document.getElementById("deadline-description").value;
  const msg = document.getElementById("deadline-msg");

  try {
    const res = await fetch(`${API}/deadlines`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ title, type, dueDate, description })
    });
    const data = await res.json();
    if (msg) msg.innerText = data.message || "Deadline request processed";

    if (res.ok) {
      loadDeadlines();
      loadDeadlinesForMemberFilters();
    }
  } catch (err) {
    console.error(err);
    if (msg) msg.innerText = "Failed to create deadline.";
  }
}

async function loadDeadlines() {
  if (!currentUser || (currentUser.role !== "student" && currentUser.role !== "teacher" && currentUser.role !== "admin")) {
    return;
  }

  try {
    const res = await fetch(`${API}/deadlines`, { credentials: "include" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || "Failed to load deadlines");

    const studentSelect = document.getElementById("deadline-select");
    if (studentSelect) {
      const options = [`<option value="">Select submission deadline</option>`];
      data.filter((d) => d.status === "open").forEach((d) => {
        options.push(`<option value="${d.id}">#${d.id} ${d.title} (${d.type}) - ${new Date(d.due_date).toLocaleString()}</option>`);
      });
      studentSelect.innerHTML = options.join("");
    }

    const list = document.getElementById("deadlines-list");
    if (list) {
      list.innerHTML = data.map((d) => `
        <div class="item">
          <strong>#${d.id} ${d.title}</strong> (${d.type})<br>
          Due: ${new Date(d.due_date).toLocaleString()} | Status: <em>${d.status}</em><br>
          Created by: ${d.created_by_name || "N/A"}
        </div>
      `).join("");
    }

    const rendered = data.map((d) => `
      <div class="item">
        <strong>Deadline #${d.id}</strong> - ${d.title} (${d.type})<br>
        ${new Date(d.due_date).toLocaleString()} - ${d.status}
      </div>
    `).join("");
    const output = document.getElementById("output");
    if (output && (window.location.pathname.includes("admin-dashboard.html") || window.location.pathname.includes("teacher-dashboard.html"))) {
      output.innerHTML = rendered || `<div class="item">No deadlines found.</div>`;
    }
  } catch (err) {
    console.error(err);
  }
}

async function loadDeadlinesForMemberFilters() {
  const select = document.getElementById("member-deadline-select");
  if (!select) return;

  try {
    const res = await fetch(`${API}/deadlines`, { credentials: "include" });
    const data = await res.json();
    if (!res.ok) throw new Error("Failed to load deadline filters");

    const options = [`<option value="">Filter projects by deadline</option>`];
    data.forEach((d) => {
      options.push(`<option value="${d.id}">#${d.id} ${d.title} (${d.type})</option>`);
    });
    select.innerHTML = options.join("");
  } catch (err) {
    console.error(err);
  }
}

async function loadProjectsByDeadline() {
  const deadlineId = Number(document.getElementById("member-deadline-select").value);
  const list = document.getElementById("deadline-projects-list");
  if (!deadlineId || !list) return;

  try {
    const res = await fetch(`${API}/projects/deadline/${deadlineId}`, { credentials: "include" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || "Failed to load projects by deadline");

    if (!data.length) {
      list.innerHTML = `<div class="item">No projects submitted under this deadline yet.</div>`;
      return;
    }

    list.innerHTML = data.map((p) => `
      <div class="item item-row">
        <span><strong>#${p.id}</strong> ${p.title} (${p.type}) - by ${p.creator || "Unknown"}</span>
        <button class="secondary" onclick="setProjectForMemberManagement(${p.id})">Use</button>
      </div>
    `).join("");
  } catch (err) {
    console.error(err);
    list.innerHTML = `<div class="item">Failed to load projects.</div>`;
  }
}

function setProjectForMemberManagement(projectId) {
  const input = document.getElementById("member-project-id");
  if (!input) return;
  input.value = String(projectId);
  loadProjectMembers();
}

// 📁 UPLOAD FILE
async function uploadFile() {
  if (!currentProjectId) {
    alert("Please create a project first.");
    return;
  }

  const fileInput = document.getElementById("projectFile");
  if (!fileInput || !fileInput.files.length) {
    alert("Please select a file.");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    const res = await fetch(`${API}/upload/project/${currentProjectId}`, {
      method: "POST",
      body: formData,
      credentials: "include"
    });

    const data = await res.json();
    const msg = document.getElementById("upload-msg");
    if (msg) msg.innerText = data.message;
  } catch (err) {
    console.error(err);
    const msg = document.getElementById("upload-msg");
    if (msg) msg.innerText = "Upload failed.";
  }
}

// 📊 LOAD MY PROJECTS
async function loadMyProjects() {
  try {
    const res = await fetch(`${API}/projects/mine`, { credentials: "include" });
    if (!res.ok) throw new Error("Failed to fetch");
    const data = await res.json();

    const output = document.getElementById("output");
    if (output) {
      output.innerHTML = data.map((p) => `
        <div class="item">
          <strong>#${p.id} ${p.title}</strong> (${p.type})
        </div>
      `).join("");
    }
  } catch (err) {
    console.error(err);
    const output = document.getElementById("output");
    if (output) {
      output.innerText = "Error loading projects.";
    }
  }
}

// 📊 LOAD ALL PROJECTS
async function loadAllProjects() {
  if (!currentUser || (currentUser.role !== "teacher" && currentUser.role !== "admin")) {
    const output = document.getElementById("output");
    if (output) output.innerText = "Access denied";
    return;
  }

  try {
    const res = await fetch(`${API}/projects/all`, { credentials: "include" });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.message || "Failed to fetch all projects");
    }

    const output = document.getElementById("output");
    if (output) {
      output.innerHTML = data.map((p) => `
        <div class="item">
          <strong>#${p.id} ${p.title}</strong> (${p.type}) - ${p.creator || "Unknown"}
        </div>
      `).join("");
    }
  } catch (err) {
    console.error(err);
    const output = document.getElementById("output");
    if (output) {
      output.innerText = `Error loading all projects: ${err.message}`;
    }
  }
}

async function loadDashboardStats() {
  try {
    const res = await fetch(`${API}/dashboard/stats`, { credentials: "include" });
    const data = await res.json();
    if (!res.ok) throw new Error("Failed to load stats");

    const output = document.getElementById("output");
    const teacherTotal = document.getElementById("teacher-kpi-total");
    const teacherPending = document.getElementById("teacher-kpi-pending");
    const teacherDeadlines = document.getElementById("teacher-kpi-deadlines");
    const adminUsers = document.getElementById("admin-kpi-users");
    const adminProjects = document.getElementById("admin-kpi-projects");
    const adminPending = document.getElementById("admin-kpi-pending");
    const adminDeadlines = document.getElementById("admin-kpi-deadlines");

    if (teacherTotal) teacherTotal.innerText = data.total_projects || 0;
    if (teacherPending) teacherPending.innerText = data.pending_absences || 0;
    if (teacherDeadlines) teacherDeadlines.innerText = data.open_deadlines || 0;
    if (adminUsers) adminUsers.innerText = data.total_users || 0;
    if (adminProjects) adminProjects.innerText = data.total_projects || 0;
    if (adminPending) adminPending.innerText = data.pending_absences || 0;
    if (adminDeadlines) adminDeadlines.innerText = data.open_deadlines || 0;

    if (output) {
      output.innerHTML = `
        <div class="item">
          <strong>System Statistics</strong><br>
          Projects: ${data.total_projects || 0}<br>
          Major: ${data.major_count || 0}<br>
          Minor: ${data.minor_count || 0}<br>
          Users: ${data.total_users || 0} (Students: ${data.total_students || 0}, Teachers: ${data.total_teachers || 0}, Admin: ${data.total_admins || 0})<br>
          Pending Absences: ${data.pending_absences || 0}<br>
          Open Deadlines: ${data.open_deadlines || 0}
        </div>
      `;
    }
  } catch (err) {
    console.error(err);
  }
}

async function loadAllUsers() {
  if (!currentUser || currentUser.role !== "admin") {
    const output = document.getElementById("output");
    if (output) output.innerText = "Access denied";
    return;
  }

  try {
    const res = await fetch(`${API}/users`, { credentials: "include" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || "Failed to load users");

    const output = document.getElementById("output");
    if (output) {
      output.innerHTML = data.map((u) => `
        <div class="item">
          <strong>${u.name}</strong> (${u.role})<br>
          ${u.email}
        </div>
      `).join("");
    }
  } catch (err) {
    console.error(err);
    const output = document.getElementById("output");
    if (output) output.innerText = err.message;
  }
}

// 👥 MEMBER MANAGEMENT
async function loadAllUsersForMemberSelect() {
  const select = document.getElementById("member-user-select");
  if (!select) return;

  try {
    const res = await fetch(`${API}/users`, { credentials: "include" });
    const users = await res.json();
    if (!res.ok) throw new Error(users.message || "Failed to fetch users");

    const options = [`<option value="">Select user to add</option>`];
    users.forEach((u) => {
      options.push(`<option value="${u.id}">${u.name} (${u.role}) - ${u.email}</option>`);
    });
    select.innerHTML = options.join("");
  } catch (err) {
    console.error(err);
  }
}

async function addProjectMember() {
  if (!isTeacherOrAdmin()) {
    return;
  }

  const projectId = Number(document.getElementById("member-project-id").value);
  const userId = Number(document.getElementById("member-user-select").value);
  const msg = document.getElementById("member-msg");

  if (!projectId || !userId) {
    if (msg) msg.innerText = "Project ID and user are required.";
    return;
  }

  try {
    const res = await fetch(`${API}/projects/${projectId}/members`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ userId })
    });
    const data = await res.json();
    if (msg) msg.innerText = data.message;

    if (res.ok) {
      renderProjectMembers(data.members, projectId);
    }
  } catch (err) {
    console.error(err);
    if (msg) msg.innerText = "Failed to add member.";
  }
}

async function loadProjectMembers() {
  if (!currentUser) return;

  const projectId = Number(document.getElementById("member-project-id").value);
  const msg = document.getElementById("member-msg");
  if (!projectId) {
    if (msg) msg.innerText = "Enter a valid Project ID.";
    return;
  }

  try {
    const res = await fetch(`${API}/projects/${projectId}/members`, { credentials: "include" });
    const members = await res.json();
    if (!res.ok) throw new Error(members.message || "Failed to load members");
    renderProjectMembers(members, projectId);
    if (msg) msg.innerText = "Members loaded.";
  } catch (err) {
    console.error(err);
    if (msg) msg.innerText = err.message;
  }
}

function renderProjectMembers(members, projectId) {
  const container = document.getElementById("project-members-list");
  if (!container) return;

  if (!members.length) {
    container.innerHTML = `<div class="item">No members yet.</div>`;
    return;
  }

  container.innerHTML = members.map((m) => `
    <div class="item item-row">
      <span><strong>${m.name}</strong> - ${m.email}</span>
      ${isTeacherOrAdmin() ? `<button class="danger" onclick="removeProjectMember(${projectId}, ${m.id})">Remove</button>` : ""}
    </div>
  `).join("");
}

async function removeProjectMember(projectId, userId) {
  if (!isTeacherOrAdmin()) {
    return;
  }

  const msg = document.getElementById("member-msg");
  try {
    const res = await fetch(`${API}/projects/${projectId}/members/${userId}`, {
      method: "DELETE",
      credentials: "include"
    });
    const data = await res.json();
    if (msg) msg.innerText = data.message;
    if (res.ok) renderProjectMembers(data.members, projectId);
  } catch (err) {
    console.error(err);
    if (msg) msg.innerText = "Failed to remove member.";
  }
}

// 🔔 SEND NOTIFICATION
async function sendNotification() {
  if (!isTeacherOrAdmin()) {
    return;
  }

  const title = document.getElementById("ntitle").value;
  const message = document.getElementById("nmsg").value;

  try {
    const res = await fetch(`${API}/notifications/send`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ title, message })
    });
    const data = await res.json();

    if (res.ok) {
      alert("Notification sent!");
      loadNotifications();
    } else {
      alert(data.message || "Failed to send notification.");
    }
  } catch (err) {
    console.error(err);
  }
}

// 🔔 LOAD NOTIFICATIONS
async function loadNotifications() {
  try {
    const res = await fetch(`${API}/notifications/all`, { credentials: "include" });
    const data = await res.json();
    const container = document.getElementById("notifications-list");
    if (container) {
      container.innerHTML = data.map((n) => `
        <div class="item">
          <strong>${n.title}</strong> (from ${n.sender})<br>
          <small>${new Date(n.created_at).toLocaleString()}</small><br>
          ${n.message}
        </div>
      `).join("");
    }
  } catch (err) {
    console.error(err);
  }
}

// 🚫 ABSENCE
async function submitAbsence() {
  if (!currentUser || currentUser.role !== "student") {
    return;
  }

  const reason = document.getElementById("reason").value;
  const date = document.getElementById("date").value;

  const res = await fetch(`${API}/absence/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ reason, date })
  });

  if (res.ok) {
    alert("Absence submitted");
    loadAbsences();
  }
}

// 🚫 LOAD ABSENCES
async function loadAbsences() {
  try {
    const res = await fetch(`${API}/absence/all`, { credentials: "include" });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.message || "Failed to load absence requests");
    }
    const container = document.getElementById("absences-list");
    const output = document.getElementById("output");
    const rendered = data.map((a) => `
      <div class="item">
        <strong>${a.name}</strong> - ${a.reason} (${a.date}) - <em>${a.status}</em>
        ${a.reviewed_by_name ? `<br><small>Reviewed by ${a.reviewed_by_name} at ${new Date(a.reviewed_at).toLocaleString()}</small>` : ""}
        ${!isTeacherOrAdmin() ? `
          <br><small>Your request is currently: <strong>${a.status}</strong></small>
        ` : ""}
        ${isTeacherOrAdmin() && a.status === "pending" ? `
          <div class="actions">
            <button onclick="updateAbsenceStatus(${a.id}, 'approved')">Approve</button>
            <button class="danger" onclick="updateAbsenceStatus(${a.id}, 'rejected')">Reject</button>
          </div>
        ` : ""}
      </div>
    `).join("");

    if (container) {
      container.innerHTML = rendered;
    }

    if (output && window.location.pathname.includes("admin-dashboard.html")) {
      output.innerHTML = rendered || `<div class="item">No absence requests yet.</div>`;
    }
  } catch (err) {
    console.error(err);
    const container = document.getElementById("absences-list");
    const output = document.getElementById("output");
    if (container) {
      container.innerHTML = `<div class="item">Error loading absences: ${err.message}</div>`;
    }
    if (output && window.location.pathname.includes("admin-dashboard.html")) {
      output.innerHTML = `<div class="item">Error loading absence queue: ${err.message}</div>`;
    }
  }
}

async function updateAbsenceStatus(absenceId, status) {
  if (!isTeacherOrAdmin()) {
    return;
  }

  try {
    const res = await fetch(`${API}/absence/${absenceId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ status })
    });
    const data = await res.json();
    if (!res.ok) {
      alert(data.message || "Failed to update status");
      return;
    }
    loadAbsences();
  } catch (err) {
    console.error(err);
  }
}
