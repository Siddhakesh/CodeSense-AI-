"""
Main FastAPI application entry point.
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from dotenv import load_dotenv


from contextlib import asynccontextmanager
from .api import ingest, analyze, chat, profile, auth
from .core.database import create_db_and_tables

# Load environment variables
load_dotenv(override=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    title="Explain Any Codebase",
    description="Backend API for analyzing and explaining GitHub repositories",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(ingest.router, prefix="/api", tags=["ingest"])
app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(profile.router, prefix="/api", tags=["profile"])


# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.get("/")
async def root():
    """Serve the frontend."""
    return FileResponse(static_path / "index.html")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "explain-any-codebase"}

@app.get("/login")
async def login_page():
    """Serve the login page."""
    return FileResponse(static_path / "login.html")
