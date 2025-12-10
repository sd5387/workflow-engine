# app/workflows.py
from app.models import GraphDef, NodeDef

def create_code_review_graph():
    """
    Option A: Code Review Mini-Agent
    Steps:
    - extract -> complexity -> issues -> suggest (loop until quality_score >= threshold)
    """
    nodes = [
        NodeDef(name="extract", action="extract_functions", next="complexity"),
        NodeDef(name="complexity", action="check_complexity", next="issues"),
        NodeDef(name="issues", action="detect_issues", next="suggest"),
        # suggest_improvements: condition checks whether quality_score >= threshold
        # condition is evaluated as Python expression using `state`. If True and next is None -> end.
        NodeDef(
            name="suggest",
            action="suggest_improvements",
            condition="state.get('quality_score', 0) >= state.get('threshold', 7)",
            next=None,
        ),
    ]
    g = GraphDef(name="code_review_mini_agent", nodes=nodes)
    return g
