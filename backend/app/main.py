import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routers import chat, tasks, emails, expenses, documents, meetings, reports, dashboard

STATIC_DIR = Path(__file__).parent.parent / "static"


@asynccontextmanager
async def lifespan(application: FastAPI):
    await init_db()
    yield


app = FastAPI(title="AI Admin Agent", lifespan=lifespan)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(chat.router)
app.include_router(tasks.router)
app.include_router(emails.router)
app.include_router(expenses.router)
app.include_router(documents.router)
app.include_router(meetings.router)
app.include_router(reports.router)
app.include_router(dashboard.router)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


# Serve frontend static files
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="static-assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        file_path = (STATIC_DIR / full_path).resolve()
        if full_path and file_path.is_relative_to(STATIC_DIR.resolve()) and file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(STATIC_DIR / "index.html"))
