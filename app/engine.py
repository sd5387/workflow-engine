# app/engine.py
import asyncio
import uuid
import time
from typing import Optional, Dict, Any
from app.models import GraphDef, NodeDef
from app.storage import GRAPHS, RUNS
from app.tools import TOOL_REGISTRY

class Engine:
    def __init__(self):
        self.graphs = GRAPHS
        self.runs = RUNS

    def create_graph(self, graph_def: GraphDef) -> str:
        graph_id = str(uuid.uuid4())
        # store as dict to keep it JSON-serializable
        self.graphs[graph_id] = graph_def.dict()
        return graph_id

    async def run_graph(self, graph_id: str, initial_state: Dict[str, Any], run_id: Optional[str] = None, websocket=None) -> str:
        if run_id is None:
            run_id = str(uuid.uuid4())
        self.runs[run_id] = {
            "state": dict(initial_state),
            "status": "running",
            "logs": [],
            "start_time": time.time(),
            "current_node": None,
        }
        run_entry = self.runs[run_id]

        graph_dict = self.graphs.get(graph_id)
        if not graph_dict:
            run_entry["status"] = "error"
            run_entry["logs"].append("Graph not found")
            return run_id

        # reconstruct NodeDef list for convenience
        nodes = [NodeDef(**n) for n in graph_dict.get("nodes", [])]
        node_map = {n.name: n for n in nodes}
        current_node = nodes[0].name if nodes else None

        iter_guard = 0
        MAX_ITER = 500

        while current_node is not None and iter_guard < MAX_ITER:
            iter_guard += 1
            node_def = node_map.get(current_node)
            if not node_def:
                run_entry["logs"].append(f"Node {current_node} not found; stopping")
                break

            run_entry["current_node"] = current_node
            log_line = f"Running node: {current_node}"
            run_entry["logs"].append(log_line)
            if websocket:
                await websocket.send_text(log_line)

            action_fn = TOOL_REGISTRY.get(node_def.action)
            if action_fn is None:
                run_entry["logs"].append(f"Action {node_def.action} not registered")
                run_entry["status"] = "error"
                break

            try:
                result = action_fn(run_entry["state"])
                if asyncio.iscoroutine(result):
                    result = await result
                run_entry["logs"].append(f"Result: {result}")
            except Exception as e:
                run_entry["logs"].append(f"Error executing {node_def.action}: {e}")
                run_entry["status"] = "error"
                break

            # branching: evaluate condition if present
            next_node = None
            if node_def.condition:
                try:
                    # restricted eval: only `state` allowed in locals, no builtins
                    cond = node_def.condition
                    eval_result = eval(cond, {"__builtins__": {}}, {"state": run_entry["state"]})
                    if isinstance(eval_result, str) and eval_result in node_map:
                        next_node = eval_result
                    elif isinstance(eval_result, bool):
                        # if condition is boolean, if True use node_def.next else end/None
                        if eval_result and node_def.next:
                            next_node = node_def.next
                        else:
                            next_node = None
                    else:
                        next_node = None
                except Exception as e:
                    run_entry["logs"].append(f"Condition eval error for node {current_node}: {e}")
                    next_node = None
            else:
                next_node = node_def.next

            # dynamic goto: a tool can set state["_goto"] to jump to another node
            if run_entry["state"].get("_goto"):
                candidate = run_entry["state"].pop("_goto")
                if candidate in node_map:
                    next_node = candidate

            run_entry["logs"].append(f"Next node: {next_node}")
            run_entry["state"]["_last_node"] = current_node

            if next_node is None:
                run_entry["status"] = "finished"
                break
            else:
                current_node = next_node

        if iter_guard >= MAX_ITER:
            run_entry["status"] = "stopped"
            run_entry["logs"].append("Max iterations reached (possible infinite loop).")
        elif run_entry.get("status") != "error":
            run_entry["status"] = run_entry.get("status", "finished")

        run_entry["end_time"] = time.time()
        return run_id

# single engine instance to import in main
engine = Engine()
