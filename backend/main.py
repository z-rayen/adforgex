"""
backend/main.py — FastAPI application entry point

Startup:
  - Initializes ChromaDB RAG engine
  - Creates pipeline instance
  - Mounts static frontend
  - Registers all routers

Run:
  uvicorn backend.main:app --reload --port 8000
"""
"""
backend/main.py — FastAPI application entry point
...
"""
import sys
import asyncio

# Windows fix: Playwright needs SelectorEventLoop, not ProactorEventLoop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.config import get_settings
from backend.models import HealthResponse
from backend.pipeline import AdGenerationPipeline
from backend.routers.pipeline_router import router as pipeline_router
from backend.routers.rag_router import router as rag_router
from backend.routers.auth_router import router as auth_router
from backend.database import init_db
from rag.rag_engine import RAGEngine

# ─────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("adforge")

settings = get_settings()


# ─────────────────────────────────────────────────
# Startup / Shutdown
# ─────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AdForge starting up...")

    # Initialize SQLite database (users + history)
    init_db()
    logger.info("SQLite DB initialized")

    # Initialize RAG engine
    rag_engine = RAGEngine(
        db_path=settings.chroma_db_path,
        embedding_model=settings.embedding_model,
    )
    try:
        rag_engine.initialize()
        doc_count = rag_engine.count()
        if doc_count == 0:
            logger.warning(
                "RAG knowledge base is empty! Run: python rag/seed_data.py"
            )
        else:
            logger.info(f"RAG ready with {doc_count} documents")
    except Exception as e:
        logger.error(f"RAG initialization failed: {e}")
        rag_engine = None

    # Create pipeline
    pipeline = AdGenerationPipeline(rag_engine=rag_engine)

    # Store on app state
    app.state.rag_engine = rag_engine
    app.state.pipeline = pipeline

    logger.info(f"AdForge ready at http://{settings.host}:{settings.port}")
    yield

    logger.info("AdForge shutting down...")


# ─────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────

app = FastAPI(
    title="AdForge AI",
    description="6-step AI-powered ad generation pipeline with RAG and web scraping",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins for local dev; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(pipeline_router)
app.include_router(rag_router)


# ─────────────────────────────────────────────────
# Health & Root
# ─────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health(request: Request):
    rag = request.app.state.rag_engine
    return HealthResponse(
        status="ok",
        rag_ready=rag is not None and rag.count() > 0,
        groq_key_set=bool(settings.groq_api_key),
    )


@app.get("/", tags=["system"])
async def root():
    """Serve the frontend."""
    frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if frontend_path.exists():
        return FileResponse(str(frontend_path))
    return JSONResponse(
        {"message": "AdForge API running. See /docs for API reference."}
    )


@app.get("/docs-redirect")
async def docs():
    from fastapi.responses import RedirectResponse
    return RedirectResponse("/docs")


# Mount static files if frontend dir exists
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


# ─────────────────────────────────────────────────
# Error handlers
# ─────────────────────────────────────────────────

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"error": str(exc)})


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error on {request.url}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


# ─────────────────────────────────────────────────
# Dev runner
# ─────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info",
    )
