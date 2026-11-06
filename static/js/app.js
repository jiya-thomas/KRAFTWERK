/**
 * KRAFTWERK // SWISS PROJECT MANAGEMENT SYSTEM
 * Pure Vanilla JS Application Controller
 */

// Application State
const state = {
  projects: [],
  activeProject: null,
  activeFilter: 'ALL',
  searchQuery: '',
  stats: {},
  currentEditingProject: null,
  currentEditingTask: null
};

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', () => {
  initClock();
  setupEventListeners();
  loadStats();
  loadProjects();
});

function initClock() {
  const clockEl = document.getElementById('zurich-clock');
  function updateTime() {
    const now = new Date();
    // Display in ISO/Swiss clean format
    const str = now.toLocaleTimeString('de-CH', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
    if (clockEl) clockEl.textContent = `ZRH // ${str} UTC+1`;
  }
  updateTime();
  setInterval(updateTime, 1000);
}

// ==================== API HELPERS ====================

async function apiRequest(url, options = {}) {
  try {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || 'Server error occurred');
    }
    return data;
  } catch (err) {
    showToast(err.message, 'error');
    console.error('API Error:', err);
    throw err;
  }
}

// ==================== STATS & PROJECTS ====================

async function loadStats() {
  try {
    const stats = await apiRequest('/api/stats');
    state.stats = stats;
    renderStats();
  } catch (err) {}
}

function renderStats() {
  const s = state.stats;
  document.getElementById('stat-total-projects').textContent = s.total_projects ?? 0;
  document.getElementById('stat-active-projects').textContent = s.active_projects ?? 0;
  document.getElementById('stat-completed-tasks').textContent = s.completed_tasks ?? 0;
  document.getElementById('stat-completion-rate').textContent = `${s.task_completion_rate ?? 0}%`;
  
  const budgetFormatted = new Intl.NumberFormat('de-CH', { style: 'currency', currency: 'CHF', maximumFractionDigits: 0 }).format(s.total_budget || 0);
  document.getElementById('stat-budget-meta').textContent = `COMMITTED: ${budgetFormatted}`;
}

async function loadProjects() {
  try {
    let url = `/api/projects?`;
    if (state.activeFilter !== 'ALL') {
      url += `status=${encodeURIComponent(state.activeFilter)}&`;
    }
    if (state.searchQuery.trim()) {
      url += `search=${encodeURIComponent(state.searchQuery.trim())}&`;
    }
    
    const projects = await apiRequest(url);
    state.projects = projects;
    renderProjectsGrid();
    loadStats();
  } catch (err) {}
}

