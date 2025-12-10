# app/tests/test_engine.py
"""
Basic tests for engine behavior. Requires pytest.
Run: pytest -q
"""

import asyncio
from app.engine import engine
from app.workflows import create_code_review_graph
from app.storage import RUNS

def test_create_graph_and_run_sync():
    g = create_code_review_graph()
    graph_id = engine.create_graph(g)
    initial_state = {
        "code": "def hello():\n    print('hi')\n\ndef add(x,y):\n    if x>0:\n        return x+y\n",
        "threshold": 7
    }
    # run the graph in event loop
    run_id = asyncio.get_event_loop().run_until_complete(engine.run_graph(graph_id, initial_state))
    assert run_id in RUNS
    r = RUNS[run_id]
    assert "state" in r
    assert r["status"] in ("finished", "stopped", "error")
    # extracted functions should be present
    assert "functions" in r["state"]
