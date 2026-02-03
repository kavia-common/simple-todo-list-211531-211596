# simple-todo-list-211531-211596 (backend_fastapi)

FastAPI backend for a simple todo list.

## Features
- Create / read / update / delete tasks
- Mark task complete/incomplete
- SQLite by default; optional database URL via env var
- OpenAPI docs at `/docs` and `/openapi.json`

## Quickstart (dev)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment variables
- `DATABASE_URL` (optional): SQLAlchemy URL. Defaults to `sqlite:///./todo.db`.

## API
Base URL: `http://localhost:8000`

- `GET /health`
- `GET /tasks`
- `POST /tasks`
- `GET /tasks/{task_id}`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`

Also:
- `GET /docs/ws` (WebSocket usage note; this project has no WebSockets, but we provide a helpful page as required by template guidelines.)
