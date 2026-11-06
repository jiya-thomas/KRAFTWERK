from app.database import get_db

SAMPLE_PROJECTS = [
    {
        "code": "CH-081",
        "name": "Zurich HB Transit Information Architecture",
        "client": "SBB CFF FFS (Swiss Federal Railways)",
        "category": "INFRASTRUCTURE",
        "description": "Redesigning passenger digital wayfinding, multi-modal timetable monitors, and responsive station navigation kiosks with high-contrast accessibility standards.",
        "status": "IN_PROGRESS",
        "priority": "HIGH",
        "budget": 145000.0,
        "start_date": "2026-09-01",
        "due_date": "2026-12-15",
        "tasks": [
            {"title": "Audit existing LCD terminal visual hierarchy", "assignee": "M. MUELLER", "status": "DONE", "priority": "HIGH", "estimated_hours": 16.0, "due_date": "2026-09-20"},
            {"title": "Implement Helvetica Neue metric grid typography", "assignee": "E. KELLER", "status": "DONE", "priority": "MEDIUM", "estimated_hours": 24.0, "due_date": "2026-10-05"},
            {"title": "Calibrate high-contrast daytime luminescence", "assignee": "A. GRAF", "status": "IN_PROGRESS", "priority": "HIGH", "estimated_hours": 32.0, "due_date": "2026-11-20"},
            {"title": "Finalize real-time S-Bahn latency telemetry API", "assignee": "S. WYSS", "status": "TODO", "priority": "CRITICAL", "estimated_hours": 40.0, "due_date": "2026-12-01"}
        ]
    },
    {
        "code": "CH-104",
        "name": "Basel Clean Energy Microgrid Telemetry",
        "client": "IWB Basel Utility Services",
        "category": "ENERGY",
        "description": "Smart telemetry collection pipeline connecting Rhine hydro-electric turbines with regional municipal battery energy storage systems.",
        "status": "PLANNING",
        "priority": "CRITICAL",
        "budget": 280000.0,
        "start_date": "2026-11-01",
        "due_date": "2027-03-30",
        "tasks": [
            {"title": "SCADA sensor protocol integration specification", "assignee": "D. BRUNNER", "status": "IN_PROGRESS", "priority": "CRITICAL", "estimated_hours": 36.0, "due_date": "2026-11-25"},
            {"title": "Security audit for Modbus/TCP edge relays", "assignee": "J. SCHMID", "status": "TODO", "priority": "HIGH", "estimated_hours": 28.0, "due_date": "2026-12-10"},
            {"title": "Edge buffer failover persistence test suite", "assignee": "L. FREI", "status": "TODO", "priority": "MEDIUM", "estimated_hours": 20.0, "due_date": "2026-12-22"}
        ]
    },
    {
        "code": "CH-119",
        "name": "Helvetia Alpine Search & Rescue Telematics",
        "client": "REGA Air Rescue Logistics",
        "category": "LOGISTICS",
        "description": "Low-power VHF and satellite telemetry tracking software for alpine medical rescue helicopters operating in high-altitude Valais corridors.",
        "status": "REVIEW",
        "priority": "CRITICAL",
        "budget": 195000.0,
        "start_date": "2026-08-15",
        "due_date": "2026-11-30",
        "tasks": [
            {"title": "Sub-zero telemetry ping resilience field trials", "assignee": "K. STEINER", "status": "DONE", "priority": "HIGH", "estimated_hours": 45.0, "due_date": "2026-10-15"},
            {"title": "Aeronautical map coordinate projection engine", "assignee": "R. MEIER", "status": "DONE", "priority": "MEDIUM", "estimated_hours": 38.0, "due_date": "2026-10-28"},
            {"title": "Federal Civil Aviation (FOCA) compliance certification", "assignee": "H. WEBER", "status": "REVIEW", "priority": "CRITICAL", "estimated_hours": 50.0, "due_date": "2026-11-25"}
        ]
    },
    {
        "code": "CH-202",
        "name": "Geneva Canton Municipal Waste Optimization",
        "client": "Ville de Genève",
        "category": "ENVIRONMENT",
        "description": "IoT bin sensor density mapping, dynamic route dispatching for electric refuse trucks, and carbon reduction reporting dashboard.",
        "status": "COMPLETED",
        "priority": "LOW",
        "budget": 85000.0,
        "start_date": "2026-04-01",
        "due_date": "2026-10-15",
        "tasks": [
            {"title": "Optical fullness sensor calibration in Carouge", "assignee": "C. FAVRE", "status": "DONE", "priority": "LOW", "estimated_hours": 18.0, "due_date": "2026-05-10"},
            {"title": "Fleet dynamic route dispatch microservice", "assignee": "G. BERTHOD", "status": "DONE", "priority": "MEDIUM", "estimated_hours": 40.0, "due_date": "2026-07-20"},
            {"title": "Cantonal sustainability report generation pipeline", "assignee": "N. ROCHAT", "status": "DONE", "priority": "LOW", "estimated_hours": 12.0, "due_date": "2026-09-30"}
        ]
    }
]

def seed_database(force: bool = False):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM projects")
    count = cursor.fetchone()[0]
    
    if count > 0 and not force:
        conn.close()
        return False
        
    if force:
        cursor.execute("DELETE FROM tasks")
        cursor.execute("DELETE FROM projects")
        
    for p in SAMPLE_PROJECTS:
        cursor.execute("""
        INSERT INTO projects (code, name, client, category, description, status, priority, budget, start_date, due_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p["code"],
            p["name"],
            p["client"],
            p["category"],
            p["description"],
            p["status"],
            p["priority"],
            p["budget"],
            p["start_date"],
            p["due_date"]
        ))
        proj_id = cursor.lastrowid
        
        for t in p.get("tasks", []):
            cursor.execute("""
            INSERT INTO tasks (project_id, title, description, assignee, status, priority, estimated_hours, due_date)
            VALUES (?, ?, '', ?, ?, ?, ?, ?)
            """, (
                proj_id,
                t["title"],
                t["assignee"],
                t["status"],
                t["priority"],
                t["estimated_hours"],
                t["due_date"]
            ))
            
    conn.commit()
    conn.close()
    return True