function renderProjectsGrid() {
  const container = document.getElementById('projects-grid');
  if (!container) return;
  
  if (state.projects.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; border: 2px dashed #0a0a0a; padding: 48px; text-align: center; background: #fafafa;">
        <p class="label-micro" style="margin-bottom: 8px;">SYSTEM NOTICE // NO DATA</p>
        <h3 style="margin-bottom: 16px;">NO PROJECTS FOUND</h3>
        <p style="color: #666; margin-bottom: 24px; font-size: 0.9rem;">There are no projects matching the current filter. Create a new project or seed demonstration data.</p>
        <div style="display: flex; gap: 12px; justify-content: center;">
          <button class="btn btn-primary" onclick="openNewProjectModal()">+ CREATE PROJECT</button>
          <button class="btn" onclick="seedSampleData()">SEED DEMO DATA</button>
        </div>
      </div>
    `;
    return;
  }
  
  container.innerHTML = state.projects.map(p => {
    const statusClass = `badge-${p.status.toLowerCase()}`;
    const priorityClass = `badge-${p.priority.toLowerCase()}`;
    const budgetFmt = new Intl.NumberFormat('de-CH', { style: 'currency', currency: 'CHF', maximumFractionDigits: 0 }).format(p.budget || 0);
    const progressDone = p.progress_pct >= 100;

    return `
      <div class="project-card" data-id="${p.id}">
        <div class="card-top">
          <span class="card-code">${escapeHtml(p.code)}</span>
          <div style="display: flex; gap: 6px;">
            <span class="badge ${priorityClass}">${escapeHtml(p.priority)}</span>
            <span class="badge ${statusClass}">${escapeHtml(p.status.replace('_', ' '))}</span>
          </div>
        </div>
        <div class="card-body">
          <h3 class="card-title" onclick="openProjectDetail(${p.id})">${escapeHtml(p.name)}</h3>
          <div class="card-client">${escapeHtml(p.client || 'INTERNAL CLIENT')} // ${escapeHtml(p.category)}</div>
          <p class="card-desc">${escapeHtml(p.description || 'No project description supplied.')}</p>
          
          <div class="progress-container">
            <div class="progress-header">
              <span class="label-micro dark">TASKS: ${p.completed_tasks || 0}/${p.total_tasks || 0}</span>
              <span class="mono" style="font-size: 0.75rem; font-weight: 800;">${p.progress_pct}%</span>
            </div>
            <div class="progress-track">
              <div class="progress-fill ${progressDone ? 'done' : ''}" style="width: ${p.progress_pct}%"></div>
            </div>
          </div>
        </div>
        <div class="card-footer">
          <div class="mono" style="font-size: 0.75rem; font-weight: 700;">
            ${budgetFmt}
          </div>
          <div class="card-actions">
            <button class="btn btn-sm" onclick="openProjectDetail(${p.id})">KANBAN</button>
            <button class="btn btn-sm" onclick="openEditProjectModal(${p.id})">EDIT</button>
            <button class="btn btn-sm btn-danger" onclick="confirmDeleteProject(${p.id}, '${escapeHtml(p.name)}')">DEL</button>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// ==================== PROJECT DETAIL & KANBAN ====================

async function openProjectDetail(projectId) {
  try {
    const project = await apiRequest(`/api/projects/${projectId}`);
    state.activeProject = project;
    
    document.getElementById('overview-view').style.display = 'none';
    document.getElementById('project-detail-view').style.display = 'block';
    
    renderProjectDetailHeader();
    renderKanbanColumns();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } catch (err) {}
}

function closeProjectDetail() {
  state.activeProject = null;
  document.getElementById('project-detail-view').style.display = 'none';
  document.getElementById('overview-view').style.display = 'block';
  loadProjects();
}

function renderProjectDetailHeader() {
  const p = state.activeProject;
  if (!p) return;
  
  const budgetFmt = new Intl.NumberFormat('de-CH', { style: 'currency', currency: 'CHF', maximumFractionDigits: 0 }).format(p.budget || 0);
  const statusClass = `badge-${p.status.toLowerCase()}`;
  
  document.getElementById('detail-code').textContent = p.code;
  document.getElementById('detail-title').textContent = p.name;
  document.getElementById('detail-client').textContent = `${p.client || 'INTERNAL'} // ${p.category}`;
  document.getElementById('detail-description').textContent = p.description || 'No description provided.';
  document.getElementById('detail-status-badge').className = `badge ${statusClass}`;
  document.getElementById('detail-status-badge').textContent = p.status.replace('_', ' ');
  document.getElementById('detail-priority-badge').textContent = p.priority;
  document.getElementById('detail-budget').textContent = budgetFmt;
  document.getElementById('detail-dates').textContent = `${p.start_date || 'N/A'} — ${p.due_date || 'N/A'}`;
}

function renderKanbanColumns() {
  const p = state.activeProject;
  if (!p) return;
  
  const tasks = p.tasks || [];
  const columns = {
    'TODO': document.getElementById('kanban-todo'),
    'IN_PROGRESS': document.getElementById('kanban-inprogress'),
    'REVIEW': document.getElementById('kanban-review'),
    'DONE': document.getElementById('kanban-done')
  };
  
  const counts = { 'TODO': 0, 'IN_PROGRESS': 0, 'REVIEW': 0, 'DONE': 0 };
  
  // Clear columns
  Object.keys(columns).forEach(col => {
    columns[col].innerHTML = '';
  });
  
  tasks.forEach(task => {
    const colKey = task.status in columns ? task.status : 'TODO';
    counts[colKey]++;
    
    const cardEl = document.createElement('div');
    cardEl.className = 'task-card';
    cardEl.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
        <span class="mono" style="font-size: 0.65rem; color: #888;">#T-${task.id}</span>
        <span class="badge badge-${task.priority.toLowerCase()}">${escapeHtml(task.priority)}</span>
      </div>
      <div class="task-card-title">${escapeHtml(task.title)}</div>
      ${task.description ? `<p style="font-size: 0.75rem; color: #555; line-height: 1.3;">${escapeHtml(task.description)}</p>` : ''}
      <div class="task-card-meta">
        <span class="task-assignee">${escapeHtml(task.assignee)}</span>
        <span class="mono" style="font-size: 0.68rem; color: #666;">${task.estimated_hours ? task.estimated_hours + 'h' : ''}</span>
      </div>
      <div class="task-card-actions">
        <div class="task-move-btns">
          ${getMoveButtonsHtml(task.id, task.status)}
        </div>
        <div style="display: flex; gap: 4px;">
          <button class="btn btn-sm" style="padding: 2px 6px; font-size: 0.65rem;" onclick="openEditTaskModal(${task.id})">EDIT</button>
          <button class="btn btn-sm btn-danger" style="padding: 2px 6px; font-size: 0.65rem;" onclick="deleteTask(${task.id})">×</button>
        </div>
      </div>
    `;
    columns[colKey].appendChild(cardEl);
  });
  
  document.getElementById('count-todo').textContent = counts['TODO'];
  document.getElementById('count-inprogress').textContent = counts['IN_PROGRESS'];
  document.getElementById('count-review').textContent = counts['REVIEW'];
  document.getElementById('count-done').textContent = counts['DONE'];
}

function getMoveButtonsHtml(taskId, currentStatus) {
  const flow = ['TODO', 'IN_PROGRESS', 'REVIEW', 'DONE'];
  const currentIndex = flow.indexOf(currentStatus);
  let html = '';
  
  if (currentIndex > 0) {
    const prevStatus = flow[currentIndex - 1];
    html += `<button class="btn btn-sm" style="padding: 2px 6px; font-size: 0.65rem;" title="Move to ${prevStatus}" onclick="moveTaskStatus(${taskId}, '${prevStatus}')">←</button>`;
  }
  if (currentIndex < flow.length - 1) {
    const nextStatus = flow[currentIndex + 1];
    html += `<button class="btn btn-sm btn-dark" style="padding: 2px 6px; font-size: 0.65rem;" title="Move to ${nextStatus}" onclick="moveTaskStatus(${taskId}, '${nextStatus}')">→</button>`;
  }
  return html;
}

async function moveTaskStatus(taskId, newStatus) {
  try {
    await apiRequest(`/api/tasks/${taskId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status: newStatus })
    });
    showToast(`Task status updated to ${newStatus}`);
    // Reload active project
    if (state.activeProject) {
      openProjectDetail(state.activeProject.id);
    }
  } catch (err) {}
}

