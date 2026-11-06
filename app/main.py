import os
import json
from starlette.applications import Starlette
from starlette.responses import JSONResponse, FileResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app.database import init_db
from app.seed_data import seed_database
import app.crud as crud

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# ==================== CONTROLLERS ====================

async def index(request):
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

async def health(request):
    return JSONResponse({"status": "ok", "system": "KRAFTWERK Swiss PM System", "version": "1.0.0"})

async def get_system_stats(request):
    stats = crud.get_stats()
    return JSONResponse(stats)

async def handle_seed(request):
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    force = body.get("force", False)
    created = seed_database(force=force)
    return JSONResponse({"success": True, "seeded": created, "stats": crud.get_stats()})

# Projects
async def list_projects_endpoint(request):
    status = request.query_params.get("status")
    priority = request.query_params.get("priority")
    search = request.query_params.get("search")
    projects = crud.list_projects(status=status, priority=priority, search=search)
    return JSONResponse(projects)

async def create_project_endpoint(request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)
    
    if not data.get("name"):
        return JSONResponse({"error": "Project name is required"}, status_code=400)
        
    project = crud.create_project(data)
    return JSONResponse(project, status_code=201)

async def get_project_endpoint(request):
    project_id = int(request.path_params["id"])
    project = crud.get_project(project_id)
    if not project:
        return JSONResponse({"error": "Project not found"}, status_code=404)
    tasks = crud.list_tasks(project_id=project_id)
    project["tasks"] = tasks
    return JSONResponse(project)

async def update_project_endpoint(request):
    project_id = int(request.path_params["id"])
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)
        
    project = crud.update_project(project_id, data)
    if not project:
        return JSONResponse({"error": "Project not found"}, status_code=404)
    return JSONResponse(project)

async def delete_project_endpoint(request):
    project_id = int(request.path_params["id"])
    success = crud.delete_project(project_id)
    if not success:
        return JSONResponse({"error": "Project not found"}, status_code=404)
    return JSONResponse({"success": True, "deleted_id": project_id})

# Tasks
async def list_tasks_endpoint(request):
    proj_id = request.query_params.get("project_id")
    status = request.query_params.get("status")
    project_id = int(proj_id) if proj_id else None
    tasks = crud.list_tasks(project_id=project_id, status=status)
    return JSONResponse(tasks)

async def create_task_endpoint(request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)
        
    if not data.get("title") or not data.get("project_id"):
        return JSONResponse({"error": "Title and project_id are required"}, status_code=400)
        
    task = crud.create_task(data)
    return JSONResponse(task, status_code=201)

async def get_task_endpoint(request):
    task_id = int(request.path_params["id"])
    task = crud.get_task(task_id)
    if not task:
        return JSONResponse({"error": "Task not found"}, status_code=404)
    return JSONResponse(task)

async def update_task_endpoint(request):
    task_id = int(request.path_params["id"])
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)
        
    task = crud.update_task(task_id, data)
    if not task:
        return JSONResponse({"error": "Task not found"}, status_code=404)
    return JSONResponse(task)

async def patch_task_status_endpoint(request):
    task_id = int(request.path_params["id"])
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)
        
    status = data.get("status")
    if not status:
        return JSONResponse({"error": "Status required"}, status_code=400)
        
    task = crud.update_task(task_id, {"status": status})
    if not task:
        return JSONResponse({"error": "Task not found"}, status_code=404)
    return JSONResponse(task)

async def delete_task_endpoint(request):
    task_id = int(request.path_params["id"])
    success = crud.delete_task(task_id)
    if not success:
        return JSONResponse({"error": "Task not found"}, status_code=404)
    return JSONResponse({"success": True, "deleted_id": task_id})

# ==================== LIFECYCLE & ROUTES ====================
import contextlib

# Ensure DB and seed data exist immediately upon import
init_db()
seed_database(force=False)

@contextlib.asynccontextmanager
async def lifespan(app):
    init_db()
    seed_database(force=False)
    yield

routes = [
    Route("/", endpoint=index, methods=["GET"]),
    Route("/api/health", endpoint=health, methods=["GET"]),
    Route("/api/stats", endpoint=get_system_stats, methods=["GET"]),
    Route("/api/seed", endpoint=handle_seed, methods=["POST"]),
    
    # Projects CRUD
    Route("/api/projects", endpoint=list_projects_endpoint, methods=["GET"]),
    Route("/api/projects", endpoint=create_project_endpoint, methods=["POST"]),
    Route("/api/projects/{id:int}", endpoint=get_project_endpoint, methods=["GET"]),
    Route("/api/projects/{id:int}", endpoint=update_project_endpoint, methods=["PUT"]),
    Route("/api/projects/{id:int}", endpoint=delete_project_endpoint, methods=["DELETE"]),
    
    # Tasks CRUD
    Route("/api/tasks", endpoint=list_tasks_endpoint, methods=["GET"]),
    Route("/api/tasks", endpoint=create_task_endpoint, methods=["POST"]),
    Route("/api/tasks/{id:int}", endpoint=get_task_endpoint, methods=["GET"]),
    Route("/api/tasks/{id:int}", endpoint=update_task_endpoint, methods=["PUT"]),
    Route("/api/tasks/{id:int}/status", endpoint=patch_task_status_endpoint, methods=["PATCH"]),
    Route("/api/tasks/{id:int}", endpoint=delete_task_endpoint, methods=["DELETE"]),
    
    # Static files
    Mount("/static", app=StaticFiles(directory=STATIC_DIR), name="static")
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
]

app = Starlette(debug=True, routes=routes, middleware=middleware, lifespan=lifespan)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
