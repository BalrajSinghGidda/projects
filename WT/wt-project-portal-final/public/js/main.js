const API = "/api";
let currentProjectId = null;

document.addEventListener("DOMContentLoaded", () => {
  const path = window.location.pathname;
  if (!path.includes("login.html")) {
    fetch(`${API}/auth/me`)
      .then(res => {
        if (res.status === 401) window.location.href = "/pages/login.html";
      })
      .catch(console.error);
  }

  // Page-specific loads
  if (path.includes("notifications.html")) loadNotifications();
  if (path.includes("absence.html")) loadAbsences();
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
      window.location = "/pages/dashboard.html";
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

  try {
    const res = await fetch(`${API}/projects/create`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ title, description, type, members: [] })
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
      document.getElementById("msg").innerText += " You can now upload a file.";
    }
  } catch (err) {
    console.error(err);
    if (document.getElementById("msg")) {
        document.getElementById("msg").innerText = "Error creating project.";
    }
  }
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
      output.innerHTML = data.map(p => `
        <div class="item">
          <strong>${p.title}</strong> (${p.type})
        </div>
      `).join("");
    }
  } catch (err) {
    console.error(err);
    if (document.getElementById("output")) {
      document.getElementById("output").innerText = "Error loading projects.";
    }
  }
}

// 📊 LOAD ALL PROJECTS
async function loadAllProjects() {
  try {
    const res = await fetch(`${API}/projects/all`, { credentials: "include" });
    if (!res.ok) throw new Error("Failed to fetch");
    const data = await res.json();

    const output = document.getElementById("output");
    if (output) {
      output.innerHTML = data.map(p => `
        <div class="item">
          <strong>${p.title}</strong> - ${p.creator}
        </div>
      `).join("");
    }
  } catch (err) {
    console.error(err);
    if (document.getElementById("output")) {
      document.getElementById("output").innerText = "Error loading projects.";
    }
  }
}

// 🔔 SEND NOTIFICATION
async function sendNotification() {
  const title = document.getElementById("ntitle").value;
  const message = document.getElementById("nmsg").value;

  const res = await fetch(`${API}/notifications/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ title, message })
  });

  if (res.ok) {
    alert("Notification sent!");
    loadNotifications();
  }
}

// 🔔 LOAD NOTIFICATIONS
async function loadNotifications() {
  try {
    const res = await fetch(`${API}/notifications/all`, { credentials: "include" });
    const data = await res.json();
    const container = document.getElementById("notifications-list");
    if (container) {
      container.innerHTML = data.map(n => `
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

// 🔔 SOCKET LISTENER
if (typeof io !== "undefined") {
  const socket = io();

  socket.on("new_notification", (data) => {
    if (!window.location.pathname.includes("notifications.html")) {
      alert(`🔔 ${data.title}\n${data.message}`);
    } else {
      loadNotifications();
    }
  });
}

// 🚫 ABSENCE
async function submitAbsence() {
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
    const container = document.getElementById("absences-list");
    if (container) {
      container.innerHTML = data.map(a => `
        <div class="item">
          <strong>${a.name}</strong> - ${a.reason} (${a.date}) - <em>${a.status}</em>
        </div>
      `).join("");
    }
  } catch (err) {
    console.error(err);
  }
}
