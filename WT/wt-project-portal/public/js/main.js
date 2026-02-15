const API = "http://localhost:3000/api";

// 🔐 LOGIN
async function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const res = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();
  document.getElementById("msg").innerText = data.message;

  if (res.ok) {
    window.location = "dashboard.html";
  }
}

// 📁 CREATE PROJECT
async function createProject() {
  const title = document.getElementById("title").value;
  const description = document.getElementById("description").value;
  const type = document.getElementById("type").value;

  const res = await fetch(`${API}/projects/create`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ title, description, type, members: [] })
  });

  const data = await res.json();
  document.getElementById("msg").innerText = data.message;
}

// 📊 LOAD MY PROJECTS
async function loadMyProjects() {
  const res = await fetch(`${API}/projects/mine`, { credentials: "include" });
  const data = await res.json();

  document.getElementById("output").innerHTML =
    data.map(p => `<div>${p.title} (${p.type})</div>`).join("");
}

// 📊 LOAD ALL PROJECTS
async function loadAllProjects() {
  const res = await fetch(`${API}/projects/all`, { credentials: "include" });
  const data = await res.json();

  document.getElementById("output").innerHTML =
    data.map(p => `<div>${p.title} - ${p.creator}</div>`).join("");
}

// 🔔 SEND NOTIFICATION
async function sendNotification() {
  const title = document.getElementById("ntitle").value;
  const message = document.getElementById("nmsg").value;

  await fetch(`${API}/notifications/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ title, message })
  });
}

// 🔔 SOCKET LISTENER
if (typeof io !== "undefined") {
  const socket = io();

  socket.on("new_notification", (data) => {
    alert(`🔔 ${data.title}\n${data.message}`);
  });
}

// 🚫 ABSENCE
async function submitAbsence() {
  const reason = document.getElementById("reason").value;
  const date = document.getElementById("date").value;

  await fetch(`${API}/absence/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ reason, date })
  });

  alert("Absence submitted");
}
