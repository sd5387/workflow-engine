# app/main.py
from fastapi import FastAPI, BackgroundTasks, WebSocket
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid

from app.models import GraphDef, CreateGraphResponse, RunRequest, RunStatus
from app.storage import RUNS
from app.engine import engine
from app.workflows import create_code_review_graph

app = FastAPI(title="Minimal Workflow Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/graph/create", response_model=CreateGraphResponse)
async def create_graph_endpoint(g: GraphDef):
    graph_id = engine.create_graph(g)
    return CreateGraphResponse(graph_id=graph_id)

@app.post("/graph/create_example", response_model=CreateGraphResponse)
async def create_example_graph():
    g = create_code_review_graph()
    graph_id = engine.create_graph(g)
    return CreateGraphResponse(graph_id=graph_id)

@app.post("/graph/run")
async def run_graph_endpoint(req: RunRequest, background_tasks: BackgroundTasks):
    run_id = str(uuid.uuid4())
    # schedule run in background and return run_id immediately
    RUNS[run_id] = {"state": req.initial_state.copy(), "status": "scheduled", "logs": []}

    async def _run():
        await engine.run_graph(req.graph_id, req.initial_state, run_id=run_id)

    background_tasks.add_task(_run)
    return JSONResponse({"run_id": run_id})

@app.get("/graph/state/{run_id}", response_model=RunStatus)
async def get_run_state(run_id: str):
    r = RUNS.get(run_id)
    if not r:
        return JSONResponse(status_code=404, content={"error": "run not found"})
    return RunStatus(run_id=run_id, status=r.get("status", "unknown"), state=r.get("state", {}), logs=r.get("logs", []))

@app.websocket("/graph/ws/{run_id}")
async def ws_run_logs(websocket: WebSocket, run_id: str):
    await websocket.accept()
    r = RUNS.get(run_id)
    if not r:
        await websocket.send_text("run not found")
        await websocket.close()
        return
    # stream current logs
    for l in r.get("logs", []):
        await websocket.send_text(l)
    # Keep connection open; in this simple implementation we do not push future logs
    try:
        while True:
            await websocket.receive_text()  # simple keep-alive echo style (blocks until client sends)
    except Exception:
        await websocket.close()
