# app/tools.py
from typing import Callable, Dict, Any
import asyncio

TOOL_REGISTRY: Dict[str, Callable[[Dict], Any]] = {}

def register_tool(name: str):
    def decorator(fn):
        TOOL_REGISTRY[name] = fn
        return fn
    return decorator

# -----------------------
# Example tools (Option A)
# -----------------------

@register_tool("extract_functions")
async def extract_functions(state: Dict[str, Any]):
    """Naive extractor: lines starting with 'def ' are functions."""
    code = state.get("code", "")
    funcs = []
    for line in code.splitlines():
        s = line.strip()
        if s.startswith("def "):
            name = s.split("def ")[1].split("(")[0].strip()
            funcs.append(name)
    state["functions"] = funcs
    return {"functions": funcs}


@register_tool("check_complexity")
async def check_complexity(state: Dict[str, Any]):
    """
    Very simple proxy for cyclomatic complexity:
    base 1 + count(if/for/while/elif) in function body.
    """
    funcs = state.get("functions", [])
    code = state.get("code", "")
    complexity = {}
    current = None
    for line in code.splitlines():
        s = line.strip()
        if s.startswith("def "):
            current = s.split("def ")[1].split("(")[0].strip()
            complexity[current] = 1
        elif current:
            if any(tok in s for tok in ("if ", "for ", "while ", "elif ")):
                complexity[current] = complexity.get(current, 1) + 1
    state["complexity"] = complexity
    avg = sum(complexity.values()) / len(complexity) if complexity else 0
    # quality_score: arbitrary mapping (higher complexity → lower score)
    state["quality_score"] = max(0, round(10 - avg, 2))
    return {"complexity": complexity, "quality_score": state["quality_score"]}


@register_tool("detect_issues")
async def detect_issues(state: Dict[str, Any]):
    """Naive linting rules for demo."""
    code = state.get("code", "")
    issues = []
    if "print(" in code:
        issues.append("Contains print statements")
    if "# TODO" in code:
        issues.append("Has TODO comments")
    for i, line in enumerate(code.splitlines(), start=1):
        if len(line) > 120:
            issues.append(f"Line {i} > 120 chars")
    state["issues"] = issues
    # Penalize quality score by number of issues
    state["quality_score"] = max(0, state.get("quality_score", 10) - len(issues))
    return {"issues": issues, "quality_score": state["quality_score"]}


@register_tool("suggest_improvements")
async def suggest_improvements(state: Dict[str, Any]):
    """Create lightweight suggestions based on complexity & issues."""
    suggestions = []
    for f, c in state.get("complexity", {}).items():
        if c > 5:
            suggestions.append(f"Refactor {f} to reduce complexity ({c})")
    for issue in state.get("issues", []):
        suggestions.append(f"Fix: {issue}")
    state.setdefault("suggestions", []).extend(suggestions)
    # small improvement to quality for suggestions
    state["quality_score"] = min(10, state.get("quality_score", 0) + len(suggestions) * 0.5)
    return {"suggestions": suggestions, "quality_score": state["quality_score"]}
