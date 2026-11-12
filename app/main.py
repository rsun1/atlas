from fastapi import FastAPI, HTTPException
from atlas.app.orchestrator import ORCHESTRATOR
from atlas.app.models import CreateTaskRequest, TaskStatus
from atlas.app import audit, memory
import asyncio
import json 
from fastapi.responses import StreamingResponse


app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "healthy"}

@app.post("/api/tasks")
async def create_task(req: CreateTaskRequest):
    task = ORCHESTRATOR.create_task(req.goal, req.auto_approve)
    return task.model_dump()

@app.get("/api/tasks/{task_id}")
def get_task(task_id: str):
    task = ORCHESTRATOR.get(task_id)
    if task is None:
        raise HTTPException(status_code=404,detail="task id not found or task does not exist")
    return task.model_dump()

@app.post("/api/tasks/{task_id}/approval")
def approval(task_id: str, approved: bool):
    ok = ORCHESTRATOR.resolve_approval(task_id, approved)
    if not ok: 
        raise HTTPException(status_code=404, detail="Cannot find task to be approved")
    return {"ok": True}

@app.get("/api/audit")
def get_audit(limit:int=200):
    return audit.tail(limit)

@app.get("/api/memory")
def get_memory(limit: int=5):
    return memory.episodic_recall(limit)

@app.get("/api/tasks/{task_id}/events")
async def task_events(task_id: str):
    task = ORCHESTRATOR.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    async def event_generator():
        q = ORCHESTRATOR.subscribe(task_id)
        try:
            snapshot = {"type":"snapshot", "data": task.model_dump()}
            yield f"data: {json.dumps(snapshot)}\n\n"
            
            while True:
                if task.status == TaskStatus.COMPLETED or task.status ==TaskStatus.FAILED:
                    break
                try:
                    event = await asyncio.wait_for(q.get(),timeout=25)
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            ORCHESTRATOR.unsubscribe(task_id,q)
    return StreamingResponse(event_generator(), media_type="text/event-stream")