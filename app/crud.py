from typing import List, Dict, Any, Optional
import sqlite3
from app.database import get_db

# ==================== PROJECTS CRUD ====================

def list_projects(status: Optional[str] = None, priority: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        p.*,
        COUNT(t.id) as total_tasks,
        SUM(CASE WHEN t.status = 'DONE' THEN 1 ELSE 0 END) as completed_tasks
    FROM projects p
    LEFT JOIN tasks t ON p.id = t.project_id
    WHERE 1=1
    """
    params = []
    
    if status and status.upper() != "ALL":
        query += " AND p.status = ?"
        params.append(status.upper())
        
    if priority and priority.upper() != "ALL":
        query += " AND p.priority = ?"
        params.append(priority.upper())
        
    if search:
        query += " AND (p.name LIKE ? OR p.code LIKE ? OR p.client LIKE ? OR p.description LIKE ?)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard, wildcard])
        
    query += " GROUP BY p.id ORDER BY p.updated_at DESC, p.id DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        d = dict(r)
        total = d.get("total_tasks") or 0
        done = d.get("completed_tasks") or 0
        d["progress_pct"] = round((done / total * 100), 1) if total > 0 else 0.0
        results.append(d)
    return results

def get_project(project_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT 
        p.*,
        COUNT(t.id) as total_tasks,
        SUM(CASE WHEN t.status = 'DONE' THEN 1 ELSE 0 END) as completed_tasks
    FROM projects p
    LEFT JOIN tasks t ON p.id = t.project_id
    WHERE p.id = ?
    GROUP BY p.id
    """, (project_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    d = dict(row)
    total = d.get("total_tasks") or 0
    done = d.get("completed_tasks") or 0
    d["progress_pct"] = round((done / total * 100), 1) if total > 0 else 0.0
    return d

def create_project(data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    
    code = (data.get("code") or "").strip().upper()
    name = (data.get("name") or "").strip()
    client = (data.get("client") or "").strip()
    category = (data.get("category") or "ENGINEERING").strip().upper()
    description = (data.get("description") or "").strip()
    status = (data.get("status") or "PLANNING").strip().upper()
    priority = (data.get("priority") or "MEDIUM").strip().upper()
    budget = float(data.get("budget") or 0.0)
    start_date = data.get("start_date") or None
    due_date = data.get("due_date") or None
    
    if not code:
        # Generate auto-code
        cursor.execute("SELECT COUNT(*) FROM projects")
        next_num = cursor.fetchone()[0] + 1
        code = f"PRJ-{next_num:03d}"
        
    cursor.execute("""
    INSERT INTO projects (code, name, client, category, description, status, priority, budget, start_date, due_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (code, name, client, category, description, status, priority, budget, start_date, due_date))
    
    project_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_project(project_id)

def update_project(project_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    
    fields = []
    values = []
    
    allowed = ["code", "name", "client", "category", "description", "status", "priority", "budget", "start_date", "due_date"]
    for k in allowed:
        if k in data:
            val = data[k]
            if k in ["code", "category", "status", "priority"] and isinstance(val, str):
                val = val.strip().upper()
            elif k == "budget":
                val = float(val or 0.0)
            fields.append(f"{k} = ?")
            values.append(val)
            
    if not fields:
        conn.close()
        return get_project(project_id)
        
    fields.append("updated_at = CURRENT_TIMESTAMP")
    values.append(project_id)
    
    sql = f"UPDATE projects SET {', '.join(fields)} WHERE id = ?"
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
    return get_project(project_id)

def delete_project(project_id: int) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

# ==================== TASKS CRUD ====================

def list_tasks(project_id: Optional[int] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT t.*, p.name as project_name, p.code as project_code FROM tasks t JOIN projects p ON t.project_id = p.id WHERE 1=1"
    params = []
    
    if project_id:
        query += " AND t.project_id = ?"
        params.append(project_id)
        
    if status and status.upper() != "ALL":
        query += " AND t.status = ?"
        params.append(status.upper())
        
    query += " ORDER BY t.id ASC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_task(task_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT t.*, p.name as project_name, p.code as project_code 
    FROM tasks t 
    JOIN projects p ON t.project_id = p.id 
    WHERE t.id = ?
    """, (task_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_task(data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    
    project_id = int(data["project_id"])
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    assignee = (data.get("assignee") or "UNASSIGNED").strip().upper()
    status = (data.get("status") or "TODO").strip().upper()
    priority = (data.get("priority") or "MEDIUM").strip().upper()
    estimated_hours = float(data.get("estimated_hours") or 0.0)
    due_date = data.get("due_date") or None
    
    cursor.execute("""
    INSERT INTO tasks (project_id, title, description, assignee, status, priority, estimated_hours, due_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (project_id, title, description, assignee, status, priority, estimated_hours, due_date))
    
    task_id = cursor.lastrowid
    # Bump project updated_at
    cursor.execute("UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (project_id,))
    
    conn.commit()
    conn.close()
    return get_task(task_id)

def update_task(task_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    
    fields = []
    values = []
    
    allowed = ["title", "description", "assignee", "status", "priority", "estimated_hours", "due_date", "project_id"]
    for k in allowed:
        if k in data:
            val = data[k]
            if k in ["assignee", "status", "priority"] and isinstance(val, str):
                val = val.strip().upper()
            elif k == "estimated_hours":
                val = float(val or 0.0)
            elif k == "project_id":
                val = int(val)
            fields.append(f"{k} = ?")
            values.append(val)
            
    if not fields:
        conn.close()
        return get_task(task_id)
        
    fields.append("updated_at = CURRENT_TIMESTAMP")
    values.append(task_id)
    
    sql = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
    cursor.execute(sql, values)
    
    # Touch project updated_at
    cursor.execute("UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = (SELECT project_id FROM tasks WHERE id = ?)", (task_id,))
    
    conn.commit()
    conn.close()
    return get_task(task_id)

def delete_task(task_id: int) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT project_id FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    project_id = row[0] if row else None
    
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    deleted = cursor.rowcount > 0
    
    if project_id:
        cursor.execute("UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (project_id,))
        
    conn.commit()
    conn.close()
    return deleted

# ==================== GLOBAL STATS ====================

def get_stats() -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM projects")
    total_projects = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM projects WHERE status IN ('PLANNING', 'IN_PROGRESS', 'REVIEW')")
    active_projects = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM projects WHERE status = 'COMPLETED'")
    completed_projects = cursor.fetchone()[0]
    
    cursor.execute("SELECT COALESCE(SUM(budget), 0.0) FROM projects")
    total_budget = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'DONE'")
    completed_tasks = cursor.fetchone()[0]
    
    conn.close()
    
    task_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0.0
    
    return {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "total_budget": total_budget,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "task_completion_rate": task_rate
    }
