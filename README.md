# TaskFlow API

TaskFlow API is a small production-style FastAPI backend used to exercise AI pull request review quality. It models task creation, filtering, search, and background summary logic with a layered architecture. Task text fields are trimmed at the API boundary and reject whitespace-only values.

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
```

Run the API locally:

```powershell
uvicorn app.main:app --reload
```

Create a token:

```powershell
curl -X POST http://127.0.0.1:8000/api/v1/auth/token `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"alice@example.com\",\"password\":\"correct-horse\"}"
```

Use the returned bearer token with `/api/v1/tasks`.

## Quality Checks

```powershell
ruff check .
black --check .
mypy app tests
python -m pytest
```
