import os
import sqlite3
from typing import Optional

DB_DIR = os.getenv("DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data"))
DB_PATH = os.getenv("DATABASE_URL", os.path.join(DB_DIR, "projects.db"))

def get_db():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        client TEXT DEFAULT '',
        category TEXT DEFAULT 'ENGINEERING',
        description TEXT DEFAULT '',
        status TEXT NOT NULL DEFAULT 'PLANNING', -- PLANNING, IN_PROGRESS, REVIEW, COMPLETED, ARCHIVED
        priority TEXT NOT NULL DEFAULT 'MEDIUM', -- LOW, MEDIUM, HIGH, CRITICAL
        budget REAL DEFAULT 0.0,
        start_date TEXT,
        due_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        assignee TEXT DEFAULT 'UNASSIGNED',
        status TEXT NOT NULL DEFAULT 'TODO', -- TODO, IN_PROGRESS, REVIEW, DONE
        priority TEXT NOT NULL DEFAULT 'MEDIUM', -- LOW, MEDIUM, HIGH, CRITICAL
        estimated_hours REAL DEFAULT 0.0,
        due_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);")

    conn.commit()
    conn.close()