// ==================== PROJECT CRUD OPERATIONS ====================

function openNewProjectModal() {
  state.currentEditingProject = null;
  document.getElementById('modal-project-title').textContent = 'NEW PROJECT ARCHITECTURE';
  document.getElementById('form-project').reset();
  document.getElementById('proj-code').value = '';
  document.getElementById('modal-project').classList.add('active');
}

function openEditProjectModal(projectId) {
  const p = state.projects.find(item => item.id === projectId) || state.activeProject;
  if (!p) return;
  
  state.currentEditingProject = p;
  document.getElementById('modal-project-title').textContent = `EDIT PROJECT // ${p.code}`;
  document.getElementById('proj-code').value = p.code || '';
  document.getElementById('proj-name').value = p.name || '';
  document.getElementById('proj-client').value = p.client || '';
  document.getElementById('proj-category').value = p.category || 'ENGINEERING';
  document.getElementById('proj-status').value = p.status || 'PLANNING';
  document.getElementById('proj-priority').value = p.priority || 'MEDIUM';
  document.getElementById('proj-budget').value = p.budget || 0;
  document.getElementById('proj-start-date').value = p.start_date || '';
  document.getElementById('proj-due-date').value = p.due_date || '';
  document.getElementById('proj-description').value = p.description || '';
  
  document.getElementById('modal-project').classList.add('active');
}

