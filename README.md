A clean, modular, FastAPI-based workflow/agent engine inspired by LangGraph principles.
Designed to demonstrate core backend fundamentals: Python structure, async execution, API design, state transitions, tools, branching, and looping.

⭐ Features

🧩 Nodes → Python functions executed step-by-step

🔁 Loops → continue execution until conditions are met

🔀 Branching → dynamic routing based on state

🧰 Tool Registry → plug-in functions for workflow steps

📦 Shared State → dictionary flowing through all nodes

🚀 Async Execution → using FastAPI BackgroundTasks

📡 WebSocket Logs (optional bonus)

🧪 Unit Tests → simple example test included

📂 Clean Project Structure → interview-ready
workflow-engine/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── tools.py
│   ├── storage.py
│   ├── engine.py
│   ├── workflows.py
│   ├── main.py
│   └── tests/
│       └── test_engine.py
│
├── README.md
├── requirements.txt
└── .gitignore

Example Workflow Implemented (Option A)
✔ Code Review Mini-Agent

Extract functions

Check complexity

Detect code issues

Suggest improvements

Loop until quality_score >= threshold

All steps are rule-based, as required.

Setup Instructions

1. Clone the Repo
git clone https://github.com/<your-username>/workflow-engine.git
cd workflow-engine

2. Create Virtual Environment
python -m venv .venv
.\.venv\Scripts\activate     # Windows
# OR
source .venv/bin/activate   # macOS/Linux

3. Install Dependencies
pip install -r requirements.txt

4. Run the Server
   uvicorn app.main:app --reload

Server starts at:
http://127.0.0.1:8000
API Endpoints
🔹 Create Graph
POST /graph/create

🔹 Create Example Graph
POST /graph/create_example

🔹 Run Workflow
POST /graph/run

🔹 Get Run State
GET /graph/state/{run_id}

🔹 WebSocket Logs (optional)
ws://127.0.0.1:8000/graph/ws/{run_id}
What I Would Improve With More Time

Add persistent storage (SQLite/Postgres)

Better sandbox for condition evaluation (replace eval)

Add retry mechanism for failed nodes

Add Node execution time metrics

Build a small UI in React or Streamlit

📄 License

MIT License
