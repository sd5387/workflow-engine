# app/storage.py
# Simple in-memory stores for graphs and runs.
# Note: this is ephemeral (cleared when process restarts).

GRAPHS = {}  # graph_id -> GraphDef (dict / pydantic-compatible)
RUNS = {}    # run_id -> {"state":..., "status":..., "logs":..., ...}
