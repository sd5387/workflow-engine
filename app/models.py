# app/models.py
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class NodeDef(BaseModel):
    name: str
    action: str  # name of the tool function in the registry
    condition: Optional[str] = None  # optional Python expression using `state`
    next: Optional[str] = None  # next node name if no condition


class GraphDef(BaseModel):
    name: str
    nodes: List[NodeDef]


class CreateGraphResponse(BaseModel):
    graph_id: str


class RunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any] = {}


class RunStatus(BaseModel):
    run_id: str
    status: str
    state: Dict[str, Any]
    logs: List[str]
