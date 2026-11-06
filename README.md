# ✚ KRAFTWERK // Swiss Project Management System

> **A minimalist, high-contrast Project Management System crafted in the International Typographic Style (Swiss Style), featuring full CRUD operations, a 4-column Kanban workflow board, real-time metrics, SQLite persistence, and ready-to-run Docker containerization.**

---

## 📐 01 // Swiss UI Style System

This application adheres strictly to the principles of the **International Typographic Style** (pioneered by Josef Müller-Brockmann, Max Bill, and Armin Hofmann):

* **Modular 12-Column Grid Architecture:** Clean structural dividing lines (`1px` and `2px` crisp solid borders) and horizontal baseline rhythm.
* **Objective Grotesque Sans-Serif Typography:** Bold `Inter` / `Helvetica Neue` with tight tracking (`-0.035em`) for display titles, paired with uppercase micro-labels (`letter-spacing: 0.14em`) and monospaced numerical metadata.
* **High-Contrast Palette:**
  * **Porcelain White** (`#ffffff`) & **Studio Off-White** (`#f5f5f7`) foundation
  * **Deep Stark Black** (`#0a0a0a`) typography and primary frames
  * **Official Swiss Red** (`#eb0029`) used with strict purpose for critical status indicators, active states, progress completions, and primary CTAs.
* **Functional Minimalism:** Zero unnecessary drop-shadows or gradients; high-contrast invert hover states and sharp geometric corners (`border-radius: 0px`).

---

## ⚡ 02 // Core Features & CRUD Capabilities

### 📂 Project Management (CRUD)
* **Create Project:** Register projects with custom code (`CH-XXX`), title, client/sponsor, sector category (`ENGINEERING`, `INFRASTRUCTURE`, `ENERGY`, `LOGISTICS`, etc.), priority (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), budget (CHF), start/due dates, and technical scope brief.
* **Read / Filter / Search:** Instant real-time search across codes, names, clients, and descriptions. Status filter pills (`ALL`, `PLANNING`, `IN PROGRESS`, `REVIEW`, `COMPLETED`).
* **Update Project:** Full modal editor to modify budgets, dates, descriptions, or pipeline status.
* **Delete Project:** Permanent deletion with cascading task cleanup and confirmation safeguards.

### 📋 Task Dispatch & 4-Stage Linear Kanban Board (CRUD)
* **Create Task:** Attach tasks to any project with title, lead assignee, priority, estimated hours, and due date.
* **Kanban Workflow:** Four discrete linear states:
  1. `01. TO DO`
  2. `02. IN PROGRESS`
  3. `03. AUDIT & REVIEW`
  4. `04. DELIVERED / DONE`
* **Status Transitions:** Instant single-click forward/backward status shifting (`←` / `→`).
* **Update / Delete Task:** Edit task specifications or delete completed items.

### 📊 Real-Time Metrics Strip
* **Total Project Registry:** Count of all registered projects and total committed capital (`CHF`).
* **Active Pipeline:** Ongoing projects in execution or audit.
* **Delivered Tasks:** Verified completed tasks across the workspace.
* **Completion Throughput:** Real-time percentage efficiency calculation.

### 🇨🇭 Instant Demonstration Seeding
* Single-click **"SEED DEMO DATA"** button preloads realistic Swiss civil engineering and technology projects:
  * *Zurich HB Transit Information Architecture (SBB CFF FFS)*
  * *Basel Clean Energy Microgrid Telemetry (IWB Basel)*
  * *Helvetia Alpine Search & Rescue Telematics (REGA)*
  * *Geneva Canton Municipal Waste Optimization (Ville de Genève)*

---

## 🐳 03 // Running with Docker (Recommended)

### Prerequisites
* Docker Engine / Docker Desktop installed

### Step 1: Start Container with Docker Compose
```bash
# Navigate to the project directory
cd project_management_system

# Build and start in detached mode
docker compose up --build -d
```

### Step 2: Access Application
Open your browser and navigate to:
```
http://localhost:8000
```

### Stop Containers
```bash
docker compose down
```

> **Data Persistence:** SQLite data is persisted across container restarts via the mounted volume `./data:/app/data`.

---

## 💻 04 // Running Locally (Without Docker)

You can also run the system directly on your machine with Python:

```bash
cd project_management_system

# 1. Install dependencies (Starlette, Uvicorn, Pydantic)
pip install -r requirements.txt

# 2. Start the application
python run.py
```

Then visit `http://localhost:8000` in your browser.

---

## 🧪 05 // Running the Test Suite

The project includes an automated test script validating database migrations, CRUD query logic, and cascade integrity:

```bash
python test_app.py
```

---

## 🔌 06 // REST API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the Swiss Single Page Application |
| `GET` | `/api/health` | System health probe (used by Docker HEALTHCHECK) |
| `GET` | `/api/stats` | Global throughput, active projects, and budget metrics |
| `POST` | `/api/seed` | Reset and seed authentic Swiss demonstration dataset |
| `GET` | `/api/projects` | Query projects (`?status=...&priority=...&search=...`) |
| `POST` | `/api/projects` | Create a new project |
| `GET` | `/api/projects/{id}` | Retrieve project details and nested task collection |
| `PUT` | `/api/projects/{id}` | Update existing project attributes |
| `DELETE`| `/api/projects/{id}` | Delete project and cascade associated tasks |
| `GET` | `/api/tasks` | Query tasks (`?project_id=...&status=...`) |
| `POST` | `/api/tasks` | Create a new task attached to a project |
| `GET` | `/api/tasks/{id}` | Get individual task by ID |
| `PUT` | `/api/tasks/{id}` | Update task details |
| `PATCH`| `/api/tasks/{id}/status`| Quick transition task status (`TODO`, `IN_PROGRESS`, `REVIEW`, `DONE`) |
| `DELETE`| `/api/tasks/{id}` | Delete task |

---

## 📁 07 // Repository Architecture

```
project_management_system/
├── Dockerfile                  # Lightweight Python 3.12-slim non-root container with healthcheck
├── docker-compose.yml          # Container orchestration with volume persistence on port 8000
├── .dockerignore               # Clean build context exclusion list
├── requirements.txt            # Python dependencies (starlette, uvicorn, pydantic)
├── run.py                      # Local development launcher
├── test_app.py                 # Automated CRUD and schema verification suite
├── README.md                   # Complete architectural guide
├── app/
│   ├── __init__.py
│   ├── main.py                 # ASGI application, API routes, and static file serving
│   ├── database.py             # SQLite schema initialization and connection management
│   ├── crud.py                 # Pure CRUD operations for Projects and Tasks
│   └── seed_data.py            # Swiss infrastructure sample dataset
├── static/
│   ├── css/
│   │   └── swiss.css           # Authentic Swiss International Style typography, grid, and palette
│   ├── js/
│   │   └── app.js              # Reactive state management, DOM renderer, and API client
│   └── index.html              # Modernist semantic HTML layout with live Zurich clock
└── data/                       # Persistent SQLite database storage (projects.db)
```