async function handleProjectSubmit(e) {
  e.preventDefault();
  const form = document.getElementById('form-project');
  const data = {
    code: document.getElementById('proj-code').value.trim(),
    name: document.getElementById('proj-name').value.trim(),
    client: document.getElementById('proj-client').value.trim(),
    category: document.getElementById('proj-category').value,
    status: document.getElementById('proj-status').value,
    priority: document.getElementById('proj-priority').value,
    budget: parseFloat(document.getElementById('proj-budget').value) || 0,
    start_date: document.getElementById('proj-start-date').value || null,
    due_date: document.getElementById('proj-due-date').value || null,
    description: document.getElementById('proj-description').value.trim()
  };
  
  if (!data.name) {
    showToast('Project title is required', 'error');
    return;
  }
  
  try {
    if (state.currentEditingProject) {
      await apiRequest(`/api/projects/${state.currentEditingProject.id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
      });
      showToast(`Project ${data.code || ''} updated successfully`);
    } else {
      await apiRequest('/api/projects', {
        method: 'POST',
        body: JSON.stringify(data)
      });
      showToast('New project registered in system');
    }
    
    closeModal('modal-project');
    if (state.activeProject && state.currentEditingProject && state.activeProject.id === state.currentEditingProject.id) {
      openProjectDetail(state.activeProject.id);
    } else {
      loadProjects();
    }
  } catch (err) {}
}

function confirmDeleteProject(projectId, projectName) {
  if (confirm(`CONFIRM DESTRUCTION:\nAre you sure you want to permanently delete project:\n"${projectName}" (ID: ${projectId}) and all associated tasks?`)) {
    deleteProject(projectId);
  }
}

async function deleteProject(projectId) {
  try {
    await apiRequest(`/api/projects/${projectId}`, { method: 'DELETE' });
    showToast(`Project #${projectId} successfully deleted`);
    if (state.activeProject && state.activeProject.id === projectId) {
      closeProjectDetail();
    } else {
      loadProjects();
    }
  } catch (err) {}
}

// ==================== TASK CRUD OPERATIONS ====================

function openNewTaskModal(defaultStatus = 'TODO') {
  if (!state.activeProject) return;
  state.currentEditingTask = null;
  document.getElementById('modal-task-title').textContent = `NEW TASK // ${state.activeProject.code}`;
  document.getElementById('form-task').reset();
  document.getElementById('task-status').value = defaultStatus;
  document.getElementById('modal-task').classList.add('active');
}

function openEditTaskModal(taskId) {
  if (!state.activeProject || !state.activeProject.tasks) return;
  const task = state.activeProject.tasks.find(t => t.id === taskId);
  if (!task) return;
  
  state.currentEditingTask = task;
  document.getElementById('modal-task-title').textContent = `EDIT TASK #${task.id}`;
  document.getElementById('task-title').value = task.title || '';
  document.getElementById('task-assignee').value = task.assignee || '';
  document.getElementById('task-status').value = task.status || 'TODO';
  document.getElementById('task-priority').value = task.priority || 'MEDIUM';
  document.getElementById('task-hours').value = task.estimated_hours || 0;
  document.getElementById('task-due-date').value = task.due_date || '';
  document.getElementById('task-description').value = task.description || '';
  
  document.getElementById('modal-task').classList.add('active');
}

async function handleTaskSubmit(e) {
  e.preventDefault();
  if (!state.activeProject) return;
  
  const data = {
    project_id: state.activeProject.id,
    title: document.getElementById('task-title').value.trim(),
    assignee: document.getElementById('task-assignee').value.trim(),
    status: document.getElementById('task-status').value,
    priority: document.getElementById('task-priority').value,
    estimated_hours: parseFloat(document.getElementById('task-hours').value) || 0,
    due_date: document.getElementById('task-due-date').value || null,
    description: document.getElementById('task-description').value.trim()
  };
  
  if (!data.title) {
    showToast('Task title is required', 'error');
    return;
  }
  
  try {
    if (state.currentEditingTask) {
      await apiRequest(`/api/tasks/${state.currentEditingTask.id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
      });
      showToast('Task updated');
    } else {
      await apiRequest('/api/tasks', {
        method: 'POST',
        body: JSON.stringify(data)
      });
      showToast('Task appended to project');
    }
    
    closeModal('modal-task');
    openProjectDetail(state.activeProject.id);
  } catch (err) {}
}

async function deleteTask(taskId) {
  if (!confirm(`Delete task #${taskId}?`)) return;
  try {
    await apiRequest(`/api/tasks/${taskId}`, { method: 'DELETE' });
    showToast(`Task #${taskId} removed`);
    if (state.activeProject) {
      openProjectDetail(state.activeProject.id);
    }
  } catch (err) {}
}

// ==================== SEED DATA ====================

async function seedSampleData() {
  try {
    const res = await apiRequest('/api/seed', {
      method: 'POST',
      body: JSON.stringify({ force: true })
    });
    showToast('Demonstration projects seeded!');
    loadProjects();
  } catch (err) {}
}

// ==================== EVENT LISTENERS ====================

function setupEventListeners() {
  // Filter pills
  document.querySelectorAll('.filter-pill').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.filter-pill').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      state.activeFilter = e.target.getAttribute('data-status');
      loadProjects();
    });
  });
  
  // Search input
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    let debounce;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(debounce);
      debounce = setTimeout(() => {
        state.searchQuery = e.target.value;
        loadProjects();
      }, 250);
    });
  }
  
  // Form submissions
  document.getElementById('form-project')?.addEventListener('submit', handleProjectSubmit);
  document.getElementById('form-task')?.addEventListener('submit', handleTaskSubmit);
  
  // Modal background clicks
  document.querySelectorAll('.modal-overlay').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        closeModal(modal.id);
      }
    });
  });
}

function closeModal(modalId) {
  document.getElementById(modalId)?.classList.remove('active');
}

// ==================== UTILS ====================

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  
  const toast = document.createElement('div');
  toast.className = 'toast';
  if (type === 'error') {
    toast.style.boxShadow = '4px 4px 0 #000';
    toast.style.background = '#eb0029';
  }
  toast.textContent = `// ${message}`;
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.2s ease';
    setTimeout(() => toast.remove(), 200);
  }, 3200);
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
