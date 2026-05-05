# Backend - Code Review / Tech Debt Governance Agent MVP

## Run

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Open API docs:

```text
http://localhost:8000/docs
```

## What this backend includes

- FastAPI REST API
- SQLite database
- Background task queue
- Multi-agent orchestration
- Static code scanning
- Code review report generation
- Feishu webhook notification placeholder

## Main APIs

- `POST /tasks` create a review task
- `POST /tasks/{task_id}/run` enqueue and run task
- `GET /tasks` list tasks
- `GET /tasks/{task_id}` task detail
- `GET /tasks/{task_id}/report` report detail
