# AI Admin Agent

An AI-powered business administration assistant with a chat interface for automating common business processes.

## Features

- **AI Chat** - Natural language interface to manage your business operations
- **Task Management** - Create, track, and update tasks with priorities and statuses
- **Email Drafting** - Compose and manage professional email drafts
- **Expense Tracking** - Log and categorize expenses with summaries
- **Meeting Scheduling** - Schedule and manage meetings
- **Document Management** - Store, organize, and summarize documents
- **Report Generation** - Generate and view business reports
- **Dashboard** - Overview of all business operations with charts

## Tech Stack

### Backend
- **FastAPI** - Python async web framework
- **SQLAlchemy** - Async ORM with SQLite (aiosqlite)
- **Pydantic** - Data validation and schemas

### Frontend
- **React + TypeScript** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Utility-first CSS
- **shadcn/ui** - Pre-built UI components
- **Recharts** - Charts and data visualization
- **Lucide React** - Icons

## Getting Started

### Backend

```bash
cd backend
poetry install
poetry run fastapi dev app/main.py
```

Backend runs on http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:5173

### Environment Variables

Create `frontend/.env`:
```
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
backend/
  app/
    main.py          # FastAPI entry point
    database.py      # Database configuration
    models.py        # SQLAlchemy models
    schemas.py       # Pydantic schemas
    agent.py         # AI agent logic with tools
    routers/         # API route handlers
      chat.py
      tasks.py
      emails.py
      expenses.py
      documents.py
      meetings.py
      reports.py
      dashboard.py

frontend/
  src/
    api.ts           # API client
    App.tsx          # Main app component
    components/
      Layout.tsx     # Navigation layout
      ChatPage.tsx   # AI chat interface
      DashboardPage.tsx
      TasksPage.tsx
      EmailsPage.tsx
      ExpensesPage.tsx
      MeetingsPage.tsx
      DocumentsPage.tsx
      ReportsPage.tsx
```
