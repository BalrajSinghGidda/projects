document.addEventListener('DOMContentLoaded', async () => {
    // Initialize Materialize components
    M.AutoInit();

    const mainContent = document.getElementById('main-content');
    const navLinks = document.getElementById('nav-links');
    const mobileNav = document.getElementById('mobile-nav');

    const response = await fetch('/api/me');
    if (response.status === 401) {
        window.location.href = '/login';
        return;
    }
    const user = await response.json();
    const role = user.role;

    const routes = {
        student: [
            { path: '/student-home', name: 'Home' },
            { path: '/projects', name: 'Projects' },
            { path: '/announcements', name: 'Announcements' },
            { path: '/submit', name: 'Submit Project' },
            { path: '/absence', name: 'Report Absence' }
        ],
        teacher: [
            { path: '/teacher-home', name: 'Home' },
            { path: '/projects', name: 'Projects' },
            { path: '/announcements', name: 'Announcements' },
            { path: '/schedule-viva', name: 'Schedule Viva' },
            { path: '/create-assignment', name: 'Create Assignment' },
            { path: '/register-student', name: 'Register Student' }
        ],
        admin: [
            { path: '/admin-home', name: 'Home' },
            { path: '/projects', name: 'Projects' },
            { path: '/announcements', name: 'Announcements' },
            { path: '/schedule-viva', name: 'Schedule Viva' },
            { path: '/create-assignment', name: 'Create Assignment' },
            { path: '/register-teacher', name: 'Register Teacher' },
            { path: '/register-student', name: 'Register Student' }
        ]
    };

    const loadNav = () => {
        const links = routes[role];
        if (!links) return;
        
        let navHtml = '';
        links.forEach(link => {
            navHtml += `<li><a href="${link.path}">${link.name}</a></li>`;
        });
        navHtml += `<li><a href="/api/logout">Logout</a></li>`;

        navLinks.innerHTML = navHtml;
        mobileNav.innerHTML = navHtml;
    };

    const loadContent = async (path) => {
        if (path === '/') {
            path = `/${role}-home`;
        }
        try {
            const response = await fetch(`${path}.html`);
            mainContent.innerHTML = await response.text();
            M.AutoInit(); // Re-initialize Materialize components
            
            if (path === '/projects') {
                fetchProjects();
            } else if (path === '/announcements') {
                fetchAnnouncements();
            }

            attachEventListeners();
        } catch (error) {
            mainContent.innerHTML = '<p>Page not found.</p>';
        }
    };

    const fetchProjects = async () => {
        const projectList = document.getElementById('project-list');
        const response = await fetch('/api/projects');
        const { projects } = await response.json();
        let projectsHtml = '';
        projects.forEach(project => {
            projectsHtml += `
                <div class="card">
                    <div class="card-content">
                        <span class="card-title">${project.title}</span>
                        <p>
                            <a href="${project.link}" target="_blank">${project.link}</a>
                        </p>
                        ${project.file_path ? `<p><a href="/${project.file_path}">Download File</a></p>` : ''}
                    </div>
                </div>
            `;
        });
        projectList.innerHTML = projectsHtml;
    };

    const fetchAnnouncements = async () => {
        const announcementList = document.getElementById('announcement-list');
        const response = await fetch('/api/announcements');
        const { announcements } = await response.json();
        let announcementsHtml = '';
        announcements.forEach(announcement => {
            announcementsHtml += `
                <div class="card">
                    <div class="card-content">
                        <p>${announcement.content}</p>
                    </div>
                </div>
            `;
        });
        announcementList.innerHTML = announcementsHtml;
    };
    
    const attachEventListeners = async () => {
        const createAssignmentForm = document.getElementById('create-assignment-form');
        if (createAssignmentForm) {
            createAssignmentForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const title = document.getElementById('assignment-title').value;
                const description = document.getElementById('assignment-description').value;
                await fetch('/api/assignments', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, description }),
                });
                alert('Assignment created successfully.');
                createAssignmentForm.reset();
            });
        }

        const projectForm = document.getElementById('project-form');
        if (projectForm) {
            const assignmentSelect = document.getElementById('assignment-select');
            const response = await fetch('/api/assignments');
            const { assignments } = await response.json();
            assignments.forEach(assignment => {
                const option = document.createElement('option');
                option.value = assignment.id;
                option.textContent = assignment.title;
                assignmentSelect.appendChild(option);
            });
            M.FormSelect.init(assignmentSelect);

            projectForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(projectForm);
                await fetch('/api/projects', {
                    method: 'POST',
                    body: formData
                });
                window.location.hash = '/projects';
            });
        }
        
        const absenceForm = document.getElementById('absence-form');
        if (absenceForm) {
            const vivaSelect = document.getElementById('viva-select');
            const response = await fetch('/api/vivas');
            const { vivas } = await response.json();
            vivas.forEach(viva => {
                const option = document.createElement('option');
                option.value = viva.id;
                option.textContent = `Project ${viva.project_id} - ${viva.viva_date}`;
                vivaSelect.appendChild(option);
            });
            M.FormSelect.init(vivaSelect);

            absenceForm.addEventListener('submit', async(e) => {
                e.preventDefault();
                const vivaId = vivaSelect.value;
                const reason = document.getElementById('absence-reason').value;
                await fetch('/api/absences', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ reason, viva_id: vivaId }),
                });
                alert('Absence reported.');
                absenceForm.reset();
            });
        }

        const scheduleVivaForm = document.getElementById('schedule-viva-form');
        if (scheduleVivaForm) {
            const projectSelect = document.getElementById('project-select');
            const response = await fetch('/api/projects');
            const { projects } = await response.json();
            projects.forEach(project => {
                const option = document.createElement('option');
                option.value = project.id;
                option.textContent = project.title;
                projectSelect.appendChild(option);
            });
            M.FormSelect.init(projectSelect);

            scheduleVivaForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const projectId = projectSelect.value;
                const vivaDate = document.getElementById('viva-date').value;
                await fetch('/api/vivas', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ project_id: projectId, viva_date: vivaDate })
                });
                alert('Viva scheduled successfully.');
                scheduleVivaForm.reset();
            });
        }

        const registerTeacherForm = document.getElementById('register-teacher-form');
        if (registerTeacherForm) {
            registerTeacherForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const username = document.getElementById('teacher-username').value;
                const password = document.getElementById('teacher-password').value;
                await registerUser(username, password, 'teacher');
                registerTeacherForm.reset();
            });
        }

        const registerStudentForm = document.getElementById('register-student-form');
        if (registerStudentForm) {
            registerStudentForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const username = document.getElementById('student-username').value;
                const password = document.getElementById('student-password').value;
                await registerUser(username, password, 'student');
                registerStudentForm.reset();
            });
        }
    };

    const registerUser = async (username, password, role) => {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, role }),
        });
        if (response.ok) {
            alert(`User ${username} registered successfully as a ${role}.`);
        } else {
            alert('Registration failed.');
        }
    };

    window.addEventListener('popstate', () => {
        loadContent(window.location.pathname);
    });

    document.body.addEventListener('click', e => {
        if (e.target.matches('a')) {
            const path = e.target.getAttribute('href');
            if (path.startsWith('/')) {
                if (path === '/api/logout') {
                    return; // Let the browser handle the navigation
                }
                e.preventDefault();
                history.pushState(null, '', path);
                loadContent(path);
            }
        }
    });

    loadNav();
    loadContent(window.location.pathname);
});
