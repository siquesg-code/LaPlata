# Testing AI Admin Agent

## Overview
The AI Admin Agent is a fullstack app with a FastAPI backend and React+TypeScript frontend. The backend uses SQLAlchemy with SQLite (in-memory by default, file-based with `app.db`). No API keys are required for the rules-based agent mode.

## Local Development Setup

### Backend
```bash
cd backend
poetry install
rm -f app.db  # fresh database
poetry run fastapi dev app/main.py --port 8000
```
Backend runs on http://localhost:8000. API docs at http://localhost:8000/docs.

### Frontend (dev mode)
```bash
cd frontend
npm install
# Set VITE_API_URL=http://localhost:8000 in .env for dev mode
npm run dev
```
Frontend runs on http://localhost:5173.

### Combined mode (backend serves frontend)
```bash
cd frontend
echo 'VITE_API_URL=' > .env  # empty for same-origin
npm run build
cp -r dist ../backend/static
cd ../backend
poetry run fastapi dev app/main.py --port 8000
```
Both frontend and API served from http://localhost:8000.

## Key API Endpoints
- `GET /healthz` - Health check
- `POST /api/chat` - Send chat message `{"message": "..."}`
- `GET /api/chat/history` - Get chat history
- `DELETE /api/chat/history` - Clear chat history
- `GET /api/tasks` - List tasks
- `POST /api/tasks` - Create task
- `PATCH /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `GET /api/expenses` - List expenses
- `GET /api/expenses/summary` - Expense summary by category
- `GET /api/emails` - List emails
- `GET /api/meetings` - List meetings
- `GET /api/reports` - List reports
- `GET /api/dashboard` - Dashboard stats

## Chat Commands (Rules-Based Agent)
The agent uses keyword matching in `backend/app/agent.py` (`_process_with_rules`). Supported commands:
- **Create task**: "create task ...", "add task ...", "new task ..."
- **List tasks**: "list tasks", "show tasks", "my tasks"
- **Complete task**: "complete task 1", "mark done 1"
- **Add expense**: "expense $200 for software", "add expense ..."
- **Draft email**: "draft email to user@example.com about ..."
- **Schedule meeting**: "schedule meeting tomorrow"
- **Dashboard**: "show dashboard", "overview", "stats"
- **Generate report**: "report" (but see known issue below)
- **Help**: "help", "what can you do"

## Known Issues
- **Keyword matching order bug**: The rules-based parser checks keywords in order. Messages containing both "expense" and "report" (e.g., "generate expense report") will match the expense handler instead of the report handler, since "expense" is checked first. Workaround: use "generate report" without "expense" in the same message.
- **Meeting title extraction**: The meeting title extraction may capture unexpected text after the keyword. For example, "schedule meeting tomorrow" creates a meeting titled "Tomorrow" instead of something more descriptive.

## Testing Checklist
1. Health check: `GET /healthz` returns `{"status": "ok"}`
2. Chat: create task, expense, meeting, email via chat API
3. CRUD: verify entities appear in their respective list endpoints
4. Dashboard: verify counts reflect created data
5. Update/Delete: modify and remove entities
6. Chat history: verify persistence and clearing
7. Frontend: verify static files served correctly from backend (if using combined mode)

## Devin Secrets Needed
None required for rules-based mode. For OpenAI function-calling mode, set `OPENAI_API_KEY` environment variable.
