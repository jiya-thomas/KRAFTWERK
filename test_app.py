import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db
from app.seed_data import seed_database
import app.crud as crud

def run_tests():
    print(">>> 1. Initializing DB and seeding...")
    init_db()
    seed_database(force=True)
    
    print(">>> 2. Testing list_projects()...")
    projects = crud.list_projects()
    assert len(projects) == 4, f"Expected 4 initial projects, got {len(projects)}"
    print(f"    Loaded {len(projects)} projects.")
    
    print(">>> 3. Testing create_project()...")
    new_proj = crud.create_project({
        "code": "CH-TEST",
        "name": "Lucerne Hyperloop Sub-Station",
        "client": "CFF Infrastructure",
        "category": "INFRASTRUCTURE",
        "description": "Vacuum pneumatic capsule distribution network.",
        "status": "PLANNING",
        "priority": "HIGH",
        "budget": 520000.0,
        "start_date": "2027-01-01",
        "due_date": "2027-12-31"
    })
    assert new_proj["id"] is not None
    assert new_proj["code"] == "CH-TEST"
    proj_id = new_proj["id"]
    print(f"    Created project #{proj_id}: {new_proj['name']}")
    
    print(">>> 4. Testing update_project()...")
    updated = crud.update_project(proj_id, {"status": "IN_PROGRESS", "budget": 600000.0})
    assert updated["status"] == "IN_PROGRESS"
    assert updated["budget"] == 600000.0
    print(f"    Updated project #{proj_id} status to {updated['status']}")
    
    print(">>> 5. Testing create_task()...")
    task = crud.create_task({
        "project_id": proj_id,
        "title": "Acoustic dampening finite element analysis",
        "assignee": "DR. V. KELLER",
        "status": "TODO",
        "priority": "CRITICAL",
        "estimated_hours": 36.0,
        "due_date": "2027-02-15"
    })
    assert task["id"] is not None
    task_id = task["id"]
    print(f"    Created task #{task_id} for project #{proj_id}")
    
    print(">>> 6. Testing update_task() status move...")
    task_updated = crud.update_task(task_id, {"status": "IN_PROGRESS"})
    assert task_updated["status"] == "IN_PROGRESS"
    print(f"    Task #{task_id} status moved to {task_updated['status']}")
    
    print(">>> 7. Testing stats calculation...")
    stats = crud.get_stats()
    assert stats["total_projects"] == 5
    assert stats["active_projects"] >= 1
    print(f"    Stats verified: {stats}")
    
    print(">>> 8. Testing delete_task()...")
    del_task_ok = crud.delete_task(task_id)
    assert del_task_ok is True
    assert crud.get_task(task_id) is None
    print(f"    Deleted task #{task_id}")
    
    print(">>> 9. Testing delete_project()...")
    del_proj_ok = crud.delete_project(proj_id)
    assert del_proj_ok is True
    assert crud.get_project(proj_id) is None
    print(f"    Deleted project #{proj_id}")
    
    print("\nALL BACKEND CRUD AND DATA TESTS PASSED SUCCESSFULLY! (9/9)")

if __name__ == "__main__":
    run_tests()
